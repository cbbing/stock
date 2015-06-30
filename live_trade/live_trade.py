#!/usr/local/bin/python3
#coding=utf-8

import os
import data_process.online_data as OnlineData
import strategy.macd_live_test as MACD_LIVE_TEST
from time import sleep
import time
import ctypes
from util.stockutil import fn_timer as fn_timer_
from data_process.get_data_center import *
from multiprocessing.dummy import Pool as ThreadPool


# 监听股票列表
stock_list = ['600000','600048', '600011', '002600', '002505', '000725', '000783', '300315', '002167', '601001']
#stock_list =['601001']

stock_buy_list = []
stock_sale_list = []


def main():
    # 获取实时股价
    #stockClassList = OnlineData.getLiveMutliChinaStockPrice(stock_list)
    stockClassList =OnlineData.getAllChinaStock()
    live_mult_stock(stockClassList)
    
@fn_timer_            
def live_mult_stock(stockClassList):  
    pool = ThreadPool(processes=20)
    pool.map(live_single_stock, stockClassList)
    pool.close()
    pool.join()    
    
#     for stock in stockClassList:
#         live_single_stock(stock)   

def live_single_stock(stock):
    try:
        # 多线程提醒实时买卖
        if float(stock.current) == 0.0:
            print '>>>', stock.name,'>>>停牌!',  stock.close, stock.time
            return
        
        fileName = 'h_kline_' + str(stock.code) + '.csv'
        maStrategy = MACD_LIVE_TEST.MAStrategy(cm.DownloadDir + fileName, stock)
        signal = maStrategy.select_Time_Mix()
        if signal > 0:
            #print stock.name, stock.current, (float(stock.current)-float(stock.close))/float(stock.close)*100, '%'
            print '>' * 5, 'Buy now!', stock.name, stock.current
            stock_buy_list.append(getSixDigitalStockCode(stock.code))
            #Mbox('Buy now!' , '%s %s %s' % (stock.code, stock.current, stock.time), 1)
        elif signal < 0:     
            #print stock.name, stock.current, (float(stock.current)-float(stock.close))/float(stock.close)*100, '%'
            #print '>' * 5, 'Sale now!', stock.name, stock.current, (float(stock.current)-float(stock.close))/float(stock.close)*100, '%'
            stock_sale_list.append(getSixDigitalStockCode(stock.code))
            #Mbox('Sale now!' , '%s %s %s' % (stock.code, stock.current, stock.time), 1)
        #else:
            #print stock.name, stock.current, (float(stock.current)-float(stock.close))/float(stock.close)*100, '%'
            #print 'No Operatin!', stock.name, stock.time
    except Exception as e:
        print stock.name, str(e)
        None
    finally:
        None

##  Styles:
##  0 : OK
##  1 : OK | Cancel
##  2 : Abort | Retry | Ignore
##  3 : Yes | No | Cancel
##  4 : Yes | No
##  5 : Retry | No 
##  6 : Cancel | Try Again | Continue
def Mbox(title, text, style):
    ctypes.windll.user32.MessageBoxA(0, text, title, style)
    

 
if __name__ == "__main__":
    print ">>live trade begin"
    
    while(True):
        
        
        
        print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        main()
        print '\n'
        
        print '买入:'
        for code in stock_buy_list:
            stockInfo = get_stock_info(code)
            print 'Buy:', code, stockInfo['name']
    
        print '\n卖出:'
        for code in stock_sale_list:
            stockInfo = get_stock_info(code)
            print 'Sale:', code, stockInfo['name']
        break
        sleep(30) #2s
    
    print ">>live trade end"
    