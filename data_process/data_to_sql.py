#!/usr/local/bin/python
#coding=utf-8

from sqlalchemy import create_engine
import tushare as ts
import os
import pandas as pd
import datetime
from multiprocessing.dummy import Pool as ThreadPool
from tushare.util import dateu as du
from pandas.core.algorithms import mode
from util import stockutil as util
import util.commons as cm
import redis
from util.stockutil import fn_timer as fn_timer_

#DB_WAY:数据存储方式 'csv'  # or 'mysql' or 'redis'
# DB_WAY = 'redis'
# DB_USER = 'root'
# DB_PWD = '1234' # or '123456' in win7
# DB_NAME = 'test'

r = redis.Redis(host='127.0.0.1', port=6379)

###################################
#-- 获取股票基本信息       --#
############################
# 通过DB_WAY 选择存入csv或mysql
def download_stock_basic_info():
    
    try:
        df = ts.get_stock_basics()
        #直接保存
        if cm.DB_WAY == 'csv':
            print 'choose csv'
            df.to_csv(cm.DownloadDir+cm.TABLE_STOCKS_BASIC + '.csv');
            print 'download csv finish'
            
        elif cm.DB_WAY == 'mysql':
            print 'choose mysql'
            engineString = 'mysql://' + cm.DB_USER + ':' + cm.DB_PWD + '@127.0.0.1/' + cm.DB_NAME + '?charset=utf8'
            print engineString
            engine = create_engine(engineString)
            
            df.to_sql(cm.TABLE_STOCKS_BASIC, engine, if_exists='replace')
            
            sql = 'select * from ' + cm.TABLE_STOCKS_BASIC + ' where code = "600000"'
            dfRead = pd.read_sql(sql, engine)
            print dfRead
            
        elif cm.DB_WAY == 'redis':
            print 'choose redis'
            
           
            # 查数据库大小
            print '\ndbsize:%s' %r.dbsize()
            
            # 看连接
            print 'ping %s' %r.ping()
            
            
            
            for idx, row in df.iterrows():
                print idx, row
                mapStock =  {cm.KEY_CODE:idx, cm.KEY_NAME:row['name'],cm.KEY_INDUSTRY:row['industry'],cm.KEY_AREA:row['area'],\
                             cm.KEY_TimeToMarket:row['timeToMarket']}
                # 写入hash表
                r.hmset(cm.PRE_STOCK_BASIC+idx, mapStock)
                
                #索引
                r.sadd(cm.INDEX_STOCK_BASIC, idx)
                #r.rpush(cm.INDEX_STOCK_BASIC, idx)
                #print r.hgetall(PRE_BASIC+idx)            
                
    except Exception as e:
        print str(e)        

# 下载股票的K线
# code:股票代码
# 默认为前复权数据：open, high, close, low； 不复权数据为：open_no_fq等，后复权数据为：open_hfq
# 默认为上市日期到今天的K线数据
def download_stock_kline(code, date_start='', date_end=datetime.date.today()):
    code = util.getSixDigitalStockCode(code)
    
    try:
        fileName = 'h_kline_' + str(code) + '.csv'
        
        writeMode = 'w'
        if os.path.exists(cm.DownloadDir+fileName):
            #print (">>exist:" + code)
            df = pd.DataFrame.from_csv(path=cm.DownloadDir+fileName)
            
            se = df.head(1).index #取已有文件的最近日期
            dateNew = se[0] + datetime.timedelta(1)
            date_start = dateNew.strftime("%Y-%m-%d")
            #print date_start
            writeMode = 'a'
        
        if date_start == '':
            se = get_stock_info(code)
            date_start = se['timeToMarket'] 
            date = datetime.datetime.strptime(str(date_start), "%Y%m%d")
            date_start = date.strftime('%Y-%m-%d')
        date_end = date_end.strftime('%Y-%m-%d')  
        date_end = '2015-06-30'
        # 已经是最新的数据
        if date_start >= date_end:
            df = pd.read_csv(cm.DownloadDir+fileName)
            return df
        
        print 'download ' + str(code) + ' k-line >>>begin (', date_start+u' 到 '+date_end+')'
        df_qfq = ts.get_h_data(str(code), start=date_start, end=date_end) # 前复权
        df_nfq = ts.get_h_data(str(code), start=date_start, end=date_end, autype=None) # 不复权
        df_hfq = ts.get_h_data(str(code), start=date_start, end=date_end, autype='hfq') # 后复权
        
        if df_qfq is None or df_nfq is None or df_hfq is None:
            return None
        
        df_qfq['open_no_fq'] = df_nfq['open']
        df_qfq['high_no_fq'] = df_nfq['high']
        df_qfq['close_no_fq'] = df_nfq['close']
        df_qfq['low_no_fq'] = df_nfq['low']
        df_qfq['open_hfq']=df_hfq['open']
        df_qfq['high_hfq']=df_hfq['high']
        df_qfq['close_hfq']=df_hfq['close']
        df_qfq['low_hfq']=df_hfq['low']
             
        if writeMode == 'w':
            df_qfq.to_csv(cm.DownloadDir+fileName)
        else:
            
            df_old = pd.DataFrame.from_csv(cm.DownloadDir + fileName)
            
            # 按日期由远及近
            df_old = df_old.reindex(df_old.index[::-1])
            df_qfq = df_qfq.reindex(df_qfq.index[::-1])
            
            df_new = df_old.append(df_qfq)
            #print df_new
            
            # 按日期由近及远
            df_new = df_new.reindex(df_new.index[::-1])
            df_new.to_csv(cm.DownloadDir+fileName)
            #df_qfq = df_new
        
            print '\ndownload ' + str(code) +  ' k-line to csv finish'
            return pd.read_csv(cm.DownloadDir+fileName)
        
            
        
    except Exception as e:
        print str(e)        
    
        
    return None

def download_stock_kline_to_redis(code, date_start='', date_end=datetime.date.today()):
    code = util.getSixDigitalStockCode(code)
    
    try:
        fileName = 'h_kline_' + str(code) + '.csv'
        
#         writeMode = 'w'
#         if os.path.exists(cm.DownloadDir+fileName):
#             #print (">>exist:" + code)
#             df = pd.DataFrame.from_csv(path=cm.DownloadDir+fileName)
#             
#             se = df.head(1).index #取已有文件的最近日期
#             dateNew = se[0] + datetime.timedelta(1)
#             date_start = dateNew.strftime("%Y-%m-%d")
#             #print date_start
#             writeMode = 'a'
#         
        if date_start == '':
            dates = r.lrange(cm.INDEX_STOCK_KLINE+code, 0, -1)
            if len(dates) > 0:
                nearstDate = dates[0]
                date = datetime.datetime.strptime(str(nearstDate), "%Y-%m-%d") + datetime.timedelta(1)
                date_start = date.strftime('%Y-%m-%d')
            else:
                se = get_stock_info(code) 
                date_start = se['timeToMarket']
                date = datetime.datetime.strptime(str(date_start), "%Y%m%d")
                date_start = date.strftime('%Y-%m-%d')
        date_end = date_end.strftime('%Y-%m-%d')  
        
        print 'download ' + str(code) + ' k-line >>>begin (', date_start+u' 到 '+date_end+')'
        df_qfq = ts.get_h_data(str(code), start=date_start, end=date_end) # 前复权
        
        if df_qfq is None:
            return None
        
        print 'choose redis'
        
       
        # 查数据库大小
        print '\ndbsize:%s' %r.dbsize()
        # 看连接
        print 'ping %s' %r.ping()
        
        for idx, row in df_qfq.iterrows():
            strDate = str(idx)[0:10]
            mapStock =  {cm.KEY_DATE:strDate,cm.KEY_OPEN:float(row['open']),cm.KEY_HIGH:float(row['high']),\
                             cm.KEY_CLOSE:float(row['close']), cm.KEY_VOLUME:float(row['volume']),\
                              cm.KEY_AMOUNT:float(row['amount'])}
            # 写入hash表
            r.hmset(cm.PRE_STOCK_KLINE+code + ':' + strDate, mapStock)
            
            #索引
            r.rpush(cm.INDEX_STOCK_KLINE+code, strDate)
             
        
       
        
        print '\ndownload ' + str(code) +  ' k-line to redis finish'
            
        
    except Exception as e:
        print str(e)        
    
        
    return None

# 下载股票的历史分笔数据
# code:股票代码
# 默认为最近3年的分笔数据
def download_stock_quotes(code, date_start='', date_end=str(datetime.date.today())):
    code = util.getSixDigitalStockCode(code)
    try:
        if date_start == '':
            date = datetime.datetime.today().date() + datetime.timedelta(-365*3) 
            date_start = str(date)
          
        dateStart = datetime.datetime.strptime(str(date_start), "%Y-%m-%d")   
                
        for i in range(du.diff_day(date_start, date_end)):
            date = dateStart + datetime.timedelta(i)
            strDate = date.strftime("%Y-%m-%d")
            df = ts.get_tick_data(code, strDate)
            print df
    except Exception as e:
        print str(e)        

#######################
##  private methods  ##
#######################

# 获取个股的基本信息：股票名称，行业，地域，PE等，详细如下
#     code,代码
#     name,名称
#     industry,所属行业
#     area,地区
#     pe,市盈率
#     outstanding,流通股本
#     totals,总股本(万)
#     totalAssets,总资产(万)
#     liquidAssets,流动资产
#     fixedAssets,固定资产
#     reserved,公积金
#     reservedPerShare,每股公积金
#     eps,每股收益
#     bvps,每股净资
#     pb,市净率
#     timeToMarket,上市日期
# 返回值类型：Series
def get_stock_info(code):
    if cm.DB_WAY == 'csv':
        try:
            df = pd.DataFrame.from_csv(cm.DownloadDir + cm.TABLE_STOCKS_BASIC + '.csv')
            #se = df.loc[int(code)]
            se = df.ix[int(code)]
            return se
        except Exception as e:
            #print str(e)
            return None
    elif cm.DB_WAY == 'redis':
        try:
            se = pd.Series(r.hgetall(cm.PRE_STOCK_BASIC+code))
            return se
        except Exception as e:
            print str(e)
            return None
        
# 获取所有股票的历史K线
@fn_timer_
def download_all_stock_history_k_line():
    print 'download all stock k-line start'
    
    try:
        if cm.DB_WAY == 'csv':
            df = pd.DataFrame.from_csv(cm.DownloadDir + cm.TABLE_STOCKS_BASIC + '.csv')
            #se = df.loc[int(code)]
            #se = df.ix[code]
            pool = ThreadPool(processes=20)
            pool.map(download_stock_kline, df.index)
            pool.close()
            pool.join()
        elif cm.DB_WAY == 'redis':
            codes = r.smembers(cm.INDEX_STOCK_BASIC)
            #codes = r.lrange(cm.INDEX_STOCK_BASIC, 0, -1)
            pool = ThreadPool(processes=20)
            pool.map(download_stock_kline_to_redis, codes)
            pool.close()
            pool.join()     
        
    except Exception as e:
        print str(e)
    print 'download all stock k-line finish'
    
# 补全股票代码(6位股票代码)
# input: int or string
# output: string
# def convertStockIntToStr(code):
#     strZero = ''
#     for i in range(len(str(code)), 6):
#         strZero += '0'
#     return strZero + str(code)
    
if __name__ == '__main__'  :  
    #download_stock_basic_info()
    #get_single_stock_info(600000)
    download_all_stock_history_k_line()
    #download_stock_quotes(600000)
    #download_stock_kline_to_redis('000001')
    


