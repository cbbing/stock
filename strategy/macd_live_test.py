#!/usr/local/bin/python
#coding=utf-8

#实时均线策略

import pandas as pd
import numpy as np
from data_process.get_data_center import get_stock_k_line

SIGNAL_BUY = 1  #买 
SIGNAL_SALE = -1 #卖
SIGNAL_DEFAULT = 0
    
class MAStrategy:
    
    # df: DataFrame    
    def __init__(self, stockCsvPath = '', stockData='', df=''):
        
        self.AVR_SHORT = 12
        self.AVR_LONG = 40
            
        if len(stockCsvPath) > 0:
            #方式一
            df_stockHistory = get_stock_k_line(stockData.code)
            if len(df_stockHistory) == 0:
                return
            #df_stockHistory = pd.read_csv(stockCsvPath)
            # 将数据按照交易日期从远到近排序
            df_stockHistory.sort('date', inplace=True)
            self.close_price = df_stockHistory['close'].get_values()
            
            needWrite2Csv = False
            try:
                self.ma_12 = df_stockHistory['ma_12'].get_values()
                self.ma_40 = df_stockHistory['ma_40'].get_values()
            except Exception as e:  
                print '重新计算 ma'   
                self.ma_12 = pd.rolling_mean(self.close_price, self.AVR_SHORT)
                self.ma_40 = pd.rolling_mean(self.close_price, self.AVR_LONG)
                needWrite2Csv = True
                df_stockHistory['ma_12'] = self.ma_12
                df_stockHistory['ma_40'] = self.ma_40
                
            try:
                self.ema_12 = df_stockHistory['ema_12'].get_values()
                self.ema_40 = df_stockHistory['ema_40'].get_values()
            except Exception as e:
                print '重新计算 ema'
                self.ema_12 = pd.ewma(self.close_price, span=self.AVR_SHORT)
                self.ema_40 = pd.ewma(self.close_price, span=self.AVR_LONG)  
                needWrite2Csv = True
                df_stockHistory['ema_12'] = self.ema_12
                df_stockHistory['ema_40'] = self.ema_40
                
            if needWrite2Csv:
                # 将数据按照交易日期从近到远排序
                df_stockHistory.sort('date', ascending = False, inplace=True)
                df_stockHistory.to_csv(stockCsvPath)
                print '保存至'+stockCsvPath
            
            self.close_price = np.append(self.close_price, float(stockData.current))
            
            # 计算当前的ma
            last_ma_12 = sum(self.close_price[-self.AVR_SHORT:])/self.AVR_SHORT;
            last_ma_40 = sum(self.close_price[-self.AVR_LONG:])/self.AVR_LONG;
            self.ma_12 = np.append(self.ema_12, last_ma_12)
            self.ma_40 = np.append(self.ema_40, last_ma_40)
            
            
            # 计算当前价的ema
            last_ema_12 = self.ema_12[-2] * (self.AVR_SHORT-1)/(self.AVR_SHORT+1) + stockData.current * 2/(self.AVR_SHORT+1)
            last_ema_40 = self.ema_40[-2] * (self.AVR_LONG-1)/(self.AVR_LONG+1) + stockData.current * 2/(self.AVR_LONG+1) 
            
            #self.close_price = np.append(self.close_price, float(stockData.current))
            self.ema_12 = np.append(self.ema_12, last_ema_12)
            self.ema_40 = np.append(self.ema_40, last_ema_40)
               
        
        else:
            #方式二
            # 将数据按照交易日期从远到近排序
            df.sort('date', inplace=True)
            self.close_price = df['close'].get_values()
        
            self.ma_12 = pd.rolling_mean(self.close_price, self.AVR_SHORT)
            self.ma_40 = pd.rolling_mean(self.close_price, self.AVR_LONG)
          
            self.ema_12 = pd.ewma(self.close_price, span=self.AVR_SHORT)
            self.ema_40 = pd.ewma(self.close_price, span=self.AVR_LONG)  
            
          
            

    # 组合择时指标 (实时）
    def select_Time_Mix(self, conditionBuy = 2, conditonSale = 2):
        
        # 综合策略
        signalMA = self.select_Time_MA()
        signalMACD = self.select_Time_MACD()
        signalDMA = self.select_Time_DMA()
        signalTRIX = self.select_Time_TRIX()
        signalAMA = self.select_Time_AMA()
        
        # 买入信号的总数
        buyTotal = (abs(signalMA)+signalMA)/2 + (abs(signalMACD)+signalMACD)/2 + \
                 (abs(signalDMA)+signalDMA)/2 + (abs(signalTRIX)+signalTRIX)/2 + (abs(signalAMA)+signalAMA)/2 
                 
        # 卖出信号的总数
        saleTotal = (-abs(signalMA)+signalMA)/2 + (-abs(signalMACD)+signalMACD)/2 + \
                 (-abs(signalDMA)+signalDMA)/2 + (-abs(signalTRIX)+signalTRIX)/2 + (-abs(signalAMA)+signalAMA)/2
        
        signal = SIGNAL_DEFAULT
        if buyTotal+saleTotal >= conditionBuy:
            signal = SIGNAL_BUY
        elif buyTotal+saleTotal <= -conditonSale:
            signal = SIGNAL_SALE
        
        return signal 
    
    # MA指标择时  (回测）
    def select_Time_MA(self):
        
        #EMA 
        ma_list = [self.AVR_SHORT, self.AVR_LONG]
        if ma_list[0] == self.AVR_SHORT and ma_list[1] == self.AVR_LONG:
            ema_close_short = self.ema_12
            ema_close_long = self.ema_40
        else:     
            ema_close_short = pd.ewma(self.close_price, span=ma_list[0])
            ema_close_long = pd.ewma(self.close_price, span=ma_list[1])
        
        
        signal = SIGNAL_DEFAULT
        
        if ema_close_short[-1] > ema_close_short[-2] and ema_close_short[-1] > ema_close_long[-1] \
                            and ema_close_short[-2] < ema_close_long[-2]:
            signal = SIGNAL_BUY
        elif ema_close_long[-1] < ema_close_long[-2] and ema_close_short[-1] < ema_close_long[-1] \
                            and ema_close_short[-2] > ema_close_long[-2]:
            signal = SIGNAL_SALE            
        
        return signal            
            
        
    # MACD指标择时 (回测）
    def select_Time_MACD(self):
        
        #EMA 
        ma_list = [self.AVR_SHORT, self.AVR_LONG]
        ma_dea = 10
        if ma_list[0] == self.AVR_SHORT and ma_list[1] == self.AVR_LONG:
            ema_close_short = self.ema_12
            ema_close_long = self.ema_40
        else:     
            ema_close_short = pd.ewma(self.close_price, span=ma_list[0])
            ema_close_long = pd.ewma(self.close_price, span=ma_list[1])
        
        
        dif_price = ema_close_short - ema_close_long
        dea_price = pd.ewma(dif_price, span=ma_dea)
        macd_price = 2 * (dif_price - dea_price)
        
        signal = SIGNAL_DEFAULT
            
        if dif_price[-1] > dif_price[-2] and dif_price[-1] > dea_price[-2] \
                                            and dif_price[-2] < dea_price[-2] and dea_price[-1] > 0:
            signal = SIGNAL_BUY
        elif dif_price[-1] < dif_price[-2] and dif_price[-1] < dea_price[-1] \
                            and dif_price[-2] > dea_price[-2] and dif_price[-1] < 0:
            signal = SIGNAL_SALE            
        return signal            
    
    # DMA指标择时 (回测）
    def select_Time_DMA(self):
        
        #MA 
        ma_list = [self.AVR_SHORT, self.AVR_LONG]
        ma_dea = 10
        
        if ma_list[0] == self.AVR_SHORT and ma_list[1] == self.AVR_LONG:
            ma_close_short = self.ma_12
            ma_close_long = self.ma_40
        else:    
            ma_close_short = pd.rolling_mean(self.close_price, ma_list[0])
            ma_close_long = pd.rolling_mean(self.close_price, ma_list[1])
        
        dma_price = ma_close_short - ma_close_long
        ama_price = pd.rolling_mean(dma_price, ma_dea)
        
        signal = SIGNAL_DEFAULT
            
        if dma_price[-1] > dma_price[-2] and dma_price[-1] > ama_price[-1] \
                                            and dma_price[-2] < ama_price[-2]:
            signal = SIGNAL_BUY
        elif dma_price[-1] < dma_price[-2] and dma_price[-1] < ama_price[-1] \
                            and dma_price[-2] > ama_price[-2]:
            signal = SIGNAL_SALE           
        return signal            
        
     
    # TRIX指标择时 (回测）
    def select_Time_TRIX(self):
        
        #EMA 
        ma_list = [self.AVR_SHORT, self.AVR_SHORT] #N,M
        
        if ma_list[0] == self.AVR_SHORT:
            ema_close = self.ema_12
        else:    
            ema_close = pd.ewma(self.close_price, span=ma_list[0])
        ema_close = pd.ewma(ema_close, span=ma_list[0])
        tr_close = pd.ewma(ema_close, span=ma_list[0])
        
        trixsList = [0]
        for i in range(1, len(tr_close)):
            #print tr_close[i], tr_close[i-1]
            trix = (tr_close[i]-tr_close[i-1])/tr_close[i-1]*100
            trixsList.append(trix)
        trixs = np.array(trixsList)    
        maxtrix = pd.rolling_mean(trixs, ma_list[1])
        
        signal = SIGNAL_DEFAULT
            
        if trixs[-1] > trixs[-2] and trixs[-1] > maxtrix[-1] \
                                            and trixs[-2] < maxtrix[-2]:
            signal = SIGNAL_BUY
        elif trixs[-1] < trixs[-2] and trixs[-1] < maxtrix[-1] \
                            and trixs[-2] > maxtrix[-2]:
            signal = SIGNAL_SALE            
        return signal
    
            
       
    
    # AMA指标择时
    def select_Time_AMA(self):
        
        percentage = 0.1
        
        # 指数平滑序列
        containts = [0]*10
        for i in range(10, len(self.close_price)):
            sub_price = self.close_price[i-10:i]
            constaint = self.getConstaint(sub_price)
            containts.append(constaint);
            
        ama_price = [float(self.close_price[0])]    
        for i in range(1, len(self.close_price)):
            ama = containts[i-1] * float(self.close_price[i-1]) + (1-containts[i-1])*ama_price[i-1]
            ama_price.append(float(ama))
         
        #print np.array(ama_price[i-19:i+1]) - np.array(ama_price[i-20:i])
        threshold = percentage * np.std(np.array(ama_price[i-19:i+1]) - np.array(ama_price[i-20:i])) # 过滤器
        
        signal = SIGNAL_DEFAULT
        if ama_price[-1] - np.min(ama_price[-6:-1]) > threshold: 
            signal = SIGNAL_BUY
        elif np.max(ama_price[-6:-1]) - ama_price[-1] > threshold:    
            signal = SIGNAL_SALE    
            
        return signal
    
    # 获取平方平滑系数
    def getConstaint(self, prices):
        direction = abs(float(prices[-1]) - float(prices[0]))
        volatility = sum(abs(float(prices[i+1])-float(prices[i])) for i in range(len(prices)-1))
        if volatility == 0.0:
            return 0
        ER = abs(direction/volatility)   
        fastSC = 2.0/(2.0+1)
        slowSC = 2.0/(30.0+1)
        sSC = ER * (fastSC-slowSC) + slowSC
        constaint = sSC*sSC 
        return constaint

