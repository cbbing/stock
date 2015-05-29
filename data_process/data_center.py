#!/usr/local/bin/python
#coding=utf-8
import os
import matplotlib.mlab as mlab

# 获取csv文件序列
def getCsvDataBySplitPath(stock_code, dataPath):
    fh = open(dataPath + '\\' + stock_code +".csv", 'r')
    r = mlab.csv2rec(fh); 
    fh.close()
    r.sort() #按时间由远及近排序
    
    #比如读取收盘价 prices = r.adj_price
    return r

# 获取csv文件序列
def getCsvDataByFullPath(csvName):
    fh = open(csvName, 'r')
    r = mlab.csv2rec(fh); 
    fh.close()
    r.sort() #按时间由远及近排序
    
    #比如读取收盘价 prices = r.adj_price
    return r

if __name__ == "__main__":
    print 'data center'