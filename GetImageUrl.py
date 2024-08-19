from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os
import dotenv
dotenv.load_dotenv()

def GetImageUrl(filename, isRemove = False):
    # 指定雲端資料夾ID
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER')
    # 設定存取權限
    SCOPES = ['https://www.googleapis.com/auth/drive']
    # 指定金鑰檔案
    SERVICE_ACCOUNT_FILE = 'google_auth.json'  # 金鑰檔案

    # 建立憑證物件
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    service = build('drive', 'v3', credentials=creds)

    #filename = "pcratio.png"  # 上傳檔的名字
    filelist = service.files().list(q=f"'{UPLOAD_FOLDER}' in parents").execute()

    if not filename in [file['name'] for file in filelist['files']]:
        media = MediaFileUpload(filename)
        file = {'name': os.path.basename(filename), 'parents': [UPLOAD_FOLDER]}

        print("正在上傳檔案...")
        file_id = service.files().create(body=file, media_body=media, fields='id').execute()
        print('雲端檔案ID：' + str(file_id['id']))
        
        if isRemove:
            if os.path.exists(filename):
                os.remove(filename)
            
        return 'https://drive.google.com/uc?export=view&id='+ str(file_id['id'])

    for file in filelist['files']:
        if filename == file['name']:
            #print('https://drive.google.com/uc?export=view&id=' + file['id'])
            return 'https://drive.google.com/uc?export=view&id=' + file['id']