#!/usr/local/bin/python
#coding=utf-8

from datetime import date
import time

stockNameList = [('600000', '浦发银行'), \
                 ('600048', '保利地产'), \
                 ('600011', '华能国际'),\
                 ('002600', '江粉磁材'),\
                 ('002505', '大康牧业'),\
                 ('000725', '京东方A'),\
                 ('000783', '长江证券'),\
                 ('300315', '掌趣科技'),\
                 ('002167', '东方锆业'),\
                 ('601001', '大同煤业'),\
                 ('150172', '证券B')]

class Stock:
    name = '' #股票名，中文
    code = '' #股票代码
    open = 0.0 #今日开盘价
    close = 0.0 #昨日收盘价
    current = 0.0 #当前价
    high = 0.0 #今日最高价
    low = 0.0 #今日最低价
    buyFiveInfo = [] #五档买入：[(买一报价，买一申请数)，买二...]
    saleFiveInfo = [] #五档卖出：(卖一报价，卖一申请数)，卖二...
    dealAmount = 0 #成交股数/100，N手
    dealTurnover = 0 #成交金额
    date = date.today() #日期
    time = time.localtime(time.time()) #时间
    
    #构造函数
    def __init__(self, sinaStockInfo):
        
        if len(sinaStockInfo) >= 32:
            self.name = sinaStockInfo[0]
            self.code = self.find_in_list(self.name)
            self.open = sinaStockInfo[1]
            self.close = sinaStockInfo[2]
            self.current = sinaStockInfo[3]
            self.high = sinaStockInfo[4]
            self.low = sinaStockInfo[5]
            self.dealAmount = sinaStockInfo[8]
            self.dealTurnover = sinaStockInfo[9]
            self.date = sinaStockInfo[30]
            self.time = sinaStockInfo[31]
            self.buyFiveInfo = [(sinaStockInfo[11], sinaStockInfo[10]),\
                                (sinaStockInfo[13], sinaStockInfo[12]),\
                                (sinaStockInfo[15], sinaStockInfo[14]),\
                                (sinaStockInfo[17], sinaStockInfo[16]),\
                                (sinaStockInfo[19], sinaStockInfo[18])]
            self.saleFiveInfo = [(sinaStockInfo[21], sinaStockInfo[20]),\
                                (sinaStockInfo[23], sinaStockInfo[22]),\
                                (sinaStockInfo[25], sinaStockInfo[24]),\
                                (sinaStockInfo[27], sinaStockInfo[26]),\
                                (sinaStockInfo[29], sinaStockInfo[28])]
    
    def find_in_list(self, name):
        try:
            for i in range(0, len(stockNameList)):
                if name == stockNameList[i][1]:
                    return stockNameList[i][0]
        except Exception as e:
            print "find_in_list() Exception:", str(e)
        finally:
            None     
        return ''

    