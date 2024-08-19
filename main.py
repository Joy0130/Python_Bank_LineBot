from flask import Flask, request, abort
from linebot.exceptions import InvalidSignatureError
#接收
from linebot.v3.webhook import WebhookHandler,MessageEvent
from linebot.v3.messaging import ImageMessage
from linebot.models import FlexSendMessage, BubbleContainer, BoxComponent,TextComponent,SeparatorComponent,MessageEvent, TextSendMessage, TemplateSendMessage,TextMessage, ButtonsTemplate,MessageAction,ImageSendMessage
from linebot import LineBotApi
from linebot import LineBotApi, WebhookHandler
import requests
from bs4 import BeautifulSoup
import re
import os
import pandas as pd
import GetImageUrl #上傳google雲端
import goldprice #黃金
import gold_history_price #黃金歷史價格圖
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import dotenv
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("agg")
dotenv.load_dotenv()

app = Flask(__name__)

LINE_CHANNEL_ACCESS_TOKEN = 'M9oRyIx17/IYn3imOpgILugg1SpI2MG2dJtAeX/ZuWHTYmmdmNcXuLdbBGml8CIrcIS3ryfKQmD+bC4vgaUJLxzk0rph0xepuzJvcZJSDo8lQTj51e2mhXomGkrssxzEnRJ5cDgjS3pewbJHMxqYgQdB04t89/1O/w1cDnyilFU='
LINE_CHANNEL_SECRET = '3891d551b91c8fa64109ee3186f95e23'

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# 當呼叫line verify驗證成功後 會回應ok
@app.route("/callback", methods=['POST'])
def callback():
    
    signature = request.headers['X-Line-Signature']


    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

#幣別名稱對照表
currency_translation = {
    "美金": "USD",
    "日幣": "JPY",
    "日元": "JPY",
    "歐元": "EUR",
    "人民幣": "CNY",
    "港幣": "HKD",
    "英鎊": "GBP",
    "澳幣": "AUD",
    "加拿大幣": "CAD",
    "新加坡幣": "SGD",
    "瑞士法郎": "CHF",
    "韓元": "KRW",
    "泰銖": "THB",
    "菲國比索":"PHP",
    "南非幣":"ZAR",
    "瑞典幣":"SEK",
    "紐元":"NZD",
    "越南盾":"VND",
    "馬來幣":"MYR",
    "泰幣":"THB",
}


#爬取台灣銀行匯率資料
def get_exchange_rates_message():
    try:
        url = "https://rate.bot.com.tw/xrt"
        response = requests.get(url)
        response.encoding = 'utf-8'

        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', {'title': '牌告匯率'})

        # 取得表格中的內容
        contents = []

        # 表頭
        header = BoxComponent(
            layout="horizontal",
            contents=[
                TextComponent(text="幣別", weight="bold", flex=2, wrap=True),
                TextComponent(text="現金匯率 本行買入", weight="bold", flex=3, align="end", wrap=True),
                TextComponent(text="現金匯率 本行賣出", weight="bold", flex=3, align="end", wrap=True),
                TextComponent(text="即期匯率 本行買入", weight="bold", flex=3, align="end", wrap=True),
                TextComponent(text="即期匯率 本行賣出", weight="bold", flex=3, align="end", wrap=True)
            ]
        )
        contents.append(header)
        contents.append(SeparatorComponent())

        for tr in table.find('tbody').find_all('tr'):
            cells = [td.text.strip() for td in tr.find_all('td')]
            currency = re.search(r'\b[A-Z]{3}\b', cells[0]).group(0) # Find 3-letter abbreviation
            cash_buy = cells[1].strip()
            cash_sell = cells[2].strip()
            spot_buy = cells[3].strip()
            spot_sell = cells[4].strip()

            row = BoxComponent(
                layout="horizontal",
                contents=[
                    TextComponent(text=currency, flex=2, wrap=True),
                    TextComponent(text=cash_buy, flex=3, align="end", wrap=True),
                    TextComponent(text=cash_sell, flex=3, align="end", wrap=True),
                    TextComponent(text=spot_buy, flex=3, align="end", wrap=True),
                    TextComponent(text=spot_sell, flex=3, align="end", wrap=True)
                ]
            )
            contents.append(row)
            contents.append(SeparatorComponent())

        # Flex Message調整版面
        flex_message = FlexSendMessage(
            alt_text="匯率資訊",
            contents=BubbleContainer(
                direction='ltr',
                body=BoxComponent(
                    layout='vertical',
                    contents=contents,
                    spacing="xs"
                )
            )
        )
        return flex_message

    except Exception as e:
        return FlexSendMessage(
            alt_text="匯率資訊",
            contents=BubbleContainer(
                direction='ltr',
                body=BoxComponent(
                    layout='vertical',
                    contents=[TextComponent(text=f"An error occurred: {e}")]
                )
            )
        )
#抓匯率資料
def get_exchange_rates():
    try:
        url = "https://rate.bot.com.tw/xrt"
        response = requests.get(url)
        response.encoding = 'utf-8'

        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', {'title': '牌告匯率'})

        exchange_rates = {}

        for tr in table.find('tbody').find_all('tr'):
            cells = [td.text.strip() for td in tr.find_all('td')]
            currency = re.search(r'\b[A-Z]{3}\b', cells[0]).group(0)  # 找到三個字母的貨幣縮寫
            cash_buy = cells[1].strip()
            cash_sell = cells[2].strip()
            spot_buy = cells[3].strip()
            spot_sell = cells[4].strip()

            exchange_rates[currency] = {
                'cash_buy': cash_buy,
                'cash_sell': cash_sell,
                'spot_buy': spot_buy,
                'spot_sell': spot_sell
            }

        return exchange_rates
    except Exception as e:
        print(f"Error occurred: {e}")
        return None

# 生成 Flex Message 來顯示匯率資訊
def generate_flex_message(currency, rate_info):
    try:
        contents = []

        # 表頭
        header = BoxComponent(
            layout="horizontal",
            contents=[
                TextComponent(text="幣別", weight="bold", flex=2, wrap=True),
                TextComponent(text="現金匯率 本行買入", weight="bold", flex=3, align="end", wrap=True),
                TextComponent(text="現金匯率 本行賣出", weight="bold", flex=3, align="end", wrap=True),
                TextComponent(text="即期匯率 本行買入", weight="bold", flex=3, align="end", wrap=True),
                TextComponent(text="即期匯率 本行賣出", weight="bold", flex=3, align="end", wrap=True)
            ]
        )
        contents.append(header)
        contents.append(SeparatorComponent())

        # 加入指定幣別的匯率資料
        row = BoxComponent(
            layout="horizontal",
            contents=[
                TextComponent(text=currency, flex=2, wrap=True),
                TextComponent(text=rate_info['cash_buy'], flex=3, align="end", wrap=True),
                TextComponent(text=rate_info['cash_sell'], flex=3, align="end", wrap=True),
                TextComponent(text=rate_info['spot_buy'], flex=3, align="end", wrap=True),
                TextComponent(text=rate_info['spot_sell'], flex=3, align="end", wrap=True)
            ]
        )
        contents.append(row)
        contents.append(SeparatorComponent())

        # Flex Message
        flex_message = FlexSendMessage(
            alt_text=f"{currency}匯率資訊",
            contents=BubbleContainer(
                direction='ltr',
                body=BoxComponent(
                    layout='vertical',
                    contents=contents,
                    spacing="xs"
                )
            )
        )
        return flex_message

    except Exception as e:
        return TextSendMessage(text=f"An error occurred: {e}")
 
  
# 台灣銀行黃金
def get_gold_message():
    try:
        url = "https://rate.bot.com.tw/gold/quote/recent"
        response = requests.get(url)
        response.raise_for_status()  

        
        soup = BeautifulSoup(response.text, 'html.parser')

        
        div_info = soup.find('div', class_='cf').find('div', class_='pull-left trailer text-info')
        #取得掛牌時間
        time = div_info.get_text(strip=True)

        tables = pd.read_html(url)
        if tables:

            df = tables[0]

            df.columns = ['_'.join(col).strip() for col in df.columns.values]

            sell_column = '單位：新臺幣元_1 公克'
            buy_column = 'Unnamed: 1_level_0_Unnamed: 1_level_1'

            #資料列
            df_filtered = df[[sell_column, buy_column]]

            # 重命名列
            df_filtered.columns = ['本行賣出', '本行買進']

            df_filtered = df_filtered[~df_filtered.apply(lambda row: row.astype(str).str.contains('^0$|^1$', regex=True).any(), axis=1)]

            # Flex Message内容
            contents = []

            # 表頭
            header = BoxComponent(
                layout="horizontal",
                contents=[
                    TextComponent(text="商品", weight="bold", flex=2, wrap=True),
                    TextComponent(text="黃金1克", weight="bold", flex=3, align="end", wrap=True),
                    TextComponent(text=time, weight="bold", flex=3, align="end", wrap=True)
                ]
            )
            contents.append(header)
            contents.append(SeparatorComponent())

            # 表格
            for index, row in df_filtered.iterrows():
                row_content = BoxComponent(
                    layout="horizontal",
                    contents=[
                        TextComponent(text="黃金", flex=2, wrap=True),
                        TextComponent(text=row['本行賣出'], flex=3, align="end", wrap=True),
                        TextComponent(text=row['本行買進'], flex=3, align="end", wrap=True)
                    ]
                )
                contents.append(row_content)
                contents.append(SeparatorComponent())

            # Flex Message 調整版面
            flex_message = FlexSendMessage(
                alt_text="黃金資訊",
                contents=BubbleContainer(
                    direction='ltr',
                    body=BoxComponent(
                        layout='vertical',
                        contents=contents,
                        spacing="xs"
                    )
                )
            )
            return flex_message

        else:
            return FlexSendMessage(
                alt_text="黃金資訊",
                contents=BubbleContainer(
                    direction='ltr',
                    body=BoxComponent(
                        layout='vertical',
                        contents=[TextComponent(text="無表格資料")]
                    )
                )
            )

    except Exception as e:
        return FlexSendMessage(
            alt_text="黃金資訊",
            contents=BubbleContainer(
                direction='ltr',
                body=BoxComponent(
                    layout='vertical',
                    contents=[TextComponent(text=f"發生錯誤: {e}")]
                )
            )
        )

#模板訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    cmdtxt = event.message.text.lower()
    user_message = event.message.text.strip()
    # 輸入中文則轉換為英文
    currency_code = currency_translation.get(user_message, user_message.upper())
    # 取得匯率資料
    exchange_rates = get_exchange_rates()

    if exchange_rates and currency_code in exchange_rates:
        rate_info = exchange_rates[currency_code]
        flex_message = generate_flex_message(currency_code, rate_info)
        line_bot_api.reply_message(event.reply_token, flex_message)
   
    elif cmdtxt == "匯率":
        line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage(
                alt_text="模板訊息",
                template=ButtonsTemplate(
                    thumbnail_image_url="https://i.imgur.com/vRKlaXQ.png",
                    title="匯率",
                    text="現金匯率/即時匯率/匯率換算",
                    actions=[
                        MessageAction(
                            label="各國匯率",
                            text="各國匯率"
                        ),
                        MessageAction(
                            label="匯率換算", 
                            text="匯率換算",
                        ),
                        MessageAction(
                            label="澳幣歷史價錢查詢", 
                            text="澳幣歷史價錢查詢",
                        ),
                        MessageAction(
                            label="日圓(幣)歷史價錢查詢", 
                            text="日圓(幣)歷史價錢查詢",
                        )
                    ]
                )
            )
        )
    elif cmdtxt == "黃金":
        line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage(
                alt_text="模板訊息",
                template=ButtonsTemplate(
                    thumbnail_image_url="https://i.imgur.com/Derw1Du.png",
                    title="黃金",
                    text="黃金價格/買賣黃金趨勢圖/歷史黃金趨勢圖",
                    actions=[
                        MessageAction(
                            label="黃金價格",
                            text="黃金價格"
                        ),
                         MessageAction(
                            label="黃金買賣價格圖",
                            text="黃金價格圖"
                        ),
                         MessageAction(
                            label="黃金買賣動態價格圖",
                            text="黃金動態價格圖"
                        ),
                         MessageAction(
                            label="黃金平均移動線圖",
                            text="黃金平均移動線圖"
                        )
                    ]
                )
            )
        )

    elif cmdtxt == "各國匯率":
        flex_message = get_exchange_rates_message()
        line_bot_api.reply_message(
            event.reply_token,
            flex_message
        )
    elif cmdtxt == "匯率換算":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="請點選此連結：https://rate.bot.com.tw/trial/t14")
        )
    elif cmdtxt == "澳幣歷史價錢查詢":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="請點選此連結：https://rate.bot.com.tw/xrt/quote/l6m/AUD")
        )
    elif cmdtxt == "日圓(幣)歷史價錢查詢":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="請點選此連結：https://rate.bot.com.tw/xrt/quote/l6m/JPY")
        )
#黃金價格
    elif cmdtxt == "黃金價格":
        flex_message = get_gold_message()
        line_bot_api.reply_message(
            event.reply_token,
            flex_message
        )
#黃金價格圖
    elif cmdtxt == "黃金價格圖":
        imagefile = "gold.png"
        goldprice.createGoldpriceImage(imagefile)
        url = GetImageUrl.GetImageUrl(imagefile)
        if url:
            image_message = ImageSendMessage(
                original_content_url=url,
                preview_image_url=url
            )

            line_bot_api.reply_message(
                event.reply_token,
                image_message
            )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="價格圖片上傳失敗")
            )
#黃金動態價格圖    
    elif cmdtxt == "黃金動態價格圖":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="請點選此連結：https://rate.bot.com.tw/gold/chart/year/TWD")
        )
#黃金歷史價格圖
    elif cmdtxt == "黃金平均移動線圖":
        imagefile = "gold_historyprice_mark.png"
        gold_history_price.createGoldhistorypriceImage(imagefile)
        url = GetImageUrl.GetImageUrl(imagefile)
        if url:
            image_message = ImageSendMessage(
                original_content_url=url,
                preview_image_url=url
            )

            line_bot_api.reply_message(
                event.reply_token,
                image_message
            )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="平均移動線圖片上傳失敗")
            )
    else:
        response_message = "無法找到對應的匯率資訊，請確認輸入的幣別名稱是否正確。"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=response_message))

if __name__ == "__main__":
    app.run(port=5002) #預設5000 mac執行要加上port5001或5002
    
