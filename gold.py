import pandas as pd
import requests
from bs4 import BeautifulSoup

# Target URL
url = "https://rate.bot.com.tw/gold/quote/recent"
response = requests.get(url)
response.raise_for_status()  # 确保请求成功
# Attempt to read the HTML table
# 解析网页内容
soup = BeautifulSoup(response.text, 'html.parser')
# 查找目标元素
div_info = soup.find('div', class_='cf').find('div', class_='pull-left trailer text-info')
# 提取挂牌时间
time = div_info.get_text(strip=True)
#爬取台灣銀行匯率資料
def get_gold_message():
    try:
        tables = pd.read_html(url)
        if tables:
            # Display the first table
            df = tables[0]

            # Combine the multi-level columns into single level by joining with '_'
            df.columns = ['_'.join(col).strip() for col in df.columns.values]

            # Print columns to inspect the structure
            # print(df.columns)

            # The combined column names based on the MultiIndex levels
            sell_column = '單位：新臺幣元_1 公克'
            buy_column = 'Unnamed: 1_level_0_Unnamed: 1_level_1'

            # Extract relevant columns baseQd on identified names
            df_filtered = df[[sell_column, buy_column]]

            # Rename columns for clarity
            df_filtered.columns = ['本行賣出', '本行買進']

            # Display the DataFrame
            print(time)
            print(df_filtered)
            
        else:
            print("無表格資料")
    except Exception as e:
        print(f"錯誤: {e}")
