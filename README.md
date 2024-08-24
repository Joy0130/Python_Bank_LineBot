#一、Render 部屬
##1. 將程式放在github

##2. 註冊/登入 Render

##3. Settings
###(1) 連結自己github網址
![image](https://github.com/user-attachments/assets/41061b9d-b446-466b-9e33-4c1c6a97299c)

###(2)設定build.sh & requirements.txt
build.sh
#!/bin/bash
pip install --upgrade pip
pip install -r requirements.txt
![image](https://github.com/user-attachments/assets/c7e5d9db-9f7d-4c9d-8c25-27b74447effe)
requirements.txt (依照自己程式中import的模組)
Flask
gunicorn
fastapi
line-bot-sdk
beautifulsoup4
pandas
google-auth
google-auth-oauthlib
google-auth-httplib2
google-cloud-storage
google-api-python-client
python-dotenv
matplotlib
lxml

###(3) 設定 Start Command
![image](https://github.com/user-attachments/assets/ad10d778-edcf-4663-b399-b634390d4de0)

##4. Environment：設定LineBot的環境變數
![image](https://github.com/user-attachments/assets/7fccf18a-487e-4e0b-9c81-83bfe4b18c00)

##5. 部屬
![image](https://github.com/user-attachments/assets/d6f1f046-fb46-4a3c-bcfa-36a45f2694fc)

##6. 部屬成功
![image](https://github.com/user-attachments/assets/395a24c7-7b26-43d9-a48e-bc11030b771e)
![image](https://github.com/user-attachments/assets/5e8a5069-cac3-453c-8d7b-07168fc8c17c)






