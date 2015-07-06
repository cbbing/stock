#!/usr/local/bin/python3
#coding=utf-8

import time,sched,os
import data_process.online_data as OnlineData
import strategy.macd_live_test as MACD_LIVE_TEST
from time import sleep
import ctypes
from util.stockutil import fn_timer as fn_timer_
from data_process.get_data_center import *
from multiprocessing.dummy import Pool as ThreadPool


# 监听股票列表
stock_list = ['600000','600048', '600011', '002600', '002505', '000725', '000783', '300315', '002167', '601001',\
              '600893', '000020']
#stock_list =['600893']

stock_buy_list = []
stock_sale_list = []


def main():
    # 获取实时股价
    #stockClassList = OnlineData.getLiveMutliChinaStockPrice(stock_list)
    stockClassList =OnlineData.getAllChinaStock()
    #stockClassList =OnlineData.getAllChinaStock2()
    print '获取股票总数：',len(stockClassList)
    live_mult_stock(stockClassList)
    
           
def live_mult_stock(stockClassList):  
#     pool = ThreadPool(processes=4)
#     pool.map(live_single_stock, stockClassList)
#     pool.close()
#     pool.join()    
    for stock in stockClassList:
        live_single_stock(stock) 
          

def live_single_stock(stock):
    try:
        # 多线程提醒实时买卖
        if float(stock.current) == 0.0:
            print '>>>', stock.name,'>>>停牌!',  stock.close, stock.time
            return
        
        fileName = 'h_kline_' + str(stock.code) + '.csv'
        if cm.DB_WAY == 'csv':
            maStrategy = MACD_LIVE_TEST.MAStrategy(cm.DownloadDir + fileName, stock)
        elif cm.DB_WAY == 'redis':
            maStrategy = MACD_LIVE_TEST.MAStrategy(stockData = stock, df=get_stock_k_line(stock.code))    
        signal = maStrategy.select_Time_Mix(2)
        if signal > 0:
            #print stock.name, stock.current, (float(stock.current)-float(stock.close))/float(stock.close)*100, '%'
            print '>' * 5, 'Buy now!', stock.name, stock.current, (float(stock.current)-float(stock.close))/float(stock.close)*100, '%'
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
    

#初始化sched模块的scheduler类
#第一个参数是一个可以返回时间戳的函数，第二个参数可以在定时未到达之前阻塞。
s = sched.scheduler(time.time,time.sleep)

#被周期性调度触发的函数
@fn_timer_ 
def event_func():
    #print "Current Time:",time.time()
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    main()
    print '\n'
    
    r = redis.Redis(host='127.0.0.1', port=6379)
    
    print '买入:'
    for code in stock_buy_list:
        stockInfo = get_stock_info(code)
        print 'Buy:', code, stockInfo['name']
        r.lpush('buy_list', stockInfo['name'])

    print '\n卖出:'
    for code in stock_sale_list:
        if code in stock_list:
            stockInfo = get_stock_info(code)
            print 'Sale:', code, stockInfo['name']
            r.lpush('sale_list', stockInfo['name'])
    
#enter四个参数分别为：间隔事件、优先级（用于同时间到达的两个事件同时执行时定序）、被调用触发的函数，给他的参数（注意：一定要以tuple给如，如果只有一个参数就(xx,)）
def perform(inc):
    s.enter(inc,0,perform,(inc,))
    event_func()
    
def mymain(inc=60):
    s.enter(0,0,perform,(inc,))
    s.run()
 
   
 
if __name__ == "__main__":
    print ">>live trade begin"
    
    mymain()
    
#     while(True):
#         
#         
#         
#         print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
#         main()
#         print '\n'
#         
#         print '买入:'
#         for code in stock_buy_list:
#             stockInfo = get_stock_info(code)
#             print 'Buy:', code, stockInfo['name']
#     
#         print '\n卖出:'
#         for code in stock_sale_list:
#             if code in stock_list:
#                 stockInfo = get_stock_info(code)
#                 print 'Sale:', code, stockInfo['name']
#         #break
#         sleep(30) #2s
    
    print ">>live trade end"
    