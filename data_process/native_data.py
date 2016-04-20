#!/usr/local/bin/python
#coding=utf-8
import os
#import matplotlib.mlab as mlab
import sys
#import chardet

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
    
#     typeEncode = sys.getfilesystemencoding()##系统默认编码
#     infoencode = chardet.detect(fh).get('encoding','utf-8') #通过第3方模块来自动提取网页的编码
#     fh = fh.decode(infoencode, 'ignore').encode(typeEncode)##先转换成unicode编码，然后转换系统编码输出  ---------->方式一
    
    r = mlab.csv2rec(fh); 
    fh.close()
    r.sort() #按时间由远及近排序
    
    #比如读取收盘价 prices = r.adj_price
    return r

if __name__ == "__main__":
    print 'data center'