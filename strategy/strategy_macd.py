#!/usr/local/bin/python
#coding=utf-8

import sys
import macd
import os
import matplotlib.pyplot as plt

sys.path.append("..\\data_process\\")
import data_center

def strategy_macd():
    #读取历史数据
    
    # 计算EMA（12日，26日）, DIF, DEA, MACD
    downloadDir = os.path.pardir + '\\stockdata'
    downloadDirNew = os.getcwd() + '\\stockdata_macd'
    if os.path.exists(downloadDir) == False:
        os.makedirs(downloadDir)
    if os.path.exists(downloadDirNew) == False:
        os.makedirs(downloadDirNew)
                    
    #遍历文件夹下的所有csv数据                
    for root, dirs, files in os.walk(downloadDir):
        for name in files:
            stockCsvPath =  root + '\\' + name
            if ".csv" in stockCsvPath:
                basename = os.path.basename(stockCsvPath)
                stock_code, exp = os.path.splitext(basename)
                #macd.run(stockCsvPath, stock_code)
                
                each_stock_strategy(stockCsvPath, stock_code)
                #break

def each_stock_strategy(stockCsvPath, stock_code):
    plt.figure()
                
    r = data_center.getCsvDataByFullPath(stockCsvPath)
    dif_price, dea_price, macd_price = macd.getMAStrategy(stockCsvPath, stock_code, 'MACD')
    ama_price = macd.getMAStrategy(stockCsvPath, stock_code, 'AMA')
    
    #plot.plotClosePrice(plt, str(stock_code), stock_code, root)    
    #plot.plotData(stockCsvPath + '\\' +name, name)
    plt.plot(range(len(r.adj_close)), r.adj_close, 'black', label="Close")
    plt.plot(range(len(dif_price)), dif_price, 'red', label='DIF')
    plt.plot(range(len(dea_price)), dea_price, 'blue', label='DEA')
    plt.plot(range(len(macd_price)), macd_price, 'cyan', label='MACD')
    plt.plot(range(len(ama_price)), ama_price, 'green', label='AMA')
    plt.title(stock_code)
    plt.legend()
    plt.grid()
    plt.show()
 
    
if __name__ == "__main__":
    strategy_macd()    
    #each_stock_strategy("..\\stockdata\\600000.csv", '399001')