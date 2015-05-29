#!/usr/local/bin/python3
#coding=utf-8
#source http://www.cnblogs.com/txw1958/

import os, io, sys, re, time, json, base64
import webbrowser,  decimal
import urllib2
from time import sleep
from plot import plotData


period_All_List = [
                    "min",      #分时线
                    "daily",    #日K线
                    "weekly",   #周K线
                    "monthly"   #月K线
                  ]
period_min = period_All_List[0]
period_daily = period_All_List[1]

ChinaStockIndexList = [
    "000001", # sh000001 上证指数
    "399001", # sz399001 深证成指
#     "000300", # sh000300 沪深300
#     "399005", # sz399005 中小板指
#     "399006", # sz399006 创业板指
#     "000003",  # sh000003 B股指数
]
ChinaStockIndividualList = [
    "600011", #  
    "600000", #  
    "002600", #  
    "002505", #  
    "000725", #  
    "000783", #  
    "600048", #  
    "300315", #
    "002167", #
    "601001", #
    "150172", #  
]

ChinaStockNumIndividualList = [
    {'code':"600011", 'num':1100}, # 华能国际
    {'code':"600000", 'num':1900}, # 浦发银行
    {'code':"002600", 'num':1000}, # 江粉磁材
    {'code':"002505", 'num':1000}, # 大康牧业
    {'code':"000725", 'num':2000}, # 京东方A
    {'code':"000783", 'num':600},  # 长江证券
    {'code':"600048", 'num':2000}, # 保利地产
    {'code':"300315", 'num':200}, # 掌趣科技
    {'code':"002167", 'num':600}, # 东方锆业
    {'code':"601001", 'num':1000}, # 大同煤业
    {'code':"150172", 'num':5000}, # 证券B 
]

WorldStockIndexList = [
    {'code':"000001", 'yahoo':"000001.SS",'name':{'chinese':"中国上证指数", 'english':"CHINA SHANGHAI COMPOSITE INDEX"}},
    {'code':"399001", 'yahoo':"399001.SZ",'name':{'chinese':"中国深证成指", 'english':"SZSE COMPONENT INDEX"}},
    {'code':"DJI", 'yahoo':"^DJI",'name':{'chinese':"美国道琼斯工业平均指数", 'english':"Dow Jones Industrial Average"}},
    {'code':"IXIC", 'yahoo':"^IXIC",'name':{'chinese':"美国纳斯达克综合指数", 'english':"NASDAQ Composite"},},
    {'code':"GSPC", 'yahoo':"^GSPC",'name':{'chinese':"美国标准普尔500指数", 'english':"S&P 500"}},
    {'code':"N225", 'yahoo':"^N225",'name':{'chinese':"日本日经225指数", 'english':"NIKKEI 225"}},
    {'code':"TWII", 'yahoo':"^TWII",'name':{'chinese':"台湾台北加权指数", 'english':"TSEC weighted index"}},
    {'code':"HSI", 'yahoo':"^HSI",'name':{'chinese':"香港恒生指数", 'english':"HANG SENG INDEX"}},
    {'code':"FCHI", 'yahoo':"^FCHI",'name':{'chinese':"法国CAC40指数", 'english':"CAC 40"}},
    {'code':"FTSE", 'yahoo':"^FTSE",'name':{'chinese':"英国富时100指数", 'english':"FTSE 100"}},
    {'code':"GDAXI", 'yahoo':"^GDAXI",'name':{'chinese':"德国法兰克福DAX指数", 'english':"DAX"}
    }
]
WorldStockIndexList_SP500 =  WorldStockIndexList[7]

#国内股票数据：指数
def getChinaStockIndexInfo(stockCode, period):
    try:
        exchange = "sz" if (int(stockCode) // 100000 == 3) else "sh"
        #http://hq.sinajs.cn/list=s_sh000001
        dataUrl = "http://hq.sinajs.cn/list=s_" + exchange + stockCode
        stdout = urllib2.urlopen(dataUrl)
        stdoutInfo = stdout.read().decode('gb2312').encode('utf-8')
        tempData = re.search('''(")(.+)(")''', stdoutInfo).group(2)
        stockInfo = tempData.split(",")
        #stockCode = stockCode,
        stockName   = stockInfo[0]
        stockEnd    = stockInfo[1]  #当前价，15点后为收盘价
        stockZD     = stockInfo[2]  #涨跌
        stockLastEnd= str(float(stockEnd) - float(stockZD)) #开盘价
        stockFD     = stockInfo[3]  #幅度
        stockZS     = stockInfo[4]  #总手
        stockZS_W   = str(int(stockZS) / 100)
        stockJE     = stockInfo[5]  #金额
        stockJE_Y   = str(int(stockJE) / 10000)
        content = "#" + stockName + "#" + "(" + str(stockCode) + ")" + " 收盘：" \
          + stockEnd + "，涨跌：" + stockZD + "，幅度：" + stockFD + "%" \
          + "，总手：" + stockZS_W + "万" + "，金额：" + stockJE_Y + "亿" + "  "

        imgPath = "http://image.sinajs.cn/newchart/" + period + "/n/" + exchange + str(stockCode) + ".gif"
        twitter = {'message': content, 'image': ''}

    except Exception as e:
        print(">>>>>> Exception: " + str(e))
    else:
        return twitter
    finally:
        None

#国内股票数据：个股
def getChinaStockIndividualInfo(stockCode, period):
    try:
        exchange = "sh" if (int(stockCode) // 100000 == 6) else "sz"
        dataUrl = "http://hq.sinajs.cn/list=" + exchange + stockCode
        stdout = urllib2.urlopen(dataUrl)
        stdoutInfo = stdout.read().decode('gb2312').encode('utf-8')
        tempData = re.search('''(")(.+)(")''', stdoutInfo).group(2)
        stockInfo = tempData.split(",")
        #stockCode = stockCode,
        stockName   = stockInfo[0]  #名称
        stockStart  = stockInfo[1]  #开盘
        stockLastEnd= stockInfo[2]  #昨收盘
        stockCur    = stockInfo[3]  #当前
        stockMax    = stockInfo[4]  #最高
        stockMin    = stockInfo[5]  #最低
        stockUp     = round(float(stockCur) - float(stockLastEnd), 2)
        if (float(stockCur) == 0.0):
            stockUp = 0
        stockRange  = round(float(stockUp) / float(stockLastEnd), 4) * 100
        if (stockRange == 0):
            stockRange = 0
        stockVolume = round(float(stockInfo[8]) / (100 * 10000), 2)
        stockMoney  = round(float(stockInfo[9]) / (100000000), 2)
        stockTime   = stockInfo[31]

#         content = "#" + stockName + "#(" + stockCode + ")" + " 开盘:" + stockStart \
#         + ",最新:" + stockCur + ",最高:" + stockMax + ",最低:" + stockMin \
#         + ",涨跌:" + str(stockUp) + ",幅度:" + str(stockRange) + "%" \
#         + ",总手:" + str(stockVolume) + "万" + ",金额:" + str(stockMoney) \
#         + "亿" + ",更新时间:" + stockTime + "  "
        
        content = "#" + stockName + "#(" + stockCode + ")" + " 幅度:" + str(stockRange) + "%"\
        + ",最新:" + stockCur + ",最高/最低:" + stockMax + "/" + stockMin \
        + ",总手:" + str(stockVolume) + "万" + ",金额:" + str(stockMoney) \
        + "亿" + ",更新时间:" + stockTime + "  "

        #imgUrl = "http://image.sinajs.cn/newchart/" + period + "/n/" + exchange + str(stockCode) + ".gif"
        #twitter = {'message': content, 'image': imgUrl}
        
        twitter = {'message': content, 'image':'', 'stockUp':stockUp}

    except Exception as e:
        print(">>>>>> Exception: " + str(e))
    else:
        return twitter
    finally:
        None

#全球股票指数
def getWorldStockIndexInfo(stockDict):
    try:
        #http://download.finance.yahoo.com/d/quotes.csv?s=^IXIC&f=sl1c1p2l
        yahooCode = stockDict['yahoo']
        dataUrl = "http://download.finance.yahoo.com/d/quotes.csv?s=" + yahooCode + "&f=sl1c1p2l"

        stdout = urllib2.urlopen(dataUrl)
        stdoutInfo = stdout.read().decode('gb2312')
        tempData = stdoutInfo.replace('"', '')
        stockInfo = tempData.split(",")
        stockNameCn = stockDict['name']['chinese']
        stockNameEn = stockDict['name']['english']
        stockCode   = stockDict['code']
        stockEnd    = stockInfo[1]  #当前价，5点后为收盘价
        stockZD     = stockInfo[2]  #涨跌
        stockLastEnd= str(float(stockEnd) - float(stockZD)) #开盘价
        stockFD     = stockInfo[3]  #幅度
        percent     = float(stockFD.replace("%", ""))
        matchResult = re.search("([\w?\s?:]*)(\-)", stockInfo[4])  #日期和最新值
        stockDate   = matchResult.group(1)

        content = "#" + stockNameCn + "# " + stockNameEn + "(" + stockCode + ")" \
          + " 当前：" + stockEnd + ", 涨跌：" + stockZD + ", 幅度：" + stockFD \
          + ", 最后交易时间：" + stockDate

        twitter = content

    except Exception as err:
        print(">>>>>> Exception: " + yahooCode + " " + str(err))
    else:
        return twitter
    finally:
        None

def test_china_index_data():
    for stockCode in ChinaStockIndexList:
        twitter = getChinaStockIndexInfo(stockCode, period_daily)
        #print twitter['message'] + twitter['image']

def test_china_individual_data():
    
#     for stockCode in ChinaStockIndividualList:
#         twitter = getChinaStockIndividualInfo(stockCode, period_min)
#         print(twitter['message'] + twitter['image'])
    total = 0.0
    for stockCodeNumDict in ChinaStockNumIndividualList:
        twitter = getChinaStockIndividualInfo(stockCodeNumDict['code'], period_min)
        print twitter
        if twitter != None:
            total += twitter['stockUp'] * stockCodeNumDict['num'] 
            print twitter['message'] + twitter['image']
    print '当日盈亏:' + str(total)    
        

def test_global_index_data():
    for stockDict in WorldStockIndexList:
        print getWorldStockIndexInfo(stockDict)


def main():
    "main function"
    print base64.b64decode(b'Q29weXJpZ2h0IChjKSAyMDEyIERvdWN1YmUgSW5jLiBBbGwgcmlnaHRzIHJlc2VydmVkLg==').decode()
    
#     dataUrl = "http://ichart.yahoo.com/table.csv?s=600000.SS&a=08&b=25&c=2010&d=09&e=8&f=2010&g=d"
#     stdout = urllib.request.urlopen(dataUrl)
#     stdoutInfo = stdout.read().decode('utf-8')
    
    ISOTIMEFORMAT='%Y-%m-%d %X'
    while 1:
        str = time.strftime(ISOTIMEFORMAT, time.localtime())
        print str
        test_china_index_data()
        test_china_individual_data()
        #test_global_index_data()
        print '\n'
        sleep(180) #180s

if __name__ == '__main__':
    #plotData()
    main()
    
