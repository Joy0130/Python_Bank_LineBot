# coding: utf-8
import datetime as dt
from dateutil.relativedelta import relativedelta
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
from io import StringIO
import matplotlib.pyplot as plt
import platform

import matplotlib
matplotlib.use("agg")

# 設置字體根據操作系統
if platform.system() == 'Windows':
    plt.rcParams['font.sans-serif'] = 'Microsoft Yahei'#['Microsoft JhengHei']  # Windows 10 字體設置
elif platform.system() == 'Darwin':  # Darwin 是 Mac OS 的內核名
    plt.rcParams['font.sans-serif'] = 'Arial Unicode MS'#['PingFang TC']  # Mac OS 字體設置
else:
    plt.rcParams['font.sans-serif'] = ['Noto Sans CJK TC']  # 通用字體設置

plt.rcParams['axes.unicode_minus'] = False  # 解決負號顯示問題

def getTaifexData(startdate, enddate):
    url = "https://www.taifex.com.tw/cht/3/pcRatio"
    payload = {
        'down_type':'',
        'queryStartDate':'2024%2F06%2F07',
        'queryEndDate':'2024%2F07%2F07'
    }
    payload['queryStartDate'] = startdate
    payload['queryEndDate'] = enddate
    res = requests.get(url, params = payload)
    soup = bs(res.text, 'lxml')
    tb = soup.select('table')[0]
    df = pd.read_html(StringIO(tb.prettify()))
    return df[0]
def createPCratioImage(imagefilename):
    data = []
    base = dt.datetime.today() - relativedelta(months= 6)
    while base <= dt.datetime.today():
        startdate = base.replace(day = 1).strftime("%Y/%m/%d")
        enddate = (base.replace(day = 1) + 
                relativedelta(months = 1) - 
                relativedelta(days = 1)).strftime("%Y/%m/%d")
        print(startdate, enddate)
        data.append(getTaifexData(startdate, enddate))
        base += relativedelta(months = 1) 
    df = pd.concat(data, ignore_index = True)
    
    df['買賣權未平倉量比率%'] = df['買賣權未平倉量比率%'].astype(float)
    # 將日期欄位轉換為 datetime 格式
    df['日期'] = pd.to_datetime(df['日期'], format='%Y/%m/%d')
    # 按日期排序
    df = df.sort_values('日期')
    
    # 繪製折線圖並保存為大尺寸png圖片
    plt.figure(figsize=(5, 3))  # 設置為1920x1080的比例
    plt.plot(df['日期'], df['買賣權未平倉量比率%'], linestyle='-')
    plt.xlabel('日期')
    plt.ylabel('買賣權未平倉量比率%')
    plt.title('買賣權未平倉量比率% 時間趨勢圖')
    plt.grid(True) #加入格線
    plt.xticks(rotation=45) #將X軸字體旋轉45度
    plt.tight_layout()
    plt.savefig(imagefilename, dpi=200)  # 設置dpi來控制圖片解析度
    plt.show()
if __name__=='__main__':
    createPCratioImage("pcratio.png")