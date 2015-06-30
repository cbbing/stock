#!/usr/local/bin/python
#coding=utf-8

import urllib2
import re
import Stock as st
import tushare as ts
import pandas as pd
import util.commons as cm
import util.stockutil as util
import time

#获取实时股价(同时获取多只股票)
def getLiveMutliChinaStockPrice(stockCodeList):
    stockCodeListEx = []
    for stockCode in stockCodeList:
        if len(str(stockCode)) == 6:
            exchange = "sh" if (int(stockCode) // 100000 == 6) else "sz"
            stockCode = exchange + str(stockCode)
        stockCodeListEx.append(stockCode)
    strStockCode = ','.join(stockCodeListEx)
    dataUrl = "http://hq.sinajs.cn/list=%s"  % (strStockCode)
    stdout = urllib2.urlopen(dataUrl)
    stdoutInfo = stdout.read().decode('gb2312').encode('utf-8')
    stdoutInfoList = stdoutInfo.splitlines()
    
    stockClassList = []
    index = 0
    for eachLine in stdoutInfoList:
        
        # 正则表达式说明
        # 搜索 “ ”双引号内的字符串，包含换行符，将匹配的字符串分为三组：用（）表示
        # group(2)：取第二组数据
        tempData = re.search('''(")(.+)(")''', eachLine).group(2)
        stockInfo = tempData.split(",")
        stock = st.Stock(stockInfo)
        stock.code = stockCodeList[index]
        index += 1
        stockClassList.append(stock)
    return stockClassList

#获取实时股价
def getLiveChinaStockPrice(stockCode):
    
    try:
        exchange = "sh" if (int(stockCode) // 100000 == 6) else "sz"
        dataUrl = "http://hq.sinajs.cn/list=" + exchange + stockCode
        stdout = urllib2.urlopen(dataUrl)
        stdoutInfo = stdout.read().decode('gb2312').encode('utf-8')
        
        # 正则表达式说明
        # 搜索 “ ”双引号内的字符串，包含换行符，将匹配的字符串分为三组：用（）表示
        # group(2)：取第二组数据
        tempData = re.search('''(")(.+)(")''', stdoutInfo).group(2)
        stockInfo = tempData.split(",")
        
        #bb[0]:股票名  bb[1]:今日开盘价    bb[2]：昨日收盘价    bb[3]:当前价格   bb[4]:今日最高价    bb[5]:今日最低价
        #bb[6]:买一报价 bb[7]:卖一报价     bb[8]:成交股票数/100 bb[9]:成交金额/w bb[10]:买一申请股数 bb[11]:买一报价
        #bb[12]:买二股数 bb[13]:买二报价   bb[14]:买三股数      bb[15]:买三报价  bb[16]:买四申请股数 bb[17]:买四报价
        #bb[18]:买五股数 bb[19]:买五报价   bb[20]:卖一股数      bb[21]:卖一报价  bb[22]:卖二申请股数 bb[23]:卖二报价
        #bb[24]:卖三股数 bb[25]:卖三报价   bb[26]:卖四股数      bb[27]:卖四报价  bb[28]:卖五股数     bb[29]:卖五报价
        #bb[30]:日期     bb[31]:时间     bb[8]:不知道
        
        return st.Stock(stockInfo)
        
    except Exception as e:
        print(">>>>>> Exception: " + str(e))
    finally:
        None    

# 获取A股所有股票的实时股价
# 通过 ts.get_today_all 获取
def getAllChinaStock():
    df = ts.get_today_all()
    stockList = []
    for se in df.get_values():
        stock = st.Stock('')
        stock.code = se[0]
        stock.name = se[1]
        stock.current = se[3]
        stock.open = se[4]
        stock.high = se[5]
        stock.low = se[6]
        stock.close = se[7]
        stock.dealAmount = se[8]/100
        stock.time = time.localtime(time.time()) #时间
        #print stock
        stockList.append(stock)
    return stockList

# 获取A股所有股票的实时股价
# 通过get_realtime_quotes接口获取
def getAllChinaStock2():
    df_list = pd.read_csv(cm.DownloadDir + cm.TABLE_STOCKS_BASIC + '.csv')
    stockList = df_list['code'].values;
    stockList_group = util.group_list(stockList, 20)
    print len(stockList_group)
    print stockList_group[1]
    stockList = []
    for group in stockList_group:
        df = ts.get_realtime_quotes(group)
    
        for se in df.get_values():
            stock = st.Stock('')
            stock.code = se[0]
            stock.name = se[1]
            stock.current = se[3]
            stock.open = se[4]
            stock.high = se[5]
            stock.low = se[6]
            stock.close = se[7]
            stock.dealAmount = se[8]/100
            stock.time = time.localtime(time.time()) #时间
            #print stock
            stockList.append(stock)
    return stockList
    
if __name__ == "__main__":
    getAllChinaStock()    
    

#df = ts.get_realtime_quotes('002600')
#print df[['code', 'name', 'price', 'bid', 'ask', 'volume', 'amount', 'time']]        