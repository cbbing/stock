#!/usr/local/bin/python
#coding=utf-8

import urllib2
import re
import Stock

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
    stdoutInfoList = stdoutInfo.split('\n')
    
    stockClassList = []
    for eachLine in stdoutInfoList:
        
        # 正则表达式说明
        # 搜索 “ ”双引号内的字符串，包含换行符，将匹配的字符串分为三组：用（）表示
        # group(2)：取第二组数据
        tempData = re.search('''(")(.+)(")''', eachLine).group(2)
        stockInfo = tempData.split(",")
        stockClassList.append(Stock(stockInfo))
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
        
        return Stock(stockInfo)
        
    except Exception as e:
        print(">>>>>> Exception: " + str(e))
    finally:
        None    