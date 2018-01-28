#!/usr/local/bin/python
#coding=utf-8
# 趋势追踪策略
"""
http://t.cn/RqQv0JW
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
# from data_process.data_get import get_stock_k_line
from trade_process import efund_mail2
from tushare.util import dateu as du
import datetime
import tushare as ts
import cwavelet
from macd_back_test import match
#参数
prama_ma_short = 3 # 短均线
prama_ma_long = 7 # 长均线
prama_ma_long20 = 15 # 长均线
prama_ma_long30 = 20 # 长均线
filter_range = 0.004 # 滤波区间
drift = 0.0015 #漂移项
param_big_band = 0.02 #大波段判断条件
protect_big_band = 0.002 # 大波段保护止赢点

SIGNAL_BUY = 1  #买 
SIGNAL_SALE = -1 #卖
SIGNAL_DEFAULT = 0    
    
# 趋势追踪实时交易
# 参数
# code：股票代码
# df: 个股的K线数据
# price_now:实时股价
def tread_track_live_trading(code, price_now, df=None):
    # 分析某个时间段的股票
    #dateS = datetime.datetime.today().date() + datetime.timedelta(-100)
    #date_start = dateS.strftime("%Y-%m-%d")
    #df = df[df.index > date_start]
    try:
        fundlist = efund_mail2.get_histrydata(code,365)
        df = pd.DataFrame(fundlist[::-1], columns=['date', 'close', 'countclose','change'])
        #df = df.reindex(df.index[::-1])
    except Exception as e:
        print str(e)
        return    
    #print df
    close_price = df['close'].get_values()
    close_price = np.append(close_price, float(price_now))
    ma_short = pd.rolling_mean(close_price, prama_ma_short)
    ma_long  = pd.rolling_mean(close_price, prama_ma_long)
    ma_long20 = pd.rolling_mean(close_price, prama_ma_long20)
    ma_long30 = pd.rolling_mean(close_price, prama_ma_long30)
    #print ma_short

    signal = SIGNAL_SALE
    print '趋势追踪实时交易,交易开始'
    
    plt.figure(figsize=(8,5))
    plt.plot(range(len(ma_short)), ma_short, label=code, color="b", linewidth=1)
    plt.plot(range(len(ma_long)), ma_long, label=code, color="r",  linewidth=1)
    plt.plot(range(len(ma_long20)), ma_long20, label=code, color="g",  linewidth=1)
    plt.plot(range(len(ma_long30)), ma_long30, label=code,  linewidth=1)
    plt.plot(range(len(close_price)), close_price, label='close', linewidth=1)
    plt.xlabel("Time")
    plt.ylabel("Price")
    plt.savefig()
    
    # 过滤微小波动
    extreIndex = -1 #极值点的索引        
    for i in range(prama_ma_short+1, len(ma_short)-1):
        bMax = ma_short[i] > ma_short[i-1] and ma_short[i] > ma_short[i+1] # 极大值的条件
        bMin = ma_short[i] < ma_short[i-1] and ma_short[i] < ma_short[i+1] # 极小值的条件
        if bMax or bMin:
            extreIndex = i
        elif extreIndex > 0:
            if ma_short[i] > ma_short[extreIndex]*(1-filter_range) and \
                    ma_short[i] < ma_short[extreIndex]*(1+filter_range):
                ma_short[i] = ma_short[extreIndex]
                #print i,ma_short[i]
    
    #plt.plot(range(len(ma_short.get_values())), ma_short.get_values(), label=code, color="r", linewidth=1)
    
    # 交易次数
    count_sale = 0 
    count_buy = 0

    min_index_pre = 0 #前一个极小值
    max_index_pre = 0 #前一个极大值
    
    # 止损位
    keep_stop_price = 0 
    keep_stop_index = 0
    
    # 止赢位
    keep_win_price = 0 
    keep_win_index = 0
    
    total = 0
    price_buy = 0
    price_init = 0
    money_init = 50000
    stock_money = money_init
    stock_count = 0

    #for i in range(prama_ma_short+1, len(ma_short)-1):
    for i in range(len(ma_short)-30, len(ma_short)-1):    
        
        #滤波后的均线走平时（即处于滤波区间内），将其识别为一个点
        index_post = i+1
        
        try:
            while(ma_short[index_post] == ma_short[i] and index_post < len(ma_short)-1):
                index_post += 1
        except Exception as e:
            print str(e)
            
        # 长均线保护策略
        bLongMA_protect_close = True
        try:
            bLongMA_protect_close = ma_short[i] > ma_long[i] # 长均线保护是否关闭
        except Exception as e:
            print str(e)    
        #if bLongMA_protect_close == False:
            #print "长均线保护打开", i    
        
        # 高低点比较策略
        if ma_short[i] > ma_short[i-1] and ma_short[i] > ma_short[index_post]:
            #print '极大值:', ma_short[i], 'pos:', i
            if bLongMA_protect_close and max_index_pre > 0 and ma_short[i] < ma_short[max_index_pre] + drift*(i-max_index_pre) and signal == SIGNAL_BUY:
                signal = SIGNAL_SALE
                print '卖出:', close_price[i], 'pos:', i
                count_sale += 1
                total += close_price[i] - price_buy
                
                stock_money += stock_count * close_price[i]
                stock_count = 0
                
            max_index_pre = i
        elif ma_short[i] < ma_short[i-1] and ma_short[i] < ma_short[index_post]: 
            #print '极小值:', ma_short[i], 'pos:', i
            if bLongMA_protect_close and min_index_pre > 0 and ma_short[i] > ma_short[min_index_pre] + drift*(i-min_index_pre)  and signal == SIGNAL_SALE:
                signal = SIGNAL_BUY
                print '买入:', close_price[i], 'pos:', i
                count_buy += 1
                price_buy = close_price[i]
                if price_init == 0:
                    price_init = price_buy
                
                stock_count = (stock_money/100)/close_price[i]*100
                stock_money = stock_money - stock_count*close_price[i]
            min_index_pre = i
        
        # 高低点突破策略    
        # 股价突破前一个低点加漂移项，则卖出
        elif bLongMA_protect_close and signal == SIGNAL_BUY and min_index_pre > 0 and \
                ma_short[i] < ma_short[min_index_pre] + drift*(i-min_index_pre):
            signal = SIGNAL_SALE
            print '卖出:', close_price[i], 'pos:', i
            count_sale += 1
            total += close_price[i] - price_buy
            
            stock_money += stock_count * close_price[i]
            stock_count = 0
                
        # 股价突破前一个高点加漂移项，则买入    
        elif bLongMA_protect_close and signal == SIGNAL_SALE and max_index_pre > 0 and \
                ma_short[i] > ma_short[max_index_pre] + drift*(i-max_index_pre):    
            signal = SIGNAL_BUY
            print '买入:', close_price[i], 'pos:', i
            count_buy += 1
            price_buy = close_price[i]
            
            stock_count = (stock_money/100)/close_price[i]*100
            stock_money = stock_money - stock_count*close_price[i]

        # 大波段保护策略
        elif min_index_pre > 0 and ma_short[i] >= ma_short[min_index_pre]*(1+param_big_band):
            keep_stop_price = ma_short[i] * (1-protect_big_band) #止损位
            keep_stop_index = i
        elif bLongMA_protect_close and signal == SIGNAL_BUY and keep_stop_price > 0 and \
                 ma_short[i] < keep_stop_price + drift*(i-keep_stop_index):    
            signal = SIGNAL_SALE
            print '卖出:', close_price[i], 'pos:', i
            count_sale += 1
            total += close_price[i] - price_buy
            
            stock_money += stock_count * close_price[i]
            stock_count = 0
    print "buy count:", count_buy
    print "sale count:", count_sale
    
    if stock_count > 0:
        stock_money += stock_count * close_price[-1]
        total += close_price[-1] - price_buy
    
    print "每股盈利：", total, "收益率：", (stock_money-money_init)/money_init*100,"%\n"
    print '交易结束'        
            
    # plt.grid()
    # plt.legend()
    # plt.show()
    return (stock_money-money_init)/money_init*100 

# 趋势追踪回测
# 参数
# code：股票代码
# df: 个股的K线数据
def tread_track_backtest(code, fundlist,avg):
    # df = get_stock_k_line(code, date_start='2015-12-30', date_end='2016-05-05')
    # df=efund_mail2.get_histrydata(code,365)
    # fundlist = efund_mail2.get_histrydata(code, 365)
    df = pd.DataFrame(fundlist[::-1], columns=['date', 'close', 'countclose', 'change'])
    if len(df) == 0:
        return None
    # print df.head(2)
    # 分析某个时间段的股票
    #dateS = datetime.datetime.today().date() + datetime.timedelta(-100)
    #date_start = dateS.strftime("%Y-%m-%d")
    #df = df[df.index > date_start]
    #print df
    
    # try:
    #     df = df.reindex(df.index[::-1])
    # except Exception as e:
    #     print str(e)
    #     return
    #print df
    
    close_price = df['close'].get_values()
    ma_short = pd.rolling_mean(df['close'], avg[0])
    ma_long  = pd.rolling_mean(df['close'], avg[1])
    ma_long20 = pd.rolling_mean(close_price, avg[2])
    # ma_long30 = pd.rolling_mean(close_price, prama_ma_long30)
    #print ma_short
    
    signal = SIGNAL_SALE

    print '趋势追踪回测,交易开始'
    
    #plt.figure(figsize=(16,8))
    #plt.plot(range(len(ma_short)), ma_short.get_values(), label=code, color="b", linewidth=1)
    plt.figure(figsize=(6, 3))
    plt.plot(range(len(ma_short)), ma_short, label=code, color="b", linewidth=1)
    plt.plot(range(len(ma_long)), ma_long, label=code, color="r", linewidth=1)
    plt.plot(range(len(ma_long20)), ma_long20, label=code, color="g", linewidth=1)
    # plt.plot(range(len(ma_long30)), ma_long30, label=code, linewidth=1)
    plt.plot(range(len(close_price)), close_price, label='close', linewidth=1)
    plt.xlabel("Time")
    plt.ylabel("Price")
    plt.title(code[1])
    plt.savefig(r'E:\03IT\GitHub\stock-2\trade_process\stockdata\\'+code[1]+'.jpg')


    # 判断极点
    # for i in range(prama_ma_short+1, len(ma_short)-1):
    #     if ma_short[i] > ma_short[i-1] and ma_short[i] > ma_short[i+1]:
    #         print '极大值:', ma_short[i], 'pos:', i
    #
    #     elif ma_short[i] < ma_short[i-1] and ma_short[i] < ma_short[i+1]:
    #         print '极小值:', ma_short[i], 'pos:', i
    
    # 过滤微小波动
    extreIndex = -1 #极值点的索引        
    for i in range(prama_ma_short+1, len(ma_short)-1):
        bMax = ma_short[i] > ma_short[i-1] and ma_short[i] > ma_short[i+1] # 极大值的条件
        bMin = ma_short[i] < ma_short[i-1] and ma_short[i] < ma_short[i+1] # 极小值的条件
        if bMax or bMin:
            extreIndex = i
        elif extreIndex > 0:
            if ma_short[i] > ma_short[extreIndex]*(1-filter_range) and \
                    ma_short[i] < ma_short[extreIndex]*(1+filter_range):
                ma_short[i] = ma_short[extreIndex]
                #print i,ma_short[i]

    xticklabels = df['date'].apply(lambda x : str(x)).get_values()
    # print xticklabels[:5]
    # print xticklabels[-5:]

    #plt.plot(df['date'].get_values(), ma_short.get_values(), label=code, color="r", linewidth=1)
    #plt.plot(df['date'].get_values(), ma_short.get_values(), color="r")

    def wavlet_plt():
        # trick to get the axes
        fig,ax = plt.subplots()

        xValues = close_price[-200:]
        ax.plot(xValues, label=code, color="r", linewidth=1)
        zValues = cwavelet.getWaveletData(xValues, 'db2', 2, 'sqtwolog')
        zxValue = np.arange(0,len(zValues),1)
        #plt.figure(figsize=(16,8))

        ax.plot(zxValue, zValues, color="b", linewidth=2)
        ax.grid()

        # make ticks and tick labels
        xticks=range(0, len(xValues)+1,10)
        #xticklabels=['2000-01-0'+str(n) for n in range(1,len(xValues)+1)]
        xticklabels = df['date'].apply(lambda x : str(x)).get_values()


        # set ticks and tick labels
        ax.set_xticks(xticks)
        ax.set_xticklabels(xticklabels,rotation=15)

        #plt.legend()
        plt.show()

    min_index_pre = 0 #前一个极小值
    max_index_pre = 0 #前一个极大值

    keep_stop_up_price = 0
    keep_stop_down_price = 0

    stockPos = StockPosition(50000, code)
    
    #for i in range(prama_ma_short+1, len(ma_short)-1):
    for i in range(prama_ma_long-1, len(ma_short)-1):
        # print prama_ma_long, len(ma_short)-1
        # print ma_short[prama_ma_long]
        # print ma_long[prama_ma_long]

        #滤波后的均线走平时（即处于滤波区间内），将其识别为一个点
        index_post = i+1
        while (ma_short[index_post] == ma_short[i] and index_post < len(ma_short) - 1):
            index_post += 1
            
        # 长均线保护策略:
        # bLongMA_forbid_buy = ma_short[i] < ma_long[i] # 买入保护
        # bLongMA_forbid_sale = not bLongMA_forbid_buy      # 卖出保护
        #
        # if bLongMA_forbid_buy and signal == SIGNAL_BUY:
        #     signal = SIGNAL_SALE
        #     stockPos.sale(close_price[i], str(df.ix[i, 'date']))
        #     min_index_pre = 0
        #     max_index_pre = 0
        #     keep_stop_up_price = 0
        #     keep_stop_down_price = 0
        #     continue
        # if bLongMA_forbid_buy and signal == SIGNAL_SALE:
        #     continue

        #     if len(stockPos.transaction_records): # 有交易以后才考虑此情况
        #         signal = SIGNAL_BUY
        #         stockPos.buy(close_price[i], str(df.ix[i, 'date']))
        #         #print '买入:', close_price[i], '  ', str(df.ix[i, 'date'])
        #         continue

        # 高低点比较策略
        if ma_short[i] > ma_short[i-1] and ma_short[i] > ma_short[index_post]: # 极大值
            # <卖出> 如果当前高点比前一个高点的向下漂移项低，则空头开仓或持有空头；
            # <买入> 如果当前高点比前一个高点的向上漂移项高，则多头开仓或持有多头；
            if max_index_pre > 0 and i > max_index_pre:

                if signal == SIGNAL_BUY and ma_short[i] < ma_short[max_index_pre] - drift*(i-max_index_pre):
                    signal = SIGNAL_SALE
                    stockPos.sale(close_price[i], str(df.ix[i, 'date']))
                    min_index_pre = 0
                    max_index_pre = 0
                    keep_stop_up_price = 0
                    keep_stop_down_price = 0
                    continue
                elif signal == SIGNAL_SALE and ma_short[i] > ma_short[max_index_pre] + drift*(i-max_index_pre):
                    signal = SIGNAL_BUY
                    stockPos.buy(close_price[i], str(df.ix[i, 'date']))
                    keep_stop_up_price = 0
                    keep_stop_down_price = 0
                    continue

            max_index_pre = i
        elif ma_short[i] < ma_short[i-1] and ma_short[i] < ma_short[index_post]:  # 极小值
            # < 买入 > 如果当前低点比前一个低点的向上漂移项高，则多头开仓或持有多头；
            # < 卖出 > 如果当前低点比前一个低点的向下漂移项低，则空头开仓或持有空头
            if min_index_pre > 0 and i > min_index_pre:
                if signal == SIGNAL_SALE and ma_short[i] > ma_short[min_index_pre] + drift*(i-min_index_pre):
                    signal = SIGNAL_BUY
                    stockPos.buy(close_price[i], str(df.ix[i, 'date']))
                    keep_stop_up_price = 0
                    keep_stop_down_price = 0
                    continue
                elif signal == SIGNAL_BUY and ma_short[i] > ma_short[min_index_pre] - drift*(i-min_index_pre):
                    signal = SIGNAL_SALE
                    stockPos.sale(close_price[i], str(df.ix[i, 'date']))
                    min_index_pre = 0
                    max_index_pre = 0
                    keep_stop_up_price = 0
                    keep_stop_down_price = 0
                    continue

            min_index_pre = i
        
        # 高低点突破策略    
        # <卖出>如果滤波后的均线比前一个低点的向下漂移项低，则空头开仓或持有空头。
        if signal == SIGNAL_BUY and min_index_pre > 0 and ma_short[i] < ma_short[min_index_pre] - drift*(i-min_index_pre):
            signal = SIGNAL_SALE
            stockPos.sale(close_price[i], str(df.ix[i, 'date']))
            min_index_pre = 0
            max_index_pre = 0
            keep_stop_up_price = 0
            keep_stop_down_price = 0
            continue
                
        # <买入>如果滤波后的均线比前一个高点的向上漂移项高，则多头开仓或持有多头。
        elif signal == SIGNAL_SALE and max_index_pre > 0 and ma_short[i] > ma_short[max_index_pre] + drift*(i-max_index_pre):
            signal = SIGNAL_BUY
            stockPos.buy(close_price[i], str(df.ix[i, 'date']))
            keep_stop_up_price = 0
            keep_stop_down_price = 0
            continue

        # 大波段保护策略
        ## 向上的大波段
        if min_index_pre > 0 and close_price[i] >= ma_short[min_index_pre] * (1 + param_big_band):
            if close_price[i] * (1 - protect_big_band) > keep_stop_up_price:
                keep_stop_up_price = close_price[i] * (1 - protect_big_band)  # 止盈位
                keep_stop_up_index = i
        if signal == SIGNAL_BUY and keep_stop_up_price > 0 and \
                 close_price[i] < keep_stop_up_price + drift*(i-keep_stop_up_index):
            signal = SIGNAL_SALE
            stockPos.sale(close_price[i], str(df.ix[i, 'date']))
            min_index_pre = 0
            max_index_pre = 0
            keep_stop_up_price = 0
            keep_stop_down_price = 0
            continue
        
        ## 向下的大波段
        if max_index_pre > 0 and close_price[i] <= ma_short[max_index_pre] * (1 - param_big_band):
            if keep_stop_down_price == 0 or close_price[i] * (1 + protect_big_band) < keep_stop_down_price:
                keep_stop_down_price = close_price[i] * (1 + protect_big_band)  # 止损位
                keep_stop_down_index = i
        if signal == SIGNAL_SALE and keep_stop_down_price > 0 and \
                        close_price[i] > keep_stop_down_price + drift * (i + keep_stop_down_index):

            signal = SIGNAL_BUY
            keep_stop_up_price = 0
            keep_stop_down_price = 0
            stockPos.buy(close_price[i], str(df.ix[i, 'date']))
            continue
    stockPos.current_price = close_price[-1]
    stockPos.startcountPrice = close_price[0]

    stockPos.summary()
    print '交易结束'
    # plt.grid()
    # plt.legend()
    # plt.show()
    return stockPos

class StockPosition():

    def __init__(self, cash, code):
        self.code = code
        self.init_cash = cash
        self.cash = cash
        self.stock_count = 0
        self.transaction_records = {} # {2016-05-05: ('BUY', 20.1元, 1000股), 2016-03-01: ('SALE', 23.0元, 200股)}
        self.current_price = 0
        self.startcountPrice=0


    def buy(self, price, buy_date, buy_ratio=1.0):
        """
        :param price:
        :param buy_date:
        :param buy_ratio: 默认为1, 以所有现金购买;
        :return:
        """
        count = self.cash / price
        count = (int)(count / 100) * 100
        self.cash = self.cash - price * count
        self.stock_count = count
        self.transaction_records[buy_date] = ('BUY', price, count)
        print buy_date, 'BUY', price, count
        a = 0

    def sale(self, price, sale_date, sale_ratio=1.0):
        """
        :param price:
        :param sale_date:
        :param sale_ratio: 默认为1, 卖出所有;
        :return:
        """
        money = price * self.stock_count
        self.cash += money

        dates = self.transaction_records.keys()
        dates.sort()
        data = self.transaction_records.get(dates[-1])
        price_buy = data[1]

        self.transaction_records[sale_date] = ('SALE', price, self.stock_count)
        print sale_date, 'SALE', price, self.stock_count, "{:.2f}%".format((price-price_buy)/price_buy*100)

        self.stock_count = 0

    def summary(self, price = 0):
        """
        统计时的股价
        :param price:
        :return:
        """
        if price == 0:
            price = self.current_price
        initcash_now=self.init_cash*(self.current_price/self.startcountPrice)
        cash_now = self.cash + self.stock_count * price
        out1 = '交易次数:{}'.format(len(self.transaction_records))
        out2 = "收益率：{}%".format((cash_now - self.init_cash) / self.init_cash * 100)
        out3= "超额收益率：{}%".format((cash_now - initcash_now) / self.init_cash * 100)
        print self.code, out1, out2 ,out3
        return (cash_now - self.init_cash) / self.init_cash * 100, len(self.transaction_records)

def stock_trader_main(code):
    codelist = [['002963', 'egold'], ['003321', 'eoil'], ['004744', 'eGEI'], ['110003', 'eSSE50'], ['110020', 'HS300'],
            ['110031', 'eHSI'], ['161130', 'eNASDAQ100'], ['110028', 'anxinB'], ['110022', 'eConsumption '],
            ['161125', 'SPX500']]
    name = ['eGold', 'eoil', '创业板', '上证50', '沪深300', '恒生', '易方达纳斯达克100', '安心b']
    buysell = []
    stockTxtNewPath = "E:/03IT/GitHub/stock-2/stockdata/" + 'GAOpt100.txt'
    file_to_read = open(stockTxtNewPath, 'r')
    lines = file_to_read.readlines()  # 整行读取数据
    for i in codelist:
        if not lines:
            break
            pass
        else:
            contmatch = match('MA', i, lines)
            if len(contmatch) != 0:
                Avg = [int(contmatch[0][1].split(',')[0]), int(contmatch[0][1].split(',')[1]),
                       int(contmatch[0][1].split(',')[2])]
            elif (len(contmatch)==0):
                Avg = ([3, 8, 40])
        # save(strfundcode=i ,numdays=365*1)
        ifundlist = efund_mail2.get_histrydata(i, 365)
        buysell.append(tread_track_backtest(i,ifundlist,Avg))

    for i in buysell:
        i.summary()
        # url = 'http://fund.eastmoney.com/%s.html' % i[0]
        # todayvalue = efund_mail2.spider(url)
        # if todayvalue != None:
        #     tread_track_live_trading(i,todayvalue[1])

if __name__ == "__main__":
    # list_stock = ['600011','002600','002505','000725','000783','600048','300315','002167','601001']
    # result = []
    # for code in list_stock:
    #     result.append(tread_track_backtest(code))
    # print '平均盈亏',sum(result)/len(list_stock), '%'
    #result += tread_track('150172')         
    # df = ts.get_realtime_quotes(list_stock)
    # for index in df.index:
    #     tread_track_live_trading(list_stock[index], df.iloc[index]['price'])


    # import tushare as ts
    # df = ts.get_hs300s()
    # print df.head()
    # stockPoss = [tread_track_backtest(code) for code in df['code'].get_values()[::]]
    #
    # result_list = list()
    # for stockPos in stockPoss:
    #     if stockPos:
    #         r1, r2 = stockPos.summary()
    #         result_list.append((stockPos.code, r2, r1))
    # result_list = sorted(result_list, key = lambda x : x[2])
    # print result_list[0]
    # print result_list[-1]
    code = [['002963', 'egold'], ['003321', 'eoil'], ['004744', 'eGEI'], ['110003', 'eSSE50'], ['110020', 'HS300'],
            ['110031', 'eHSI'], ['161130', 'eNASDAQ100'], ['110028', 'anxinB'], ['110022', 'eConsumption '],
            ['161125', 'SPX500']]
    stock_trader_main(code)


    
    
    
    
    
    
    
    
    
    
