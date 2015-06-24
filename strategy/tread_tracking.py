#!/usr/local/bin/python
#coding=utf-8
# 趋势追踪策略

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from util.stockutil import getSixDigitalStockCode
from data_process.get_data_center import get_stock_k_line
from scipy.ndimage.measurements import extrema

# 参数
# code：股票代码
# df: 个股的K线数据
def tread_track(code, df=None):
    if df == None:
        code = getSixDigitalStockCode(code)
    df = get_stock_k_line(code)
    df = df.reindex(df.index[::-1])
    #print df
    
    #参数
    prama_ma_short = 15 # 短均线
    prama_ma_long = 180 # 长均线
    filter_range = 0.004 # 滤波区间
    drift = 0.0015 #漂移项
    param_big_band = 0.02 #大波段判断条件
    protect_big_band = 0.002 # 大波段保护止赢点
    
    
    ma_short = pd.rolling_mean(df['close'], prama_ma_short)
    ma_long  = pd.rolling_mean(df['close'], prama_ma_long)
    #print ma_short
    
     
    SIGNAL_BUY = 1  #买 
    SIGNAL_SALE = -1 #卖
    SIGNAL_DEFAULT = 0
    
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
    
    plt.plot(df.index, ma_short.get_values(), label=code, color="r", linewidth=1)
    
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
    
    
    
    for i in range(prama_ma_short+1, len(ma_short)-1):
        
        #滤波后的均线走平时（即处于滤波区间内），将其识别为一个点
        index_post = i+1
        while(ma_short[index_post] == ma_short[i] and index_post < len(ma_short)-1):
            index_post += 1
        
        # 高低点比较策略
        if ma_short[i] > ma_short[i-1] and ma_short[i] > ma_short[index_post]:
            #print '极大值:', ma_short[i], 'pos:', i
            if max_index_pre > 0 and ma_short[i] < ma_short[max_index_pre] + drift*(i-max_index_pre) and signal == SIGNAL_BUY:
                signal = SIGNAL_SALE
                print '卖出:', ma_short[i], 'pos:', i
                count_sale += 1
                total += ma_short[i] - price_buy
            max_index_pre = i
        elif ma_short[i] < ma_short[i-1] and ma_short[i] < ma_short[index_post]: 
            #print '极小值:', ma_short[i], 'pos:', i
            if min_index_pre > 0 and ma_short[i] > ma_short[min_index_pre] + drift*(i-min_index_pre)  and signal == SIGNAL_SALE:
                signal = SIGNAL_BUY
                print '买入:', ma_short[i], 'pos:', i
                count_buy += 1
                price_buy = ma_short[i]
                if price_init == 0:
                    price_init = price_buy
            min_index_pre = i
        
        # 高低点突破策略    
        # 股价突破前一个低点加漂移项，则卖出
        elif signal == SIGNAL_BUY and min_index_pre > 0 and \
                ma_short[i] < ma_short[min_index_pre] + drift*(i-min_index_pre):
            signal = SIGNAL_SALE
            print '卖出:', ma_short[i], 'pos:', i
            count_sale += 1
            total += ma_short[i] - price_buy
        # 股价突破前一个高点加漂移项，则买入    
        elif signal == SIGNAL_SALE and max_index_pre > 0 and \
                ma_short[i] > ma_short[max_index_pre] + drift*(i-max_index_pre):    
            signal = SIGNAL_BUY
            print '买入:', ma_short[i], 'pos:', i
            count_buy += 1
            price_buy = ma_short[i]

        # 大波段保护策略
        elif min_index_pre > 0 and ma_short[i] >= ma_short[min_index_pre]*(1+param_big_band):
            keep_stop_price = ma_short[i] * (1-protect_big_band) #止损位
            keep_stop_index = i
        elif signal == SIGNAL_BUY and keep_stop_price > 0 and \
                 ma_short[i] < keep_stop_price + drift*(i-keep_stop_index):    
            signal = SIGNAL_SALE
            print '卖出:', ma_short[i], 'pos:', i
            count_sale += 1
            total += ma_short[i] - price_buy
            
    print "buy count:", count_buy
    print "sale count:", count_sale
    print "每股盈利：", total, "收益率：", (total+price_init)/price_init*100,"%"
    print '交易结束'        
            
    plt.grid()
    #plt.legend()
    #plt.show()
    
if __name__ == "__main__":
    tread_track('600000')        