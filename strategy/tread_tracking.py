#!/usr/local/bin/python
#coding=utf-8
# 趋势追踪策略

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from util.stockutil import getSixDigitalStockCode
from data_process.get_data_center import get_stock_k_line

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
    print ma_short
    
     
    SIGNAL_BUY = 1  #买 
    SIGNAL_SALE = -1 #卖
    SIGNAL_DEFAULT = 0
    
    signal = SIGNAL_SALE
        
    print '交易开始'
        
    # 判断极点
    min_index_pre = 0 #前一个极小值
    max_index_pre = 0 #前一个极大值
    for i in range(prama_ma_short+1, len(ma_short)-1):
        if ma_short[i] > ma_short[i-1] and ma_short[i] > ma_short[i+1]:
            #print '极大值:', ma_short[i], 'pos:', i
            if max_index_pre > 0 and ma_short[i] < ma_short[max_index_pre] and signal == SIGNAL_BUY:
                signal = SIGNAL_SALE
                print '卖出:', ma_short[i], 'pos:', i
            max_index_pre = i
        elif ma_short[i] < ma_short[i-1] and ma_short[i] < ma_short[i+1]: 
            #print '极小值:', ma_short[i], 'pos:', i
            if min_index_pre > 0 and ma_short[i] > ma_short[min_index_pre] and signal == SIGNAL_SALE:
                signal = SIGNAL_BUY
                print '买入:', ma_short[i], 'pos:', i
            min_index_pre = i
            
    print '交易结束'        
            
    
if __name__ == "__main__":
    tread_track('000001')        