#!/usr/local/bin/python3
#coding=utf-8

import sys
import data_process.online_data as OnlineData

if __name__ == "__main__":
    print ">>live trade begin"
    
    # 监听股票列表
    stock_list = [600000, 600048]
    # 获取实时股价
    stockClassList = OnlineData.getLiveMutliChinaStockPrice(stock_list)
    for stock in stockClassList:
        print stock.current
    
    # 多线程提醒实时买卖
    
    
    print ">>live trade end"

    