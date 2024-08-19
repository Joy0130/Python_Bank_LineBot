from dateutil.relativedelta import relativedelta
from bs4 import BeautifulSoup as bs
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("agg")

# 以下是兩種調整中文字型，如果沒有亂碼可以省略此行
plt.rcParams['font.family'] = ["SimHei"]
plt.rcParams['font.family'] = ["Microsoft YaHei"]

url = "https://rate.bot.com.tw/gold/chart/year/TWD"

def createGoldpriceImage(imagefilename):
    try:
        # 抓網站中的表格資料
        print(f"Fetching data from URL: {url}")
        df_list = pd.read_html(url)
        print(f"Number of tables fetched: {len(df_list)}")

        # 讀取第一個表格資料
        df = df_list[0]
        print("Table columns:", df.columns)

        # 取網頁中所需的資料
        if "日期" in df.columns and "本行買入價格" in df.columns and "本行賣出價格" in df.columns:
            # 取出我们要的列
            df = df[["日期", "本行買入價格", "本行賣出價格"]]
            print("Filtered columns:", df.columns)

            # 日期格式
            df["日期"] = pd.to_datetime(df["日期"], format="%Y/%m/%d")
            print("Date conversion successful")

            # 依照日期排序
            df.sort_values(by="日期", inplace=True)
            print("Data sorted by date")

            # 繪製图表
            plt.figure(figsize=(14, 7))

            # 繪製图表本行買入價格
            plt.subplot(2, 1, 1)
            plt.plot(df["日期"], df["本行買入價格"], label="本行買入價格", color="blue")
            plt.xlabel("日期")
            plt.ylabel("本行買入價格")
            plt.title("本行買入價格")
            plt.legend()
            plt.grid(True)

            # 繪製图表本行賣出價格
            plt.subplot(2, 1, 2)
            plt.plot(df["日期"], df["本行賣出價格"], label="本行賣出價格", color="red")
            plt.xlabel("日期")
            plt.ylabel("本行賣出價格")
            plt.title("本行賣出價格")
            plt.legend()
            plt.grid(True)

            # 顯示圖表
            plt.tight_layout()
            plt.savefig(imagefilename, dpi=400)
            plt.show()
            print("Plot saved as:", imagefilename)
            print(df)
        else:
            print("無資料: Required columns not found")

    except Exception as e:
        print(f"错误: {e}")

if __name__ == '__main__':
    createGoldpriceImage("gold.png")
