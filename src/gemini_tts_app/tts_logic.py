# src/gemini_tts_app/tts_logic.py
# Phiên bản: tts_logic_v39_rework_progress
import mimetypes
import os
import struct
import traceback
import base64
import time
import queue 
import threading

import google.generativeai as genai
from google.generativeai import types
from google.api_core import exceptions as core_exceptions
from pydub import AudioSegment
# Thêm dòng này để import các hằng số màu
from .constants import COLOR_OK, COLOR_WARN, COLOR_ERROR, COLOR_NORMAL
gemini_api_config_lock = threading.Lock()

def save_binary_file(file_name, data, log_callback=None):
    try:
        norm_file_name = os.path.normpath(file_name)
        with open(norm_file_name, "wb") as f: f.write(data)
        if log_callback: log_callback(f"File saved to: {norm_file_name}")
        return True
    except Exception as e:
        if log_callback: log_callback(f"Error saving file '{os.path.normpath(file_name)}': {e}")
        return False

def parse_audio_mime_type(mime_type: str) -> dict[str, int | None]:
    bits_per_sample = 16; rate = 24000
    main_type_params = mime_type.split(";", 1); main_type = main_type_params[0].strip()
    if main_type.startswith("audio/L"):
        try: bits_per_sample = int(main_type.split("L", 1)[1])
        except (ValueError, IndexError): pass
    if len(main_type_params) > 1:
        params_str = main_type_params[1]; params = params_str.split(";")
        for param in params:
            param = param.strip()
            if param.lower().startswith("rate="):
                try: rate = int(param.split("=", 1)[1])
                except (ValueError, IndexError): pass
    return {"bits_per_sample": bits_per_sample, "rate": rate}

def convert_to_wav(audio_data: bytes, assumed_pcm_mime_type: str, log_callback=None) -> bytes | None:
    parameters = parse_audio_mime_type(assumed_pcm_mime_type)
    bits_per_sample = parameters.get("bits_per_sample", 16); sample_rate = parameters.get("rate", 24000)
    num_channels = 1; data_size = len(audio_data);
    if data_size == 0: return None
    bytes_per_sample = bits_per_sample // 8
    block_align = num_channels * bytes_per_sample; byte_rate = sample_rate * block_align
    riff_chunk_data_size = 36 + data_size
    header = struct.pack("<4sI4s4sIHHIIHH4sI", b"RIFF", riff_chunk_data_size, b"WAVE", b"fmt ", 16, 1, num_channels, sample_rate, byte_rate, block_align, bits_per_sample, b"data", data_size)
    return header + audio_data

def count_tokens_for_model(model_instance: genai.GenerativeModel, text_or_content, log_callback=None) -> int | None:
    try:
        token_count_obj = model_instance.count_tokens(text_or_content)
        return getattr(token_count_obj, 'total_tokens', None)
    except Exception as e:
        if log_callback: log_callback(f"Error counting tokens: {e}")
        return None

def count_words(text: str) -> int: return len(text.split()) if text else 0

def split_text_into_chunks(model_instance: genai.GenerativeModel, full_text: str, max_words_per_chunk: int, max_tokens_fallback: int, log_callback=None) -> list[str]:
    if log_callback: log_callback(f"Splitting text (length: {len(full_text)} chars, ~{count_words(full_text)} words) into chunks of max ~{max_words_per_chunk} words, fallback max ~{max_tokens_fallback} tokens.")
    chunks = []; current_char_offset = 0
    while current_char_offset < len(full_text):
        words_in_remaining_text = full_text[current_char_offset:].split()
        current_chunk_words = words_in_remaining_text[:max_words_per_chunk]
        candidate_chunk_text = " ".join(current_chunk_words)
        end_char_offset_candidate = current_char_offset + len(candidate_chunk_text)
        
        temp_search_offset = current_char_offset
        if current_chunk_words:
            for i, word in enumerate(current_chunk_words):
                found_pos = full_text.find(word, temp_search_offset)
                if found_pos != -1:
                    temp_search_offset = found_pos + len(word)
                else:
                    temp_search_offset = current_char_offset + len(" ".join(current_chunk_words[:i+1]))
                    break
            end_char_offset_candidate = temp_search_offset

        text_for_token_check = full_text[current_char_offset : end_char_offset_candidate]
        num_tokens = count_tokens_for_model(model_instance, text_for_token_check, log_callback)
        
        while (num_tokens is None or num_tokens > max_tokens_fallback) and len(current_chunk_words) > 1:
            current_chunk_words = current_chunk_words[:-10]
            if not current_chunk_words: break
            
            temp_search_offset = current_char_offset
            for i, word in enumerate(current_chunk_words):
                found_pos = full_text.find(word, temp_search_offset)
                if found_pos != -1:
                    temp_search_offset = found_pos + len(word)
                else:
                    temp_search_offset = current_char_offset + len(" ".join(current_chunk_words[:i+1]))
                    break
            end_char_offset_candidate = temp_search_offset
            text_for_token_check = full_text[current_char_offset : end_char_offset_candidate]
            num_tokens = count_tokens_for_model(model_instance, text_for_token_check, log_callback)

        final_text_segment = full_text[current_char_offset : end_char_offset_candidate]
        actual_end_char_offset = end_char_offset_candidate

        if end_char_offset_candidate < len(full_text):
            best_split_pos = -1
            for punc in ['\n\n', '\n', '.', '!', '?']:
                pos = final_text_segment.rfind(punc)
                if pos != -1:
                    best_split_pos = pos + len(punc)
                    break
            
            if best_split_pos != -1 and best_split_pos > len(final_text_segment) * 0.5:
                actual_end_char_offset = current_char_offset + best_split_pos

        final_chunk_to_add = full_text[current_char_offset : actual_end_char_offset].strip()
        if final_chunk_to_add:
            chunks.append(final_chunk_to_add)
            if log_callback:
                final_tokens = count_tokens_for_model(model_instance, final_chunk_to_add, None)
                log_msg = f"  Added chunk {len(chunks)}: {count_words(final_chunk_to_add)} words, {len(final_chunk_to_add)} chars, ~{final_tokens} tokens."
                if len(final_chunk_to_add) > 30: log_msg += f" Ends: '...{final_chunk_to_add[-30:]}'"
                log_callback(log_msg)
        
        current_char_offset = actual_end_char_offset
        if current_char_offset >= len(full_text): break

    if log_callback: log_callback(f"Text split into {len(chunks)} final chunk(s).")
    return chunks

# --- HOTFIX [2025-06-08 22:00]: Thêm khoảng lặng 2 giây giữa các part khi ghép file. Thay thế toàn bộ hàm này. ---
def merge_audio_files(audio_file_paths: list[str], output_merged_path: str, output_format: str = "wav", log_callback=None) -> bool:
    actual_files_to_merge = [f for f in audio_file_paths if f and os.path.exists(os.path.normpath(f))]
    if not actual_files_to_merge:
        if log_callback: log_callback("No valid audio part files to merge.")
        return False
    
    silence_duration_ms = 2000 
    silence_segment = AudioSegment.silent(duration=silence_duration_ms)
    
    if log_callback: log_callback(f"Merging {len(actual_files_to_merge)} files with a {silence_duration_ms}ms silence...")
    
    try:
        combined_audio = AudioSegment.from_file(actual_files_to_merge[0])
        for i in range(1, len(actual_files_to_merge)):
            segment = AudioSegment.from_file(actual_files_to_merge[i])
            combined_audio += silence_segment + segment
        
        if len(combined_audio) == 0: return False
            
        combined_audio.export(os.path.normpath(output_merged_path), format=output_format)
        if log_callback: log_callback(f"Successfully merged to {os.path.normpath(output_merged_path)}")
        return True
    except Exception as e:
        if log_callback: log_callback(f"Error merging audio: {e}")
        return False

def _generate_audio_for_single_chunk(model_instance, text_chunk, reading_style_prompt, voice_name, part_filename_base, part_num, total_parts, temp_setting_from_ui, top_p_from_ui, max_retries, part_timeout, log_callback_main, progress_callback_part):
    part_start_time = time.time()
    text_for_api = f"{reading_style_prompt.strip()}: {text_chunk}" if reading_style_prompt and reading_style_prompt.strip() else text_chunk
    
    for attempt in range(max_retries + 1):
        try:
            status_msg = f"Đang xử lý Part {part_num}/{total_parts}"
            if attempt > 0: status_msg += f" (Thử lại {attempt})"
            progress_callback_part(status_msg, "blue")

            tts_contents = [{"role": "user", "parts": [{"text": text_for_api}]}]
            ai_studio_config = {"temperature": temp_setting_from_ui, "top_p": top_p_from_ui, "response_modalities": ["AUDIO"], "speech_config": {"voice_config": {"prebuilt_voice_config": {"voice_name": voice_name}}}}
            request_options = types.RequestOptions(timeout=part_timeout)
            
            response_stream = model_instance.generate_content(tts_contents, generation_config=ai_studio_config, stream=True, request_options=request_options)
            
            all_audio_data_part = bytearray()
            for chunk in response_stream:
                if hasattr(chunk, 'parts') and chunk.parts and hasattr(chunk.parts[0], 'inline_data'):
                    all_audio_data_part.extend(chunk.parts[0].inline_data.data)

            if len(all_audio_data_part) < 1024 or (bytes(all_audio_data_part).count(b'\x00') / len(all_audio_data_part) > 0.99):
                raise genai.types.generation_types.StopCandidateException("Insufficient or silent audio data")

            data_buffer = bytes(all_audio_data_part)
            if not data_buffer.startswith(b'RIFF'):
                data_buffer = convert_to_wav(data_buffer, "audio/L16;rate=24000", log_callback_main)
            
            if data_buffer and save_binary_file(f"{part_filename_base}.wav", data_buffer, log_callback_main):
                time_taken = time.time() - part_start_time
                progress_callback_part(f"Hoàn thành Part {part_num} (mất {time_taken:.1f}s)", COLOR_OK)
                return f"{part_filename_base}.wav", time_taken
            else:
                raise IOError("Failed to save audio")

        except core_exceptions.ResourceExhausted as e:
            progress_callback_part(f"Lỗi Part {part_num}: Resource Exhausted!", COLOR_ERROR)
            raise e
        except Exception as e:
            log_callback_main(f"Part {part_num}, Attempt {attempt + 1} FAILED with {e.__class__.__name__}")
            if attempt < max_retries:
                progress_callback_part(f"Lỗi Part {part_num}, đang thử lại...", COLOR_WARN)
                time.sleep(2.0 * (2**attempt))
            else:
                progress_callback_part(f"Thất bại Part {part_num}", COLOR_ERROR)
                return None, time.time() - part_start_time
    return None, time.time() - part_start_time

def _process_text_chunk_worker(api_key_info, job_queue, results_list, feedback_queue, thread_id, reading_style_prompt, voice_name, temp_audio_dir, base_filename_no_ext, total_chunks, temp_setting, top_p_setting, max_retries_per_part, part_timeout, log_callback_ui, progress_callback_ui_thread, part_times_list, api_key_config_lock):
    try:
        with api_key_config_lock: 
            genai.configure(api_key=api_key_info["key"])
            model_instance_for_thread = genai.GenerativeModel(model_name="models/gemini-2.5-pro-preview-tts")
        progress_callback_ui_thread("Sẵn sàng", COLOR_NORMAL)
    except Exception as e:
        progress_callback_ui_thread("Lỗi khởi tạo", COLOR_ERROR)
        feedback_queue.put({"type": "FATAL_ERROR", "thread_id": thread_id})
        return

    while True: 
        try:
            part_index, text_chunk = job_queue.get(block=True, timeout=2.0)
        except queue.Empty:
            progress_callback_ui_thread("Hoàn thành, không còn việc.", COLOR_NORMAL)
            break
        
        try:
            file_path, time_taken = _generate_audio_for_single_chunk(
                model_instance_for_thread, text_chunk, reading_style_prompt,
                voice_name, os.path.normpath(os.path.join(temp_audio_dir, f"{base_filename_no_ext}_part_{part_index + 1:03d}")),
                part_index + 1, total_chunks, temp_setting, top_p_setting,
                max_retries_per_part, part_timeout, log_callback_ui,
                progress_callback_ui_thread
            )
            results_list[part_index] = file_path 
            part_times_list[part_index] = time_taken
            feedback_queue.put({"type": "TASK_DONE", "success": bool(file_path)})
            if file_path:
                time.sleep(5) # Dừng 3 giây để người dùng thấy trạng thái "Hoàn thành"
                
        except core_exceptions.ResourceExhausted:
            job_queue.put((part_index, text_chunk))
            feedback_queue.put({"type": "RESOURCE_EXHAUSTED", "thread_id": thread_id})
            break
        except Exception as e:
            results_list[part_index] = None
            part_times_list[part_index] = -1.0
            progress_callback_ui_thread(f"Lỗi không xác định Part {part_index + 1}", COLOR_ERROR)
            feedback_queue.put({"type": "TASK_DONE", "success": False})

def generate_tts_audio_multithreaded(
                    active_api_keys_info: list[dict], 
                    text_to_speak: str, 
                    voice_name: str,
                    output_file_path_base: str, 
                    log_callback_ui, 
                    progress_callback_ui_total, progress_callbacks_ui_thread: list,
                    reading_style_prompt: str = "",
                    temp_setting: float = 1.0, 
                    top_p_setting: float = 0.95,
                    max_words_per_part: int = 1000, 
                    max_tokens_fallback: int = 4800, 
                    max_retries_per_part: int = 1, 
                    part_timeout: int = 600
                    ):
    total_start_time = time.time()
    log_callback_ui(f"--- generate_tts_audio_multithreaded (v38.1) called ---")
    
    if not active_api_keys_info: log_callback_ui("No active API Keys provided."); return False, None
    norm_output_file_path_base = os.path.normpath(output_file_path_base)
    temp_audio_dir = os.path.normpath(os.path.join(os.path.dirname(norm_output_file_path_base), f"{os.path.basename(norm_output_file_path_base)}_parts_temp"))
    try:
        os.makedirs(temp_audio_dir, exist_ok=True)
        log_callback_ui(f"Created temp dir: {temp_audio_dir}")
    except Exception as e: log_callback_ui(f"Error creating temp dir: {e}"); return False, None

    try:
        genai.configure(api_key=active_api_keys_info[0]["key"])
        model_for_splitting = genai.GenerativeModel(model_name="models/gemini-2.5-pro-preview-tts")
        text_chunks = split_text_into_chunks(model_for_splitting, text_to_speak, max_words_per_part, max_tokens_fallback, log_callback_ui)
    except Exception as e:
        log_callback_ui(f"Failed during text splitting setup: {e}")
        return False, None
        
    if not text_chunks: log_callback_ui("Text could not be split."); return False, None

    total_chunks = len(text_chunks)
    job_queue = queue.Queue()
    for i, chunk in enumerate(text_chunks): job_queue.put((i, chunk))
    
    feedback_queue = queue.Queue()
    results_list = [None] * total_chunks
    part_times_list = [-1.0] * total_chunks
    
    num_worker_threads = len(active_api_keys_info)
    log_callback_ui(f"Initializing {num_worker_threads} worker threads with dynamic scaling...")
    
    threads = []
    for i in range(num_worker_threads):
        worker_thread = threading.Thread(
            target=_process_text_chunk_worker,
            args=(
                active_api_keys_info[i], job_queue, results_list, feedback_queue, i,
                reading_style_prompt, voice_name, temp_audio_dir, os.path.basename(norm_output_file_path_base),
                total_chunks, temp_setting, top_p_setting, max_retries_per_part, part_timeout, log_callback_ui,
                progress_callbacks_ui_thread[i] if i < len(progress_callbacks_ui_thread) else None,
                part_times_list, gemini_api_config_lock
            ),
            daemon=True
        )
        threads.append(worker_thread)
        worker_thread.start()
        log_callback_ui(f"Thread {i+1} started.")
        if i < num_worker_threads - 1:
            time.sleep(5)

    tasks_done_count = 0
    active_thread_count = num_worker_threads
    
    progress_callback_ui_total(0) # Bắt đầu ở 0%

    while tasks_done_count < total_chunks:
        try:
            feedback = feedback_queue.get(timeout=part_timeout + 30)
            
            if feedback["type"] == "TASK_DONE":
                tasks_done_count += 1
                progress_percent = int((tasks_done_count / total_chunks) * 100)
                progress_callback_ui_total(progress_percent)
            
            elif feedback["type"] == "RESOURCE_EXHAUSTED":
                active_thread_count -= 1
                log_callback_ui(f"MANAGER: Received ResourceExhausted signal. Active worker count reduced to: {active_thread_count}")
                if active_thread_count == 0:
                    log_callback_ui("MANAGER: All workers failed. Aborting.")
                    return False, None
            
            elif feedback["type"] == "FATAL_ERROR":
                 log_callback_ui(f"MANAGER: Worker reported fatal error. Aborting.")
                 return False, None
                 
        except queue.Empty:
            log_callback_ui(f"MANAGER: Timeout waiting for feedback. Process seems stuck. Aborting.")
            return False, None

    log_callback_ui("MANAGER: All tasks reported as done. Finalizing.")

    successful_parts = [res for res in results_list if res is not None]
    if len(successful_parts) != total_chunks:
        log_callback_ui("Error: Not all parts were generated successfully. Cannot merge.")
        return False, None

    log_callback_ui("All parts generated successfully. Starting merge process...")
    final_output_filename_with_ext = os.path.normpath(f"{output_file_path_base}.wav") 
    
    if merge_audio_files(results_list, final_output_filename_with_ext, "wav", log_callback_ui):
        total_time_taken = time.time() - total_start_time
        log_callback_ui(f"Successfully merged all parts into WAV. (Total time: {total_time_taken:.2f}s)")
        return True, final_output_filename_with_ext
    else:
        log_callback_ui("Error: Failed to merge audio parts.");
        return False, None