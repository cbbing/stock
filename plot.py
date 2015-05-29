#!/usr/local/bin/python
#coding=utf-8
import os
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import numpy as np
import math
import csv
import urllib
import urllib2
import pywt
from numpy import log
import cwavelet
import copy
import cleastsq
import BP

date_begin = [1, 1, 2014]
date_end = [5, 27, 2015]


def plotClosePrice(plt, stock_name, stock_code, dataPath):
    fh = open(dataPath + '\\' + stock_code +".csv", 'r')
    r = mlab.csv2rec(fh); fh.close()
    r.sort()
    
    prices = r.adj_close
    
    
    plt.plot(r.date, prices)
    
     
 
#收盘价走势及小波处理 
def plotData(stock_code, stock_name):
    try:
        xValues=[]
        yValues=[]
        
        xLabels=[]
        
        dataPath = os.getcwd() + '\\stockdata\\';
        
        i=-1
        for line in open(dataPath + stock_code +".csv"):
            f_date, f_open, f_high, f_low, f_close, f_volume, f_adjclose = line.split(",")
            i += 1
            if i == 0 or i > 1000:
                continue 
            xValues.append(i)
            yValues.append(float(f_adjclose))
            xLabels.append(f_date)
        yValues.reverse()
        
        
        zValues = cwavelet.getWaveletData(yValues, 'db2', 4, 'sqtwolog')
        zxValue = np.arange(0,len(zValues),1)
        print len(zxValue), len(zValues)
            
        plt.figure(figsize=(16,8))
        plt.plot(xValues, yValues, label=stock_code, color="b", linewidth=1)
        plt.plot(zxValue, zValues, color="r", linewidth=2)
        plt.xlabel("Time")
        plt.ylabel("Price")
        plt.title( stock_name)
        #plt.xticks(range(min(xLabels), max(xLabels)+1, 10))
        plt.grid()
        #plt.legend()
        plt.show()
        
    except Exception as e:
        print ("Exception:>>>" + str(e))
    finally:
        None    

def plotRateOfReturn(stock_code):  
    try:
        xValues = []
        yValues = []
        
        i=-1
        for line in open(stock_code + ".csv"):
            i += 1
            if i == 0 or i > 1000:
                continue 
            f_date, f_open, f_high, f_low, f_close, f_volume, f_adjclose = line.split(",")
            yValues.append(float(f_adjclose))
        
        #yValues删除最后一个元素，zValues删除第一个元素
        zValues = copy.deepcopy(yValues)   #深拷贝
        yValues.reverse()
        yValues.pop()
        zValues.pop()
        zValues.reverse()
        if len(yValues) != len(zValues):
            return
        
        rateValues = []
        for i in range(0, len(yValues)):
            print float(zValues[i])/yValues[i]
            rateValues.append(math.log(float(zValues[i])/yValues[i]))
            xValues.append(i)
        
        rateValues = cwavelet.getWaveletData(yValues, 'db4', 2, 'sqtwolog')
        
        # BP神经网络
#         patStock = []
#         for i in range(0, len(yValues)):
#             each = [[i], [yValues[i]]]
#             patStock.append(each)
#         patStockPre = copy.deepcopy(patStock)
#         for i in range(len(yValues), len(yValues)+10):
#             each = [[i], [0]]
#             patStockPre.append(each)
#         pat = [
#         [[0], [0]],
#         [[2], [1]],
#         [[3], [1]],
#         [[4], [5]]
#         ]
#     
#         # create a network with two input, two hidden, and one output nodes
#         n = BP.NN(1, 2, 1)
#         # train it with some patterns
#         n.train(patStock)
#         # test it
#         n.test(patStock)
        
        #最小二乘法
        print "原始长度:", len(rateValues)
        catRateValues = rateValues[:-7]
        print "原始长度:", len(catRateValues)
        leastsqValues = cwavelet.getWavePacketData(catRateValues, 'haar', 4, 3)
        #leastsqValues = cleastsq.getFitYValues(range(len(catRateValues)), catRateValues, range(len(catRateValues)+3))
        print "变换后长度:", len(leastsqValues)
        newLeastsqValues = np.concatenate((rateValues[:-3], leastsqValues[-3:]))
        
        newLeastsqValues2 = []
        for data in newLeastsqValues:
            data -= 0.2
            newLeastsqValues2.append(data)
        newLeastsqValues = newLeastsqValues2
            
        print "变换后长度:", len(newLeastsqValues)
        plt.figure(figsize=(16,8))
        plt.legend()
        plt.plot(range(len(rateValues)), rateValues,'b-', linewidth=1)
        plt.plot(range(len(newLeastsqValues)), newLeastsqValues, 'r-', linewidth=1)
        plt.xlabel('Time')
        plt.ylabel('Price')
        plt.title(stock_code)
        plt.grid()
        
        plt.show()
        
            
    except Exception as e:
        print ("Exception:>>>"+str(e))   
    finally:
        None
               
def down_file(url, file_name):
    
    u = urllib2.urlopen(url)
    f = open(file_name, 'wb')
    
    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break
    
        file_size_dl += len(buffer)
        f.write(buffer)
    f.close()

ChinaStockNumIndividualList = [
    {'code':"600011", 'num':1100, 'name':u"华能国际"}, # 
    {'code':"600000", 'num':1900, 'name':u"浦发银行"}, # 
    {'code':"002600", 'num':1000, 'name':u"江粉磁材"}, # 
    {'code':"002505", 'num':1000, 'name':u"大康牧业"}, # 
    {'code':"000725", 'num':2000, 'name':u"京东方A"}, # 
    {'code':"000783", 'num':600, 'name':u"长江证券"},  # 
    {'code':"600048", 'num':2000, 'name':u"保利地产"}, # 
    {'code':"300315", 'num':200, 'name':u"掌趣科技"}, # 
    {'code':"002167", 'num':600, 'name':u"东方锆业"}, # 
    {'code':"601001", 'num':1000, 'name':u"大同煤业"}, # 
    #{'code':"150172", 'num':5000, 'name':"证券B"}, #  
]
       
if __name__ == '__main__':
    
    for stockCodeDict in ChinaStockNumIndividualList:
        print stockCodeDict['name']
        #plotRateOfReturn(stockCodeDict['code'])
        plotData(stockCodeDict['code'], stockCodeDict['name'])
        break
    #上证指数    
    #downloadData("000001")    
    #plotRateOfReturn("000001")
    
    
  



