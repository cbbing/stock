#!/usr/local/bin/python
# -*- coding: UTF-8 -*-

#回测均线策略

import pandas as pd
import matplotlib.pyplot as plt
import os,sys
import numpy as np
from data_process.download_stock import downloadAllHistoryAShareData
# from trade_process import efund_mail2
from pyevolve import G1DList, GSimpleGA, Selectors, Scaling
from pyevolve import Mutators, Initializators,GAllele
from data_process.dataDownloadByDongfangcf import downlaodDataBycode
reload(sys)
sys.setdefaultencoding('utf-8')
# import sys
# reload( sys )
# sys.setdefaultencoding('gbk')
# AVR_SHORT = 12
# AVR_LONG = 40
 
SIGNAL_BUY = 1  #买 
SIGNAL_SALE = -1 #卖
SIGNAL_DEFAULT = 0
    
    
# 导入csv股票数据，写5日、20日、60日移动平均线
def processEMA(stockCsvPath, stockCsvNewPath):
    #导入数据，stockCsvPath为在电脑中的路径
    stock_data = pd.read_csv(stockCsvPath)
    
    # 将数据按照交易日期从远到近排序
    stock_data.sort('Date', inplace=True)
    
    #=====================计算移动平均线
    
    # 分别计算5日、20日、60日移动平均线
    ma_list = [5, 20, 60]
    
    # 计算简单算术移动平均线MA - 注意：stock_data['close']为股票每条的收盘价
    for ma in ma_list:
        stock_data['MA_' + str(ma)] = pd.rolling_mean(stock_data['Adj Close'], ma)
        
    # 计算指数平滑移动平均线EMA
    for ma in ma_list:
        stock_data['EMA_' + str(ma)] = pd.ewma(stock_data['Adj Close'], span=ma)
        
    # 将数据按照交易日期从近到远排序
    stock_data.sort('Date', ascending=False, inplace=True)
    
    stock_data['DIF'] = stock_data['EMA_'+str(ma_list[0])] - stock_data['EMA_'+str(ma_list[-1])]
    stock_data['DEA_' + str(10)] = pd.ewma(stock_data['DIF'], span=10)
    
    # =================================== 将算好的数据输出到csv文件，这里请填写输出文件在您电脑的路径
    stock_data.to_csv(stockCsvNewPath, index=False)   
    
# 自适应均线    
def self_adaptive_ma(stock_data,Avg):
    AVR_SHORT = Avg[0]
    AVR_LONG = Avg[1]
     # 将数据按照交易日期从远到近排序
    # stock_data.sort('Date', inplace=True)
    
    close_price = stock_data['Adj Close'].get_values()
    high_price = stock_data['High'].get_values()
    low_price = stock_data['Low'].get_values()
    longDay = 100
    
    print len(close_price)
    if len(close_price) < 100:
        return
    
    print close_price[-10:-1]
    direction = abs(close_price[-1] - close_price[-10])
    volatility = sum(abs(close_price[i+1]-close_price[i]) for i in range(-9,0))
    ER = abs(direction/volatility)
    fastSC = 2.0/(2.0+1)
    slowSC = 2.0/(30.0+1)
    sSC = ER * (fastSC-slowSC) + slowSC
    constaint = sSC*sSC
    
    #EMA 100
    ema_close_100 = pd.ewma(close_price, span=longDay)
    ema_high_100 = pd.ewma(high_price, span=longDay)
    ema_low_100 = pd.ewma(low_price, span=longDay)
    
    amaClose = ema_close_100[-1] + constaint * (close_price[-1] - ema_close_100[-1])
    amaHigh = ema_high_100[-1] + constaint * (high_price[-1] - ema_high_100[-1])
    amaLow = ema_low_100[-1] + constaint * (low_price[-1] - ema_low_100[-1])
    print ema_close_100[-1], ema_high_100[-1], ema_low_100[-1]
    
    BKPRICE = 0.0
    SKPRICE = float('Inf')
    status = SIGNAL_DEFAULT
    print high_price[-1], low_price[-1], close_price[-1]
    if low_price[-1] > amaHigh:
        status = SIGNAL_BUY
    elif close_price[-1] < amaClose or close_price[-1] <= 0.995 * BKPRICE:
        status = SIGNAL_BUY
    elif high_price[-1] < amaLow:
        status = SIGNAL_SALE    
    elif close_price[-1] > amaClose or close_price[-1] >= 1.005 * SKPRICE:
        status = SIGNAL_SALE    
        
    return status   
     

# MA指标择时  (回测）
def select_Time_MA(stock_data, stockName,*Avg):
    AVR_SHORT = Avg[0]
    AVR_LONG = Avg[1]
    AVR_vLONG = Avg[2]
    start_money = 100000000
    now_count = 0
    now_money = start_money
    
    # 将数据按照交易日期从远到近排序
    # stock_data.sort('Date', inplace=True)
    close_price = stock_data['Adj Close'].get_values()
    
    #EMA 
    ma_list = [AVR_SHORT, AVR_LONG,AVR_vLONG]
    ema_close_short = pd.ewma(close_price, span=ma_list[0])
    ema_close_long = pd.ewma(close_price, span=ma_list[1])
    ema_close_vlong = pd.ewma(close_price, span=ma_list[2])
    
    signals = [0]*(ma_list[1]+1)
    tradeTimes = 0
    bBuySignal = True
    currentSignal=[]
    for t in range(ma_list[1]+1, len(close_price)):
        signal = SIGNAL_DEFAULT
        if ema_close_short[t] > ema_close_short[t-1] and ema_close_short[t] >ema_close_vlong[t] \
                        and ema_close_short[t-1] < ema_close_vlong[t-1]:
            if bBuySignal:
                signal = SIGNAL_BUY
                now_count = (int)(start_money / close_price[t] /100)*100
                now_money = start_money - now_count * close_price[t]
                #print u"股票价格/持股数/剩余金额：",close_price[t], '/',  now_count, '/', now_money
                bBuySignal = False  
        # elif ema_close_long[t] < ema_close_long[t-1] and ema_close_short[t] < ema_close_long[t] \
        #                 and ema_close_short[t-1] > ema_close_long[t-1]:
        elif ema_close_short[t] < ema_close_short[t - 1] and ema_close_short[t] < ema_close_long[t] \
                 and ema_close_short[t - 1] > ema_close_long[t - 1]:  #
            if bBuySignal == False:
                signal = SIGNAL_SALE
                now_money += now_count * close_price[t]
                now_count = 0
                #print u"股票价格/持股数/剩余金额：",close_price[t], '/',  now_count, '/', now_money
                bBuySignal = True    
        signals.append(signal)
        if signal != 0:
            # print 't:', str(stock_data.ix[t, 'Date']), '  signal:', signal
            tradeTimes += 1
            if (t <= len(close_price)) and (t >= (len(close_price) - 4)):
                currentSignal.append(['t:', str(stock_data.ix[t, 'Date']), '  signal:', signal])
    getmony=(now_money + now_count * close_price[-1] - start_money) / start_money
    over=(getmony -(close_price[-1]-close_price[ma_list[1]+1])/close_price[ma_list[1]+1])*100
    print stockName[0],stockName[1], u"收益率：", getmony*100, '%\t'+ u'超收：',over, '%\t'\
        u"交易次数", tradeTimes, u" 最新市值：", now_money+now_count * close_price[-1]  ,str(Avg)
    stock_data['SIGNAL_MA'] = signals
    return [(now_money+now_count * close_price[-1]-start_money)/start_money*100,currentSignal,tradeTimes,over]
#     fig = plt.figure(facecolor='white')
#     left, width = 0.1, 0.8
#     rect1 = [left, 0.5, width, 0.4]
#     rect2 = [left, 0.1, width, 0.3]
#     
#     axescolor  = '#f6f6f6'  # the axes background color
#     ax1 = fig.add_axes(rect1, axisbg=axescolor)  #left, bottom, width, height
#     ax2 = fig.add_axes(rect2, axisbg=axescolor, sharex=ax1)
#     
#     ax1.plot(range(len(close_price)), close_price, color="black", linewidth=1)
#     ax1.grid()
#     ax2.plot(range(len(ema_close_long)), ema_close_long,label='', color="red", linewidth=1)
#     ax2.plot(range(len(ema_close_short)), ema_close_short,label='', color="blue", linewidth=1)
#     ax2.grid()
    #plt.show()
    
    # 将数据按照交易日期从近到远排序
    #stock_data.sort('date', ascending=False, inplace=True)
    
# MACD指标择时 (回测）
def select_Time_MACD(stock_data, stockName,*Avg):
    AVR_SHORT = Avg[0]
    AVR_LONG = Avg[1]
    AVR_vLONG = Avg[2]
    start_money = 100000000
    now_count = 0
    now_money = start_money
    
    # 将数据按照交易日期从远到近排序
    # stock_data.sort('Date', inplace=True)
    close_price = stock_data['Adj Close'].get_values()
    
    #EMA 
    ma_list = [AVR_SHORT, AVR_LONG,AVR_vLONG]
    ma_dea = Avg[2] #10 默认9
    ema_close_short = pd.ewma(close_price, span=ma_list[0])
    ema_close_long = pd.ewma(close_price, span=ma_list[1])
    ema_close_vlong = pd.ewma(close_price, span=ma_list[2])

    dif_price = ema_close_short - ema_close_long
    dea_price = pd.ewma(dif_price, span=ma_dea)
    macd_price = 2 * (dif_price - dea_price)
    
    signals = [0]*(ma_list[1]+1)
    tradeTimes = 0
    bBuySignal = True
    currentSignal=[]
    for t in range(ma_list[1]+1, len(close_price)):
        signal = SIGNAL_DEFAULT
        if dif_price[t] > dif_price[t-1] and dif_price[t] > dea_price[t] \
                                        and dif_price[t-1] < dea_price[t-1] and dea_price[t] > 0:
            if bBuySignal:
                signal = SIGNAL_BUY
                now_count = (int)(now_money / close_price[t] /100)*100
                now_money = start_money - now_count * close_price[t]
                #print u"股票价格/持股数/剩余金额：",close_price[t], '/',  now_count, '/', now_money
                bBuySignal = False 
        elif dif_price[t] < dif_price[t-1] and dif_price[t] < dea_price[t] \
                        and dif_price[t-1] > dea_price[t-1] and dif_price[t] < 0:
            if bBuySignal == False:
                signal = SIGNAL_SALE
                now_money += now_count * close_price[t]
                now_count = 0
                #print u"股票价格/持股数/剩余金额：",close_price[t], '/',  now_count, '/', now_money
                bBuySignal = True      
        signals.append(signal)
        if signal != 0:
            #print 't:', str(stock_data.ix[t, 'Date']), '  signal:', signal
            tradeTimes += 1
            if (t<=len(close_price))and(t>=(len(close_price)-4)):
                currentSignal.append(['t:', str(stock_data.ix[t, 'Date']), '  signal:', signal])
    getmony = (now_money + now_count * close_price[-1] - start_money) / start_money
    over = (getmony - (close_price[-1] - close_price[ma_list[1]+1]) / close_price[ma_list[1]+1]) * 100
    print stockName[0],stockName[1], u"收益率：", getmony*100, '%\t'+ u'超收：',over,'%\t' \
        u"交易次数", tradeTimes, u" 最新市值：", now_money+now_count * close_price[-1]  ,str(Avg)
    stock_data['SIGNAL_MACD'] = signals
    return [(now_money+now_count * close_price[-1]-start_money)/start_money*100,currentSignal,tradeTimes,over]
#     fig = plt.figure(facecolor='white')
#     left, width = 0.1, 0.8
#     rect1 = [left, 0.5, width, 0.4]
#     rect2 = [left, 0.1, width, 0.3]
#     
#     axescolor  = '#f6f6f6'  # the axes background color
#     ax1 = fig.add_axes(rect1, axisbg=axescolor)  #left, bottom, width, height
#     ax2 = fig.add_axes(rect2, axisbg=axescolor, sharex=ax1)
#     
#     ax1.plot(range(len(close_price)), close_price, color="black", linewidth=1)
#     ax1.grid()
#     ax2.plot(range(len(dif_price)), ema_close_long,label='', color="red", linewidth=1)
#     ax2.plot(range(len(dea_price)), ema_close_short,label='', color="blue", linewidth=1)
#     ax2.grid()
    #plt.show()
    
    # 将数据按照交易日期从近到远排序
    #stock_data.sort('date', ascending=False, inplace=True)
 
    # return dif_price, dea_price, macd_price

# DMA指标择时 (回测）
def select_Time_DMA(stock_data, stockName,*Avg):
    AVR_SHORT = Avg[0]
    AVR_LONG = Avg[1]
    AVR_vLONG = Avg[2]
    start_money = 100000000
    now_count = 0
    now_money = start_money
    
    # 将数据按照交易日期从远到近排序
    # stock_data.sort('Date', inplace=True)
    close_price = stock_data['Adj Close'].get_values()
    
    #MA 
    ma_list = [AVR_SHORT, AVR_LONG,AVR_vLONG]
    ma_dea = Avg[2]#10
    ma_close_short = pd.rolling_mean(close_price, ma_list[0])
    ma_close_long = pd.rolling_mean(close_price, ma_list[1])
    ma_close_vlong = pd.rolling_mean(close_price, ma_list[2])

    dma_price = ma_close_short - ma_close_long
    ama_price = pd.rolling_mean(dma_price, ma_dea)
    
    signals = [0]*(ma_list[1]+1)
    tradeTimes = 0
    bBuySignal = True
    currentSignal=[]
    for t in range(ma_list[1]+1, len(close_price)):
        
        signal = SIGNAL_DEFAULT
        
        if dma_price[t] > dma_price[t-1] and dma_price[t] > ama_price[t] \
                                        and dma_price[t-1] < ama_price[t-1]:
            if bBuySignal:
                signal = SIGNAL_BUY
                now_count = (int)(now_money / close_price[t] /100)*100
                now_money = start_money - now_count * close_price[t]
                #print u"股票价格/持股数/剩余金额：",close_price[t], '/',  now_count, '/', now_money
                bBuySignal = False 
        elif dma_price[t] < dma_price[t-1] and dma_price[t] < ama_price[t] \
                        and dma_price[t-1] > ama_price[t-1]:
            if bBuySignal == False:
                signal = SIGNAL_SALE
                now_money += now_count * close_price[t]
                now_count = 0
                #print u"股票价格/持股数/剩余金额：",close_price[t], '/',  now_count, '/', now_money
                bBuySignal = True      
        signals.append(signal)
        if signal != 0:
            #print 't:', str(stock_data.ix[t, 'Date']), '  signal:', signal
            tradeTimes += 1
            if (t <= len(close_price)) and (t >= (len(close_price) - 4)):
                currentSignal.append(['t:', str(stock_data.ix[t, 'Date']), '  signal:', signal])

    print stockName[0],stockName[1], u"收益率：", (now_money+now_count * close_price[-1]-start_money)/start_money*100, '%\t' \
        u"交易次数", tradeTimes, u" 最新市值：", now_money+now_count * close_price[-1]  ,str(Avg)
    stock_data['SIGNAL_DMA'] = signals
    return [(now_money + now_count * close_price[-1] - start_money) / start_money * 100,currentSignal,tradeTimes]
#     fig = plt.figure(facecolor='white')
#     left, width = 0.1, 0.8
#     rect1 = [left, 0.5, width, 0.4]
#     rect2 = [left, 0.1, width, 0.3]
#     
#     axescolor  = '#f6f6f6'  # the axes background color
#     ax1 = fig.add_axes(rect1, axisbg=axescolor)  #left, bottom, width, height
#     ax2 = fig.add_axes(rect2, axisbg=axescolor, sharex=ax1)
#     
#     ax1.plot(range(len(close_price)), close_price, color="black", linewidth=1)
#     ax1.grid()
#     ax2.plot(range(len(dma_price)), dma_price,label='', color="red", linewidth=1)
#     ax2.plot(range(len(ama_price)), ama_price,label='', color="blue", linewidth=1)
#     ax2.grid()
    #plt.show()
    
    # 将数据按照交易日期从近到远排序
    #stock_data.sort('date', ascending=False, inplace=True)
 
# DMA指标择时 (回测）
def select_Time_TRIX(stock_data, stockName,*Avg):
    AVR_SHORT = Avg[0]
    AVR_LONG = Avg[1]
    start_money = 100000000
    now_count = 0
    now_money = start_money
    
    # 将数据按照交易日期从远到近排序
    # stock_data.sort('Date', inplace=True)
    close_price = stock_data['Adj Close'].get_values()
    
    #EMA 
    ma_list = [AVR_SHORT, AVR_SHORT] #N,M
    
    ema_close = pd.ewma(close_price, span=ma_list[0])
    ema_close = pd.ewma(ema_close, span=ma_list[0])
    tr_close = pd.ewma(ema_close, span=ma_list[0])
    
    trixsList = [0]
    for i in range(1, len(tr_close)):
        #print tr_close[i], tr_close[i-1]
        trix = (tr_close[i]-tr_close[i-1])/tr_close[i-1]*100
        trixsList.append(trix)
    trixs = np.array(trixsList)    
    maxtrix = pd.rolling_mean(trixs, ma_list[1])

    signals = [0]*(ma_list[1]+1)
    tradeTimes = 0
    bBuySignal = True
    currentSignal=[]
    for t in range(ma_list[1]+1, len(close_price)):
        
        signal = SIGNAL_DEFAULT
        if trixs[t] > trixs[t-1] and trixs[t] > maxtrix[t] \
                                        and trixs[t-1] < maxtrix[t-1]:
            if bBuySignal:
                signal = SIGNAL_BUY
                now_count = (int)(now_money / close_price[t] /100)*100
                now_money = start_money - now_count * close_price[t]
                #print u"股票价格/持股数/剩余金额：",close_price[t], '/',  now_count, '/', now_money
                bBuySignal = False 
        elif trixs[t] < trixs[t-1] and trixs[t] < maxtrix[t] \
                        and trixs[t-1] > maxtrix[t-1]:
            if bBuySignal == False:
                signal = SIGNAL_SALE
                now_money += now_count * close_price[t]
                now_count = 0
                #print u"股票价格/持股数/剩余金额：",close_price[t], '/',  now_count, '/', now_money
                bBuySignal = True      
        signals.append(signal)
        if signal != 0:
            #print 't:', str(stock_data.ix[t, 'Date']), '  signal:', signal
            tradeTimes += 1
            if (t <= len(close_price)) and (t >= (len(close_price) - 4)):
                currentSignal.append(['t:', str(stock_data.ix[t, 'Date']), '  signal:', signal])

    print stockName[0],stockName[1], u"收益率：", (now_money+now_count * close_price[-1]-start_money)/start_money*100, '%\t' \
        u"交易次数", tradeTimes, u" 最新市值：", now_money+now_count * close_price[-1]  ,str(Avg)
    stock_data['SIGNAL_TRIX'] = signals
    return [(now_money + now_count * close_price[-1] - start_money) / start_money * 100,currentSignal,tradeTimes]

# 组合择时指标 (回测）
def select_Time_Mix(stock_data, stockName,*Avg):
    AVR_SHORT = Avg[0]
    AVR_LONG = Avg[1]
    start_money = 100000000
    now_count = 0
    now_money = start_money
    
    # 综合策略
    signals = []
    tradeTimes = 0
    bBuySignal = True 
    
    close_price = stock_data['Adj Close'].get_values()
    s_ma = stock_data['SIGNAL_MA'].get_values()
    s_macd = stock_data['SIGNAL_MACD'].get_values()
    s_dma = stock_data['SIGNAL_DMA'].get_values()
    s_trix = stock_data['SIGNAL_TRIX'].get_values()
    
    for i in range(len(s_ma)):
        
        signal = SIGNAL_DEFAULT
        
        up = 0; 
        down = 0;
        if s_ma[i] == 1:
            up += 1
        elif s_ma[i] == -1:
            down += 1
        
        if s_macd[i] == 1:
            up += 1
        elif s_macd[i] == -1:
            down += 1
        
        if s_dma[i] == 1:
            up += 1
        elif s_dma[i] == -1:
            down += 1
        
        if s_trix[i] == 1:
            up += 1
        elif s_trix[i] == -1:
            down += 1            

        if up >= 3:
            if bBuySignal:
                signal = SIGNAL_BUY
                now_count = (int)(now_money / close_price[i] /100)*100
                now_money = start_money - now_count * close_price[i]
                #print u"股票价格/持股数/剩余金额：",close_price[t], '/',  now_count, '/', now_money
                bBuySignal = False 
        elif down <= -3:   
            if bBuySignal == False:
                signal = SIGNAL_SALE
                now_money += now_count * close_price[i]
                now_count = 0
                #print u"股票价格/持股数/剩余金额：",close_price[t], '/',  now_count, '/', now_money
                bBuySignal = True 
        
        signals.append(signal)
        if signal != 0:
            #print 't:', t, '  signal:', signal
            tradeTimes += 1
                
    print stockName[0],stockName[1], u"收益率：", (now_money+now_count * close_price[-1]-start_money)/start_money*100, '%\t' \
        u"交易次数", tradeTimes, u" 最新市值：", now_money+now_count * close_price[-1]  
    stock_data['SIGNAL_MIX'] = signals
    return (now_money + now_count * close_price[-1] - start_money) / start_money * 100
# AMA指标择时
def select_Time_AMA(stock_data, stockName,*Avg):
    AVR_SHORT = Avg[0]
    AVR_LONG = Avg[1]
    percentage = 0.1
    
    start_money = 100000000
    now_count = 0
    now_money = 0
    one_hand = 10000
    
    # 将数据按照交易日期从远到近排序
    # stock_data.sort('Date', inplace=True)
    
    close_price = stock_data['Adj Close'].get_values()
    
    # 指数平滑序列
    containts = [0]*10
    for i in range(10, len(close_price)):
        sub_price = close_price[i-10:i]
        constaint = getConstaint(sub_price)
        containts.append(constaint);
        
    ama_price = [close_price[0]]    
    for i in range(1, len(close_price)):
        ama = containts[i-1] * close_price[i-1] + (1-containts[i-1])*ama_price[i-1]
        ama_price.append(ama)
        
    signals = [0]*21
    tradeTimes = 0
    
    record_buy = 0
    record_sale = []
        
    # 从20天以后开始判断买卖点
    for i in range(21, len(ama_price)):
        signal = SIGNAL_DEFAULT
        #print np.array(ama_price[i-19:i+1]) - np.array(ama_price[i-20:i])
        threshold = percentage * np.std(np.array(ama_price[i-19:i+1]) - np.array(ama_price[i-20:i])) # 过滤器
        
        if ama_price[i] - np.min(ama_price[i-5:i]) > threshold: 
            signal = SIGNAL_BUY
            now_count += one_hand
            record_buy += one_hand * close_price[i]
            #print u"股票价格/持股数/剩余金额：",close_price[t], '/',  now_count, '/', now_money
        elif np.max(ama_price[i-5:i]) - ama_price[i] > threshold:    
            signal = SIGNAL_SALE
            if now_count > one_hand:
                now_count -= one_hand
                record_sale = one_hand * close_price[i]
            #print u"股票价格/持股数/剩余金额：",close_price[t], '/',  now_count, '/', now_money
        signals.append(signal)
        if signal != 0:
            # print 't:',  str(stock_data.ix[i, 'Date']), '  signal:', signal
            tradeTimes += 1           

    # 成本
    # print stockName[0],stockName[1],u'盈利', record_sale + now_count * close_price[-1] - record_buy
    
    print stockName[0],stockName[1], u"收益率：", (now_money+now_count * close_price[-1]-start_money)/start_money*100, '%\t' \
        u"交易次数", tradeTimes, u" 最新市值：", now_money+now_count * close_price[-1]  ,str(Avg)
    stock_data['SIGNAL_AMA'] = signals
    # return ama_price
    return (now_money + now_count * close_price[-1] - start_money) / start_money * 100

# 获取平方平滑系数
def getConstaint(prices):
    direction = abs(prices[-1] - prices[0])
    volatility = sum(abs(prices[i+1]-prices[i]) for i in range(len(prices)-1))
    ER = abs(direction/volatility)   
    fastSC = 2.0/(2.0+1)
    slowSC = 2.0/(30.0+1)
    sSC = ER * (fastSC-slowSC) + slowSC
    constaint = sSC*sSC 
    return constaint

# 选择一种均线策略
def getMAStrategy(stockCsvPath, stockName, strategyName='MACD'):
    if os.path.exists(stockCsvPath) == False:
        return
    stock_data = pd.read_csv(stockCsvPath)
    if strategyName == 'MACD':
        return select_Time_MACD(stock_data, stockName)
    elif strategyName == 'MA':
        return select_Time_MA(stock_data, stockName)
    elif strategyName == 'DMA':
        return select_Time_DMA(stock_data, stockName)
    elif strategyName == 'TRIX':
        return select_Time_TRIX(stock_data, stockName)
    elif strategyName == 'AMA':
        return select_Time_AMA(stock_data, stockName)

def Grid_Constructor(numline,numParm,data):
    alleles = GAllele.GAlleles()
    for i in range(0, numline*numParm):
        alleles.add(GAllele.GAlleleRange(data[i][0], data[i][1]))
    return alleles

def func(fitness,strategyName,stock_data, stockName):
    def fitness_function(chromosome):
        score = 0.0
        if fitness == 'abs':
            if strategyName == 'MACD':
                score = select_Time_MACD(stock_data, stockName, *chromosome)[0]
            elif strategyName == 'MA':
                score = select_Time_MA(stock_data, stockName, *chromosome)[0]
            elif strategyName == 'DMA':
                score = select_Time_DMA(stock_data, stockName, *chromosome)[0]
            elif strategyName == 'TRIX':
                score = select_Time_TRIX(stock_data, stockName, *chromosome)[0]
            elif strategyName == 'AMA':
                score = select_Time_AMA(stock_data, stockName, *chromosome)
        return score
    return fitness_function
def cal_opt(numParm,fintness,strategyName,func,stock_data, stockName):
    if (strategyName == 'MACD' or strategyName == 'DMA')and 'Low' in stock_data.columns:
        datarange = [[8, 15], [21, 31], [6, 12]]
    elif (strategyName == 'MACD' or strategyName == 'DMA')and 'Low' not in stock_data.columns:
        datarange = [[3, 20], [21, 41], [5, 20]]
    else:
        datarange=[[2,5],[6,19],[7,60]]
    datarange=datarange[:numParm]
    genome = G1DList.G1DList(numParm)
    genome.evaluator.set(func(fintness,strategyName,stock_data, stockName))
    # genome.setParams(allele=Grid_Constructor(numline,data1))
    genome.setParams(allele=Grid_Constructor(1,numParm,datarange))
    genome.initializator.set(Initializators.G1DListInitializatorAllele)
    genome.mutator.set(Mutators.G1DListMutatorAllele)

    ga = GSimpleGA.GSimpleGA(genome, seed=400)
    ga.setPopulationSize(40)
    ga.setGenerations(40)
    ga.setCrossoverRate(0.8)
    ga.setMutationRate(0.18)
    ga.selector.set(Selectors.GRankSelector)
    # ga.terminationCriteria.set(GSimpleGA.FitnessStatsCriteria)
    # Change the scaling method
    pop = ga.getPopulation()
    pop.scaleMethod.set(Scaling.SigmaTruncScaling)
    ga.evolve(freq_stats=10)
    best = ga.bestIndividual()
    return [best.genomeList,round(best.score,5)]
# 执行策略 
def run(stockCsvPath, stockName):
    if os.path.exists(stockCsvPath) == False:
        return
    stockCsvNewPath = stockName + '_macd.csv'
    processEMA(stockCsvPath, stockCsvNewPath)
    stock_data = pd.read_csv(stockCsvPath)
    self_adaptive_ma(stock_data)
    
    print u'>>>>>>>>>>>>> MA 策略 >>>>>>>>>>>>>>>>>>>>>>>>>>'
    select_Time_MA(stock_data, stockName)
       
    print u'>>>>>>>>>>>>> MACD 策略 >>>>>>>>>>>>>>>>>>>>>>>>>>'
    select_Time_MACD(stock_data, stockName)
   
    print u'>>>>>>>>>>>>> DMA 策略 >>>>>>>>>>>>>>>>>>>>>>>>>>'
    select_Time_DMA(stock_data, stockName)
       
    print u'>>>>>>>>>>>>> TRIX 策略 >>>>>>>>>>>>>>>>>>>>>>>>>>'
    select_Time_TRIX(stock_data, stockName)
      
    print u'>>>>>>>>>>>>> 组合策略 >>>>>>>>>>>>>>>>>>>>>>>>>>'
    select_Time_Mix(stock_data, stockName)
   
    print u'>>>>>>>>>>>>> AMA策略 >>>>>>>>>>>>>>>>>>>>>>>>>>'
    select_Time_AMA(stock_data, stockName)
            
    print '\n'
def match(select_method,stockName,lines):
    contmatch=[]
    for line in lines:
        if line != '\n':
            # print str(line.split('|'))
            if(stockName[0] == line.split('|')[1])and(select_method == line.split('|')[0]):
                contmatch.append([line.split('|')[0],line.split('|')[3]])
    return contmatch
def macdmain(stockName,fundlist):
    print "main begin"
    # stockList = ['000725', '000783', '002167', '002505', '002600', '300315', '600000', '600011', '600048', '601001']
    # downloadAllHistoryAShareData(stockList)
    # stockList = ['000725']
    buysell=[]
    # for stockName in stockList:
    # if stockName != '002600':
    #     continue
    # stockCsvPath = os.path.pardir + "\\stockdata\\" + stockName + '.csv'
    # stockCsvPath = stockName + '.csv'
    # if os.path.exists(stockCsvPath) == False:
    #     continue
    # stockCsvNewPath = stockName + '_macd.csv'
    # processEMA(stockCsvPath, stockCsvNewPath)
    # stock_data = pd.read_csv(stockCsvPath)
    stockTxtNewPath = "./stockdata/"+ 'GAOpt100.txt'
    # fundlist = efund_mail2.get_histrydata(stockName, 180)
    stock_data = pd.DataFrame(fundlist[:200][::-1], columns=['Date', 'Adj Close', 'countclose', 'change'])
    # self_adaptive_ma(stock_data)
    period_type = 'w'
    stock_data = stock_data.resample(period_type,how='last')
    #stock_data = 

    Avg1=([3,8,40])
    # select_method=['MA','MACD','DMA','TRIX','AMA']
    select_method = ['MA','MACD']
    AvgParm=[]
    cal=''
    for i in select_method:
        file_to_read=open(stockTxtNewPath, 'r')
        lines = file_to_read.readlines()  # 整行读取数据
        if not lines:
            break
            pass
        else:
            contmatch=match(i,stockName,lines)
            if (cal=='new')and(len(contmatch)==0):
                best=cal_opt(3, 'abs', i, func, stock_data, stockName)
                # AvgParm.append(best)
                f = open(stockTxtNewPath, 'a')
                f.write(str(i)+'|')
                f.write(str(stockName[0])+'|'+stockName[1].encode('gb2312')+'|')
                f.write(str(best[0]).split('[')[1].split(']')[0]+'|'+str(best[1]))
                f.write('\n')
                f.close()
                Avg = best[0]
            if len(contmatch)!=0:
                Avg = [int(contmatch[0][1].split(',')[0]),int(contmatch[0][1].split(',')[1]),int(contmatch[0][1].split(',')[2])]
            elif (len(contmatch)==0)and(i != 'MA'):
                Avg = ([12, 26, 9])
            elif (len(contmatch)==0)and(i == 'MA'):
                Avg = ([3, 8, 44])
        result=None
        if(i=='MA'):
            print u'-- MA 策略 --'
            result=select_Time_MA(stock_data, stockName,*Avg)
            if(len(result[1])):
                buysell.append([stockName,i,result])
        if (i == 'MACD'):
            print u'-- MACD 策略 --'
            result=select_Time_MACD(stock_data, stockName, *Avg)
            if (len(result[1])):
                buysell.append([stockName, i, result])
        if (i == 'DMA'):
            print u'-- DMA 策略 --'
            result=select_Time_DMA(stock_data, stockName,*Avg)
            if (len(result[1])):
                buysell.append([stockName, i, result])
        if (i == 'TRIX'):
            print u'-- TRIX 策略 -->'
            result=select_Time_TRIX(stock_data, stockName,*Avg)
            if (len(result[1])):
                buysell.append([stockName, i, result])

        # print u'-- 组合策略 --'
        # select_Time_Mix(stock_data, stockName,*Avg)
        #
        # print u'-- AMA策略 --'
        # select_Time_AMA(stock_data, stockName,*Avg)
    # print '\n'
    print "main end"
    return buysell
def mainStock():
    file = {'stockcodewangyiShangz.txt': 0,
            'stockcodewangyiShenz.txt': 1}  # 'stockcodewangyiqdii.txt':'','stockcodewangyidetail.txt':''
    buysell=[]
    stockTxtNewPath = "./stockdata/" + 'GAOpt100.txt'
    stockTxtNewPath = "./stockdata/" + 'GAOpt100.txt'
    for jj in file:
        CodeList = []
        stockTxtNewPath1 =  "./stockdata/" + jj  #r'E:\03IT\GitHub\stock-2' +
        file_to_read = open(stockTxtNewPath1, 'r')
        lines = file_to_read.readlines()  # 整行读取数据
        if not lines:
            pass
        else:
            for line in lines:
                if line != '\n' and line != ' ':
                    if jj == 'stockcodewangyidetail.txt':
                        icode = line.split(' ')
                    else:
                        icode = line.split('\t')
                    CodeList.append([icode[1],icode[2].decode('gbk')])
        # 抓取数据并保存到本地csv文件
        for stockName in CodeList:
            if not ' ' in stockName[0]:
                # stockCsvPath = r'E:\03IT\GitHub\stock-2' + "\\stockdata\\dongfangcf\\" + stockName[0] + '.csv'
                stockCsvPath=downlaodDataBycode(stockName[0],jj)
                # stockCsvPath = stockName + '.csv'
                if os.path.exists(stockCsvPath) == False:
                    continue
                else:
                    stockCsvNewPath = stockName[0] + '.csv'
                    # processEMA(stockCsvPath, stockCsvNewPath)
                    stock_data = pd.read_csv(stockCsvPath,encoding="gb2312")
                    if len(stock_data)<3:
                        continue
                    else:
                        columns1 = ['Date', 'Adj Close', 'High', 'Low']
                        stock_data = pd.DataFrame(stock_data.loc[:,[u'日期', u'收盘价', u'最高价', u'最低价']], columns=['日期', '收盘价', '最高价', '最低价'])
                        stock_data.columns=columns1
                        stock_data['Date'] = pd.to_datetime(stock_data['Date'])
                        stock_data=pd.DataFrame(stock_data.values[::-1],columns=columns1)
                        select_method = ['MA', 'MACD']
                        cal = ''
                        for i in select_method:
                            file_to_read = open(stockTxtNewPath, 'r')
                            lines = file_to_read.readlines()  # 整行读取数据
                            if not lines:
                                contmatch =[]
                            else:
                                contmatch = match(i, stockName, lines)
                            if (cal == 'new') or (len(contmatch) == 0):
                                best = cal_opt(3, 'abs', i, func, stock_data, stockName)
                                # AvgParm.append(best)
                                f = open(stockTxtNewPath, 'a')
                                f.write(str(i) + '|')
                                f.write(str(stockName[0]) + '|' + stockName[1].encode('gbk') + '|')
                                f.write(str(best[0]).split('[')[1].split(']')[0] + '|' + str(best[1]))
                                f.write('\n')
                                f.close()
                            Avg = ([2, 8, 40])#best[0]
                            if len(contmatch) != 0:
                                Avg = [int(contmatch[0][1].split(',')[0]), int(contmatch[0][1].split(',')[1]),
                                       int(contmatch[0][1].split(',')[2])]
                            elif (len(contmatch) == 0) and (i != 'MA'):
                                Avg = ([12, 26, 9])
                            elif (len(contmatch) == 0) and (i == 'MA'):
                                Avg = ([2, 8, 40])
                            result = None
                            if (i == 'MA'):
                                print u'-- MA 策略 --'
                                result = select_Time_MA(stock_data, stockName, *Avg)
                                # self_adaptive_ma(stock_data, Avg)
                                if (len(result[1])):
                                    buysell.append([stockName, i, result])
                            if (i == 'MACD'):
                                print u'-- MACD 策略 --'
                                result = select_Time_MACD(stock_data, stockName, *Avg)
                                if (len(result[1])):
                                    buysell.append([stockName, i, result])
                            if (i == 'DMA'):
                                print u'-- DMA 策略 --'
                                result = select_Time_DMA(stock_data, stockName, *Avg)
                                if (len(result[1])):
                                    buysell.append([stockName, i, result])
                            if (i == 'TRIX'):
                                print u'-- TRIX 策略 -->'
                                result = select_Time_TRIX(stock_data, stockName, *Avg)
                                if (len(result[1])):
                                    buysell.append([stockName, i, result])

                                    # print u'-- 组合策略 --'
                                    # select_Time_Mix(stock_data, stockName,*Avg)
                                    #
                                    # print u'-- AMA策略 --'
                                    # select_Time_AMA(stock_data, stockName,*Avg)
                        print '\n'
    print "main end"
    return buysell
if __name__ == "__main__":
    print "main begin"
    buysellstock= mainStock()
    print buysellstock
    stockList=['000725','000783','002167','002505','002600','300315','600000','600011','600048','601001']
    # downloadAllHistoryAShareData(stockList)
    for stockName in stockList:
        stockCsvPath = os.path.pardir +"\\stockdata\\" + stockName + '.csv'
        #stockCsvPath = stockName + '.csv'
        if os.path.exists(stockCsvPath) == False:
            continue
        #stockCsvNewPath = stockName + '_macd.csv'
        #processEMA(stockCsvPath, stockCsvNewPath)
        stock_data = pd.read_csv(stockCsvPath)
        #self_adaptive_ma(stock_data)
        Avg=[5,10,40]   
        print u'-- MA 策略 --'
        select_Time_MA(stock_data, stockName,Avg)

        print u'-- MACD 策略 --'
        select_Time_MACD(stock_data, stockName,Avg)

        print u'-- DMA 策略 --'
        select_Time_DMA(stock_data, stockName,Avg)

        print u'-- TRIX 策略 -->'
        select_Time_TRIX(stock_data, stockName,Avg)

        print u'-- 组合策略 --'
        select_Time_Mix(stock_data, stockName,Avg)

        print u'-- AMA策略 --'
        select_Time_AMA(stock_data, stockName,Avg)
                
        print '\n'
    print "main end"    
