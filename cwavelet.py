#!/usr/local/bin/python
#coding=utf-8

import math
import numpy as np
import pywt
import pylab
import matplotlib.pyplot as plt
import cleastsq
import copy

#固定阈值准则 (sqtwolog)
def threshold_sqtwolog(n):
    return math.sqrt(2*math.log(n))

#软阈值处理函数
def softThreshold(thr, values):
    newValues = []
    for value in values:
        if math.fabs(value) <= thr:
            value = 0
        elif value > thr:
            value -= thr
        else:
            value += thr
        newValues.append(value)
    return newValues     

def getWaveletData(values, waveletName, level, threadMethodName):
    mode = 'sym'
    #小波系数分解
    data = pywt.wavedec(values, waveletName, mode, level)
    #cA4, cD4, cD3, cD2, cD1 = pywt.wavedec(values, waveletName, mode, level)
    coeffs = [] #小波重构系数
    #阈值处理
    if threadMethodName == 'sqtwolog':
        #print len(cA4), len(cD4), len(cD3), len(cD2), len(cD1),len(values)
        for i in np.arange(0, len(data)):
            if i > 0:
                data[i] = softThreshold(threshold_sqtwolog(len(data[i])), data[i])
            coeffs.append(data[i])
    #小波重构
    zValues = pywt.waverec(coeffs, waveletName, mode)
        
#     if level == 4:
#         #cA4, cD4, cD3, cD2, cD1 = pywt.wavedec(values, waveletName, mode, level)
#         coeffs = []
#         #阈值处理
#         if threadMethodName == 'sqtwolog':
#             #print len(cA4), len(cD4), len(cD3), len(cD2), len(cD1),len(values)
# #             cD4 = softThreshold(threshold_sqtwolog(len(cD4)), cD4)
# #             cD3 = softThreshold(threshold_sqtwolog(len(cD3)), cD3)
# #             cD2 = softThreshold(threshold_sqtwolog(len(cD2)), cD2)
# #             cD1 = softThreshold(threshold_sqtwolog(len(cD1)), cD1)
#         #小波重构
#         #coeffs = [cA4, cD4, cD3, cD2, cD1]
#         zValues = pywt.waverec(coeffs, waveletName, mode)
#     elif level ==2:
#         cA2, cD2, cD1 = pywt.wavedec(values, waveletName, mode, level)
#         #阈值处理
#         if threadMethodName == 'sqtwolog':
#             print len(cA2), len(cD2), len(cD1),len(values)
#             cD2 = softThreshold(threshold_sqtwolog(len(cD2)), cD2)
#             cD1 = softThreshold(threshold_sqtwolog(len(cD1)), cD1)
#         #小波重构
#         coeffs = [cA2, cD2, cD1]
#         zValues = pywt.waverec(coeffs, waveletName, mode) 
    return zValues

#小波包分解
# forecastCount:预测的点位数
def getWavePacketData(values, waveletName, level, forecastCount):
    wp = pywt.WaveletPacket(data=values, wavelet=waveletName, mode='sym', maxlevel=level)
    print waveletName, ":", wp.maxlevel
    #nodes = wp.get_level(level)
    #labels = [n.path for n in nodes]
    #values = pylab.array([n.data for n in nodes], 'd')
    #print labels
    #print [n.data for n in nodes]
    #print [node.path for node in wp.get_leaf_nodes(decompose=False)]
    #print [node.path for node in wp.get_leaf_nodes(decompose=True)]
    coeffs = [(node.path, node.data) for node in wp.get_leaf_nodes(decompose=True)]
    #print coeffs
    for node in wp.get_leaf_nodes(decompose=True):
        print node.path, len(node.data)
    
    
    coeffsNew = []
    for path, data in coeffs:
        data = cleastsq.getFitYValues(range(len(data)), data, range(len(data)+forecastCount))
        coeffsNew.append((path, data))                                   
    
    #print coeffsNew
    
    wp2 = pywt.WaveletPacket(None, waveletName, maxlevel=level)
    for path, data in coeffsNew:
        wp2[path] = data
    
    #print wp["a"]
    #print [node.path for node in wp2.get_leaf_nodes(decompose=False)]
    value2s= wp2.reconstruct(update=True)
    newLen = len(values)+forecastCount
    print newLen
    return value2s[:newLen]
    
#     print len(value2s)
#     value2s_n= wp2.reconstruct(update=False)
#     plt.plot(range(18), value2s[0:18], color="b", linewidth=1)
#     #plt.plot(range(len(value2s_n)), value2s_n, color="r", linewidth=1)
#     plt.xlabel("Time")
#     plt.ylabel("Price")
#     plt.grid()
#     plt.legend()
#     plt.show()
    
#     print wp['a'].data
#     print wp['d'].data
#     print wp['add'].data
#     print wp['ada'].data
#     print [node.path for node in wp.get_level(3, 'freq')]
    
    
if __name__ == '__main__':
    values = range(16)
    for i in np.arange(4,5):
        name = "db"+str(i)
        getWavePacketData(values, name, 3, 3)   
        break 
    