#!/usr/local/bin/python3
#coding=utf-8

import os
import data_process.online_data as OnlineData
import strategy.macd_live_test as MACD_LIVE_TEST
from time import sleep
import time
import ctypes
import util.commons as cm

# 监听股票列表
stock_list = ['600000','600048', '600011', '002600', '002505', '000725', '000783', '300315', '002167', '601001']
#stock_list =['000725']

def main():
    # 获取实时股价
    stockClassList = OnlineData.getLiveMutliChinaStockPrice(stock_list)
    for stock in stockClassList:
        
        
        try:
            # 多线程提醒实时买卖
            if float(stock.current) == 0.0:
                print '>>>', stock.name,'>>>停牌!',  stock.close, stock.time
                continue
            
            
            
            fileName = 'h_kline_' + str(stock.code) + '.csv'
            maStrategy = MACD_LIVE_TEST.MAStrategy(cm.DownloadDir + fileName, stock)
            signal = maStrategy.select_Time_Mix()
            if signal > 0:
                #print stock.name, stock.current, (float(stock.current)-float(stock.close))/float(stock.close)*100, '%'
                print '>' * 5, 'Buy now!', stock.name, stock.current, stock.time
                #Mbox('Buy now!' , '%s %s %s' % (stock.code, stock.current, stock.time), 1)
            elif signal < 0:     
                #print stock.name, stock.current, (float(stock.current)-float(stock.close))/float(stock.close)*100, '%'
                print '>' * 5, 'Sale now!', stock.name, stock.current, (float(stock.current)-float(stock.close))/float(stock.close)*100, '%', stock.time
                #Mbox('Sale now!' , '%s %s %s' % (stock.code, stock.current, stock.time), 1)
            else:
                print stock.name, stock.current, (float(stock.current)-float(stock.close))/float(stock.close)*100, '%'
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
        sleep(30) #2s
    
    print ">>live trade end"
    