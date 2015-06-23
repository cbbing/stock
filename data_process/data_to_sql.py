#!/usr/local/bin/python
#coding=utf-8

from sqlalchemy import create_engine
import tushare as ts
import os
import pandas as pd
import datetime
from multiprocessing.dummy import Pool as ThreadPool

#DB_WAY:数据存储方式 'csv'  # or 'mysql'
DB_WAY = 'csv'
DB_USER = 'root'
DB_PWD = '1234' # or '123456' in win7
DB_NAME = 'test'
TABLE_STOCKS_BASIC = 'stock_basic_list'
DownloadDir = os.path.pardir + '/stockdata/' # os.path.pardir: 上级目录



# 获取股票基本信息
# 通过DB_WAY 选择存入csv或mysql
def get_stock_basic_list():
    df = ts.get_stock_basics()
    
    
    try:
        #直接保存
        if DB_WAY == 'csv':
            print 'choose csv'
            df.to_csv(DownloadDir+TABLE_STOCKS_BASIC + '.csv');
            print 'download csv finish'
        else:
            
            engineString = 'mysql://' + DB_USER + ':' + DB_PWD + '@127.0.0.1/' + DB_NAME + '?charset=utf8'
            print engineString
            engine = create_engine(engineString)
            
            df.to_sql(TABLE_STOCKS_BASIC, engine, if_exists='replace')
            
            sql = 'select * from ' + TABLE_STOCKS_BASIC + ' where code = "600000"'
            dfRead = pd.read_sql(sql, engine)
            print dfRead
    except Exception as e:
        print str(e)        

# 获取股票的K线
# code:股票代码

def get_stock_kline(code, date_start='', date_end=datetime.date.today()):
    code = convertStockIntToStr(code)
    print 'download ' + str(code) + ' k-line'
    try:
        fileName = 'h_kline_' + str(code) + '.csv'
        if os.path.exists(DownloadDir+fileName):
            print (">>exist:" + code)
            df = pd.DataFrame.from_csv(path=DownloadDir+fileName)
            
            se = df.head(1).index #取已有文件的最近日期
            date_start = se[0].strftime("%Y-%m-%d")
            #print date_start
            return
        
        if date_start == '':
            se = get_stock_info(code)
            date_start = se['timeToMarket'] 
            date = datetime.datetime.strptime(str(date_start), "%Y%m%d")
            date_start = date.strftime('%Y-%m-%d')
        date_end = date_end.strftime('%Y-%m-%d')    
        df_qfq = ts.get_h_data(str(code), start=date_start, end=date_end) # 前复权
        df_nfq = ts.get_h_data(str(code), start=date_start, end=date_end) # 不复权
        df_hfq = ts.get_h_data(str(code), start=date_start, end=date_end) # 后复权
        df_qfq['open_no_fq'] = df_nfq['open']
        df_qfq['high_no_fq'] = df_nfq['high']
        df_qfq['close_no_fq'] = df_nfq['close']
        df_qfq['low_no_fq'] = df_nfq['low']
        df_qfq['open_hfq']=df_hfq['open']
        df_qfq['high_hfq']=df_hfq['high']
        df_qfq['close_hfq']=df_hfq['close']
        df_qfq['low_hfq']=df_hfq['low']
        
        df_qfq.to_csv(DownloadDir+fileName);
        print '\ndownload ' + str(code) +  ' k-line finish'
            
        return df_qfq
        
    except Exception as e:
        print str(e)        
        
    print 'download finish'

#######################
##  private methods  ##
#######################

# 获取个股的基本信息：股票名称，行业，地域，PE等
# 返回值类型：Series
def get_stock_info(code):
    if DB_WAY == 'csv':
        try:
            df = pd.DataFrame.from_csv(DownloadDir + TABLE_STOCKS_BASIC + '.csv')
            #se = df.loc[int(code)]
            se = df.ix[int(code)]
            return se
        except Exception as e:
            print str(e)
                

# 获取所有股票的历史K线
def get_all_stock_history_k_line():
    print 'download all stock k-line'
    if DB_WAY == 'csv':
        try:
            df = pd.DataFrame.from_csv(DownloadDir + TABLE_STOCKS_BASIC + '.csv')
            #se = df.loc[int(code)]
            #se = df.ix[code]
            pool = ThreadPool(processes=20)
            pool.map(get_stock_kline, df.index)
            pool.close()
            pool.join()  
            
#             for code in df.index:
#                 
#                 print get_stock_info(code)['name']
#                 get_stock_kline(convertStockIntToStr(code))
            #return se
        except Exception as e:
            print str(e)

# 补全股票代码
# input: int or string
# output: string
def convertStockIntToStr(code):
    strZero = ''
    for i in range(len(str(code)), 6):
        strZero += '0'
        
    return strZero + str(code)
    
#get_stock_basic_list()
#get_single_stock_info(600000)
#get_stock_kline(600000)
get_all_stock_history_k_line()






