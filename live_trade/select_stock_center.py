#!/usr/local/bin/python3
#coding=utf-8
#量化选股中心

import tushare as ts
import os
import pandas as pd
import util.commons as cm
from multiprocessing.dummy import Pool as ThreadPool
from data_process.get_data_center import get_stock_k_line

def select_stock_from_all_stocks():
    print '>>>开始筛选所有A股'
    try:
        df = pd.read_csv(cm.DownloadDir + cm.TABLE_STOCKS_BASIC + '.csv')
        code_list = df['code'].get_values();
        #se = df.loc[int(code)]
        #se = df.ix[code]
        pool = ThreadPool(processes=10)
        #pool.map(download_stock_kline, df.index)
        pool.close()
        pool.join()  
            
    except Exception as e:
        print str(e)
        
    print '>>>结束筛选所有A股'
 
  
def evaluation_stock(code):
    # 以上一交易日的收盘价为判断点
    
    try:
        print 'evaluation', code, 'begin'
        df = get_stock_k_line(code)
        maStrategy = MACD_LIVE_TEST.MAStrategy(cm.DownloadDir + fileName, stock)
        #se = df.loc[int(code)]
        #se = df.ix[int(code)]
        #return se
    except Exception as e:
        print str(e)
            
    #download_stock_kline
    #
    
#     stockClassList = OnlineData.getLiveMutliChinaStockPrice(stock_list)
#     for stock in stockClassList:
#         
#         
#         try:
#             # 多线程提醒实时买卖
#             if float(stock.current) == 0.0:
#                 print '>>>', stock.name,'>>>停牌!',  stock.close, stock.time
#                 continue
#             
#             
#             
#             fileName = 'h_kline_' + str(stock.code) + '.csv'
#             maStrategy = MACD_LIVE_TEST.MAStrategy(cm.DownloadDir + fileName, stock)
#             signal = maStrategy.select_Time_Mix()
#             if signal > 0:
#                 #print stock.name, stock.current, (float(stock.current)-float(stock.close))/float(stock.close)*100, '%'
#                 print '>' * 5, 'Buy now!', stock.name, stock.current, stock.time
#                 #Mbox('Buy now!' , '%s %s %s' % (stock.code, stock.current, stock.time), 1)
#             elif signal < 0:     
#                 #print stock.name, stock.current, (float(stock.current)-float(stock.close))/float(stock.close)*100, '%'
#                 print '>' * 5, 'Sale now!', stock.name, stock.current, (float(stock.current)-float(stock.close))/float(stock.close)*100, '%', stock.time
#                 #Mbox('Sale now!' , '%s %s %s' % (stock.code, stock.current, stock.time), 1)
#             else:
#                 print stock.name, stock.current, (float(stock.current)-float(stock.close))/float(stock.close)*100, '%'
#                 #print 'No Operatin!', stock.name, stock.time
#         except Exception as e:
#             print stock.name, str(e)
#             None
#         finally:
#             None    

main()  