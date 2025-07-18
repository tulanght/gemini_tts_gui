
# file-path: src/gemini_tts_app/google_api_handler.py
# version: 1.0
# last-updated: 2025-07-18
# description: Module xử lý logic kết nối và lấy dữ liệu từ Google Drive/Docs API.

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def build_drive_service(api_key):
    """Xây dựng một đối tượng service để tương tác với Google Drive API."""
    try:
        return build('drive', 'v3', developerKey=api_key)
    except Exception as e:
        print(f"Lỗi khi xây dựng Drive service: {e}")
        return None

def build_docs_service(api_key):
    """Xây dựng một đối tượng service để tương tác với Google Docs API."""
    try:
        return build('docs', 'v1', developerKey=api_key)
    except Exception as e:
        print(f"Lỗi khi xây dựng Docs service: {e}")
        return None

def list_files_in_folder(drive_service, folder_id):
    """Lấy danh sách các file Google Docs trong một thư mục cụ thể."""
    if not drive_service:
        return None, "Drive service không hợp lệ."

    try:
        query = f"'{folder_id}' in parents and mimeType='application/vnd.google-apps.document' and trashed=false"
        results = drive_service.files().list(
            q=query,
            pageSize=100, # Giới hạn 100 file mỗi lần gọi
            fields="nextPageToken, files(id, name)"
        ).execute()

        files = results.get('files', [])
        return files, None
    except HttpError as error:
        print(f"Lỗi API khi lấy danh sách file: {error}")
        return None, f"Lỗi API: {error.reason}"
    except Exception as e:
        print(f"Lỗi không xác định khi lấy danh sách file: {e}")
        return None, "Lỗi không xác định."


def get_doc_content(docs_service, document_id):
    """Đọc và trả về nội dung text của một file Google Doc."""
    if not docs_service:
        return None, "Docs service không hợp lệ."

    try:
        document = docs_service.documents().get(documentId=document_id).execute()
        content = document.get('body').get('content')

        full_text = ""
        for element in content:
            if 'paragraph' in element:
                for para_element in element.get('paragraph').get('elements'):
                    if 'textRun' in para_element:
                        full_text += para_element.get('textRun').get('content')
        return full_text, None
    except HttpError as error:
        print(f"Lỗi API khi đọc nội dung file: {error}")
        return None, f"Lỗi API: {error.reason}"
    except Exception as e:
        print(f"Lỗi không xác định khi đọc nội dung file: {e}")
        return None, "Lỗi không xác định."