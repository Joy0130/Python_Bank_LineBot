import pandas as pd
from matplotlib import pyplot as plt
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("agg")

#以下是兩種調整中文字型
plt.rcParams['font.family'] = ["SimHei"]
plt.rcParams['font.family']=["Microsoft YaHei"]

url = "https://rate.bot.com.tw/gold/chart/year/TWD"

def createGoldhistorypriceImage(imagefilename):
    try:
        url = "https://rate.bot.com.tw/gold/chart/year/TWD"
        # 抓網站中的表格資料
        df = pd.read_html(url)[0]  # 读取第一个表格

        # 取網頁中所需的資料
        if "日期" in df.columns and "本行賣出價格" in df.columns:
            # 取出我們要的列
            df = df[["日期", "本行賣出價格"]]

            # 調整日期列的格式設置索引
            df["日期"] = pd.to_datetime(df["日期"], format="%Y/%m/%d")
            df.set_index("日期", inplace=True)

            # 依照索引 (日期) 排序
            df.sort_index(inplace=True)

            # 今天日期
            today = datetime.today()
            # 計算一年前的資料
            one_year_ago = today - timedelta(days=365)

            # 一年的資料
            df = df.loc[one_year_ago:today]

            print(df)

            # 本行賣出價格
            # plt.figure(figsize=[15, 5])
            # df["本行賣出價格"].plot(kind="line", label="本行賣出價格")

            # 移動平均線
            df["ma5"] = df["本行賣出價格"].rolling(window=5).mean()
            df["ma20"] = df["本行賣出價格"].rolling(window=20).mean()

            # 找出交叉點
            cross_points = df[(df["ma5"].shift(1) < df["ma20"].shift(1)) & (df["ma5"] > df["ma20"]) |
                              (df["ma5"].shift(1) > df["ma20"].shift(1)) & (df["ma5"] < df["ma20"])]

            # 繪製圖表
            plt.figure(figsize=[15, 5])
            df[["本行賣出價格", "ma5", "ma20"]].plot(kind="line", figsize=[15, 5])

            # 標示交叉點
            plt.scatter(cross_points.index, cross_points["ma5"], color='red',s=50,marker='o', label='交叉點', zorder=5 )

            # 圖表標題與標籤
            plt.title("本行賣出價格及平均移動線")
            plt.xlabel("日期")
            plt.ylabel("價格")
            plt.xlim(one_year_ago, today)
            plt.legend()
            plt.grid(True)

            # 顯示圖表
            plt.tight_layout()
            plt.savefig(imagefilename, dpi=400)
            plt.show()
            print("Plot saved as:", imagefilename)
            print(df)

        else:
            print("無資料")

    except Exception as e:
        print(f"錯誤: {e}")
# def createGoldhistorypriceImage(imagefilename):
#     try:
#         # 抓網站中的表格資料
#         df = pd.read_html(url)[0]  # 读取第一个表格

#         # 取網頁中所需的資料
#         if "日期" in df.columns and "本行賣出價格" in df.columns:
#         # 取出我们要的列
#             df = df[["日期", "本行賣出價格"]]

#             # 調整日期列的格式設置索引
#             df["日期"] = pd.to_datetime(df["日期"], format="%Y/%m/%d")
#             df.set_index("日期", inplace=True)

#             # 依照索引 (日期) 排序
#             df.sort_index(inplace=True)

#             # 今天日期
#             today = datetime.today()
#             # 計算一年前的資料
#             one_year_ago = today - timedelta(days=365)

#             # 一年的資料
#             df = df.loc[one_year_ago:today]

#             print(df)

#             # 本行賣出價格
#             # plt.figure(figsize=[15, 5])
#             # df["本行賣出價格"].plot(kind="line", label="本行賣出價格")

#             # 移動平均線
#             df["ma5"] = df["本行賣出價格"].rolling(window=5).mean()
#             df["ma20"] = df["本行賣出價格"].rolling(window=20).mean()
#             df[["本行賣出價格", "ma5", "ma20"]].plot(kind="line", figsize=[15, 5])

#             # 圖表標題與標籤
#             plt.title("本行賣出價格及平均移動線")
#             plt.xlabel("日期")
#             plt.ylabel("價格")
#             plt.xlim(one_year_ago, today)
#             plt.legend()
#             plt.grid(True)

#             # 顯示圖表
#             plt.tight_layout()
#             plt.savefig(imagefilename, dpi=200)
#             plt.show()
#             print("Plot saved as:", imagefilename)
#             print(df)

#         else:
#             print("無資料")

#     except Exception as e:
#         print(f"錯誤: {e}")

if __name__ == '__main__':
    createGoldhistorypriceImage('gold_historyprice_mark.png')
