# 一、Render 部屬

## 1. 將程式放在github

## 2. 註冊/登入 Render

## 3. Settings
### (1) 連結自己github網址
![image](https://github.com/user-attachments/assets/41061b9d-b446-466b-9e33-4c1c6a97299c)

### (2)設定build.sh & requirements.txt
build.sh
``````
#!/bin/bash 
pip install --upgrade pip
pip install -r requirements.txt
``````
![image](https://github.com/user-attachments/assets/c7e5d9db-9f7d-4c9d-8c25-27b74447effe)

requirements.txt (依照自己程式中import的模組)
``````
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
``````
### (3) 設定 Start Command
![image](https://github.com/user-attachments/assets/ad10d778-edcf-4663-b399-b634390d4de0)

## 4. Environment：設定LineBot的環境變數
![image](https://github.com/user-attachments/assets/7fccf18a-487e-4e0b-9c81-83bfe4b18c00)

## 5. 部屬
![image](https://github.com/user-attachments/assets/d6f1f046-fb46-4a3c-bcfa-36a45f2694fc)

## 6. 部屬成功
![image](https://github.com/user-attachments/assets/395a24c7-7b26-43d9-a48e-bc11030b771e)
![image](https://github.com/user-attachments/assets/5e8a5069-cac3-453c-8d7b-07168fc8c17c)



---

# 二、機器人功能簡介

## 💱 匯率功能

輸入「**匯率**」開啟匯率選單，提供以下四項功能：

| 按鈕 | 輸入指令 | 說明 |
|------|----------|------|
| 各國匯率 | `各國匯率` | 顯示 19 種主要貨幣兌台幣的即時參考匯率（資料來源：open.er-api.com） |
| 牌告匯率 | — | 開啟台灣銀行官方牌告匯率頁面（含現金買入/賣出、即期買入/賣出） |
| 匯率換算 | `匯率換算` | 開啟台灣銀行線上匯率換算工具 |
| 歷史走勢查詢 | `歷史走勢查詢` | 顯示各幣別近六個月走勢圖選單（19 種貨幣，點擊直接查看台銀走勢圖） |

### 支援直接輸入幣別查詢

直接輸入中文幣別名稱或英文代碼，機器人會回傳該幣別的即時匯率：

| 支援輸入範例 | 對應幣別 |
|-------------|----------|
| `美金` / `USD` | 美元 |
| `日幣` / `日元` / `JPY` | 日圓 |
| `歐元` / `EUR` | 歐元 |
| `人民幣` / `CNY` | 人民幣 |
| `港幣` / `HKD` | 港幣 |
| `英鎊` / `GBP` | 英鎊 |
| `澳幣` / `AUD` | 澳幣 |
| `加拿大幣` / `CAD` | 加幣 |
| `新加坡幣` / `SGD` | 新加坡幣 |
| `瑞士法郎` / `CHF` | 瑞郎 |
| `韓元` / `KRW` | 韓元 |
| `泰銖` / `THB` | 泰銖 |
| `菲國比索` / `PHP` | 菲律賓比索 |
| `南非幣` / `ZAR` | 南非幣 |
| `瑞典幣` / `SEK` | 瑞典克朗 |
| `紐元` / `NZD` | 紐西蘭幣 |
| `越南盾` / `VND` | 越南盾 |
| `馬來幣` / `MYR` | 馬來西亞幣 |

---

## 🥇 黃金功能

輸入「**黃金**」開啟黃金選單，提供以下功能：

| 按鈕 | 輸入指令 | 說明 |
|------|----------|------|
| 黃金價格 | `黃金價格` | 顯示台灣銀行黃金存摺最新牌價（本行買進 / 本行賣出，每克） |
| 黃金買賣動態價格圖 | `黃金動態價格圖` | 開啟台灣銀行黃金年度動態走勢圖連結 |

---



## 2026-07-03

### 🐛 修正：各國匯率查詢錯誤（`'NoneType' object` 錯誤）

**問題原因：**
台灣銀行網站（`rate.bot.com.tw`）啟用了 **Cloudflare Bot 保護**，
Python `requests` 套件發出的 HTTP 請求會被攔截，回傳驗證頁面而非匯率資料，
導致 BeautifulSoup 找不到匯率表格（`table = None`），進而發生 `'NoneType'` 錯誤。

**修正方式：**
改用 **[open.er-api.com](https://open.er-api.com/v6/latest/TWD)** 免費匯率 API（無需 API Key）取代爬蟲。

| 項目 | 修改前 | 修改後 |
|------|--------|--------|
| 資料來源 | 爬取 rate.bot.com.tw（已被封鎖） | open.er-api.com 免費 API |
| 顯示欄位 | 現金買入 / 現金賣出 / 即期買入 / 即期賣出 | 1外幣兌台幣（參考匯率） |
| 支援幣別 | 台銀提供幣別 | 19 種主要貨幣 |

**修改前各國匯率查詢結果：**

![各國匯率舊版截圖](https://github.com/user-attachments/assets/41061b9d-b446-466b-9e33-4c1c6a97299c)

**修改函式：**
- 新增 `get_exchange_rates_from_api()` — 統一呼叫 API
- 更新 `get_exchange_rates_message()` — 改用 API 資料顯示各國匯率
- 更新 `get_exchange_rates()` — 相容原有 `generate_flex_message()` 呼叫
- 更新 `generate_flex_message()` — 調整欄位為「1外幣兌台幣」

---

### ✨ 新增：匯率選單加入「牌告匯率」按鈕

在「匯率」選單（`ButtonsTemplate`）新增第 4 個按鈕：

| 按鈕 | 功能 |
|------|------|
| 各國匯率 | 顯示 19 種貨幣即時參考匯率（機器人回覆） |
| 牌告匯率 ✨ | 開啟台灣銀行官方牌告匯率頁面（含現金/即期四欄） |
| 匯率換算 | 開啟台銀換算工具連結 |
| 歷史走勢查詢 | 顯示各幣別近六個月走勢圖選單 |

> **說明：** 由於台銀網站有 Bot 保護，無法直接爬蟲取得牌告匯率詳細資料，
> 因此「牌告匯率」採用 `URIAction` 連結方式，引導使用者至台銀官網查詢。
