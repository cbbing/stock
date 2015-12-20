#!/usr/local/bin/python
#coding=utf-8
# 趋势追踪策略

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from data_process.data_get import get_stock_k_line
from tushare.util import dateu as du
import datetime
import tushare as ts
import cwavelet

#参数
prama_ma_short = 15 # 短均线
prama_ma_long = 150 # 长均线
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
        df = get_stock_k_line(code)
        #df = df.reindex(df.index[::-1])
    except Exception as e:
        print str(e)
        return    
    #print df
    
    close_price = df['close'].get_values()
    close_price = np.append(close_price, float(price_now))
    ma_short = pd.rolling_mean(close_price, prama_ma_short)
    ma_long  = pd.rolling_mean(close_price, prama_ma_long)
    #print ma_short
    
    
    signal = SIGNAL_SALE
        
    print '交易开始'
    
    plt.figure(figsize=(16,8))
    #plt.plot(range(len(ma_short)), ma_short.get_values(), label=code, color="b", linewidth=1)
    
    plt.xlabel("Time")
    plt.ylabel("Price")
    
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
            
    plt.grid()
    #plt.legend()
    #plt.show()
    return (stock_money-money_init)/money_init*100 


# 趋势追踪回测
# 参数
# code：股票代码
# df: 个股的K线数据
def tread_track_backtest(code, df=None):

    df = get_stock_k_line(code)
    
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
    ma_short = pd.rolling_mean(df['close'], prama_ma_short)
    ma_long  = pd.rolling_mean(df['close'], prama_ma_long)
    #print ma_short
    
    signal = SIGNAL_SALE
        
    print '交易开始'
    
    plt.figure(figsize=(16,8))
    #plt.plot(range(len(ma_short)), ma_short.get_values(), label=code, color="b", linewidth=1)
    
    plt.xlabel("Time")
    plt.ylabel("Price")
    
    
        
    # 判断极点
#     for i in range(prama_ma_short+1, len(ma_short)-1):
#         if ma_short[i] > ma_short[i-1] and ma_short[i] > ma_short[i+1]:
#             print '极大值:', ma_short[i], 'pos:', i
#            
#         elif ma_short[i] < ma_short[i-1] and ma_short[i] < ma_short[i+1]: 
#             print '极小值:', ma_short[i], 'pos:', i
    
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
    
    #plt.plot(df.index, ma_short.get_values(), label=code, color="r", linewidth=1)

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
    xticklabels=['2000-01-0'+str(n) for n in range(1,len(xValues)+1)]

    # set ticks and tick labels
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels,rotation=15)

    #plt.legend()
    plt.show()

    # 交易次数    count_sale = 0
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
    for i in range(len(ma_short)-180, len(ma_short)-1):    
        
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
                #count_sale += 1
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
            #count_sale += 1
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
            #count_sale += 1
            total += close_price[i] - price_buy
            
            stock_money += stock_count * close_price[i]
            stock_count = 0
        
        
            
            
    print "buy count:", count_buy
    #print "sale count:", count_sale
    
    if stock_count > 0:
        stock_money += stock_count * close_price[-1]
        total += close_price[-1] - price_buy
    
    print "每股盈利：", total, "收益率：", (stock_money-money_init)/money_init*100,"%\n"
    
    print '交易结束'        
            
    plt.grid()
    #plt.legend()
    #plt.show()
    return (stock_money-money_init)/money_init*100 
    
if __name__ == "__main__":
    list_stock = ['600011','002600','002505','000725','000783','600048','300315','002167','601001']
    result = []
#     for code in list_stock:
#         result.append(tread_track_backtest(code))
#     print '平均盈亏',sum(result)/len(list_stock), '%'
    #result += tread_track('150172')         
    # df = ts.get_realtime_quotes(list_stock)
    # for index in df.index:
    #     tread_track_live_trading(list_stock[index], df.iloc[index]['price'])

    #for code in list_stock:
    tread_track_backtest('600000')
    
    
    
    
    
    
    
    
    
    