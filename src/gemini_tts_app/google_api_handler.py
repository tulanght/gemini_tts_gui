# file-path: src/gemini_tts_app/google_api_handler.py
# version: 2.1
# last-updated: 2025-07-18
# description: Cập nhật các hàm để sử dụng credentials OAuth 2.0.

import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/documents.readonly"
]
TOKEN_PATH = "token.json"
CREDENTIALS_PATH = "credentials.json"

def get_credentials():
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Lỗi khi làm mới token: {e}")
                creds = None
        else:
            try:
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
                creds = flow.run_local_server(port=0)
            except FileNotFoundError:
                return None, "Không tìm thấy file credentials.json."
            except Exception as e:
                return None, f"Lỗi trong quá trình xác thực: {e}"

        if creds:
            with open(TOKEN_PATH, "w") as token:
                token.write(creds.to_json())
    return creds, None

def list_files_in_folder(creds, folder_id):
    try:
        service = build('drive', 'v3', credentials=creds)
        query = f"'{folder_id}' in parents and mimeType='application/vnd.google-apps.document' and trashed=false"
        results = service.files().list(
            q=query, pageSize=100, fields="files(id, name)"
        ).execute()
        return results.get('files', []), None
    except HttpError as error:
        return None, f"Lỗi API Drive: {error.reason}"
    except Exception as e:
        return None, f"Lỗi không xác định: {e}"

def get_doc_content(creds, document_id):
    try:
        service = build('docs', 'v1', credentials=creds)
        document = service.documents().get(documentId=document_id).execute()
        content = document.get('body').get('content')

        full_text = ""
        for element in content:
            if 'paragraph' in element:
                for para_element in element.get('paragraph').get('elements'):
                    if 'textRun' in para_element:
                        full_text += para_element.get('textRun').get('content')
        return full_text, None
    except HttpError as error:
        return None, f"Lỗi API Docs: {error.reason}"
    except Exception as e:
        return None, f"Lỗi không xác định: {e}"