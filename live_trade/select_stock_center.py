#!/usr/local/bin/python3
#coding=utf-8
#量化选股中心

import tushare as ts
import datetime
import pandas as pd
import util.commons as cm
from multiprocessing.dummy import Pool as ThreadPool
from data_process.get_data_center import *
import strategy.macd_live_test as MACD_LIVE_TEST
from util.stockutil import getSixDigitalStockCode

stock_buy_list = []
stock_sale_list = []

def select_stock_from_all_stocks():
    print '>>>开始筛选所有A股'
    try:
        df = pd.read_csv(cm.DownloadDir + cm.TABLE_STOCKS_BASIC + '.csv')
        code_all_list = df['code'].get_values();
        #过滤停牌的股票
        code_list = code_all_list
        
        pool = ThreadPool(processes=10)
        pool.map(evaluation_stock, code_list)
        pool.close()
        pool.join()  
            
    except Exception as e:
        print str(e)
        
    print '>>>结束筛选所有A股'
 
  
def evaluation_stock(code):
    # 以上一交易日的收盘价为判断点
    
    try:
        #print 'evaluation', getSixDigitalStockCode(code), 'begin'
        date_end = datetime.date.today() + datetime.timedelta(-3)
        df = get_stock_k_line(code)
        if df is None:
            return
        else:
            nearest_date = df.head(1)['date']
            print nearest_date
            if str(nearest_date) != date_end:
                return
        if len(df.index) > 30:
        
            maStrategy = MACD_LIVE_TEST.MAStrategy(df=df)
            signal = maStrategy.select_Time_Mix()
            if signal > 0:
                #print stock.name, stock.current, (float(stock.current)-float(stock.close))/float(stock.close)*100, '%'
                print '>' * 5, 'Buy now!', getSixDigitalStockCode(code)
                stock_buy_list.append(getSixDigitalStockCode(code))
            elif signal < 0:     
                #print stock.name, stock.current, (float(stock.current)-float(stock.close))/float(stock.close)*100, '%'
                print '>' * 5, 'Sale now!', getSixDigitalStockCode(code)
                stock_sale_list.append(getSixDigitalStockCode(code))
    except Exception as e:
        print str(e)

if __name__ == "__main__":
    select_stock_from_all_stocks()  
    #evaluation_stock('000001')
    
    
    print '买入:'
    for code in stock_buy_list:
        stockInfo = get_stock_info(code)
        print 'Buy:', code, stockInfo['name']

    print '\n卖出:'
    for code in stock_sale_list:
        stockInfo = get_stock_info(code)
        print 'Sale:', code, stockInfo['name']