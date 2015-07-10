#!/usr/local/bin/python
#coding=utf-8

import os
import datetime,time
import pandas as pd

import util.commons as cm
from util.stockutil import getSixDigitalStockCode
from data_to_sql import download_stock_kline
import tushare as ts
import redis, sqlite3
from sqlalchemy import create_engine



# 获取个股K线数据
# input:
# ->code: 股票代码
# output:
# -> DataFrame
def get_stock_k_line(code, date_start='', date_end=datetime.date.today()):
    code = getSixDigitalStockCode(code)
    fileName = 'h_kline_' + str(code) + '.csv'
    
    df = None
    #如果存在则直接取
    if cm.DB_WAY == 'csv':
    
        if os.path.exists(cm.DownloadDir+fileName):
            df = pd.read_csv(cm.DownloadDir+fileName)
        # 不存在则立即下载
        #     else:
        #         df = download_stock_kline(code, date_start, date_end)
    elif cm.DB_WAY == 'redis':
        r = redis.Redis(host='127.0.0.1', port=6379)
        if len(date_start) == 0:
            date_start = r.hget(cm.PRE_STOCK_BASIC+code, cm.KEY_TimeToMarket)
        #if len(date_start) == 0:
        date_start = '20150101'    
        date_start = datetime.datetime.strptime(str(date_start), "%Y%m%d")
        date_start = date_start.strftime("%Y-%m-%d") 
        date_end = date_end.strftime("%Y-%m-%d")
        
        keys = r.lrange(cm.INDEX_STOCK_KLINE+code, 0, -1)
        
        listSeries = []
        for key in keys:
            if key > date_start and key < date_end:
                dict = r.hgetall(cm.PRE_STOCK_KLINE+code +':'+ key)
                #_se = pd.Series(dict, index=[cm.KEY_DATE, cm.KEY_OPEN, cm.KEY_HIGH, cm.KEY_CLOSE, cm.KEY_LOW, cm.KEY_VOLUME,cm.KEY_AMOUNT]) 
                _se = pd.Series(dict, index=[cm.KEY_DATE, cm.KEY_CLOSE]) 
                listSeries.append(_se)
        df = pd.DataFrame(listSeries)       
    elif cm.DB_WAY == 'sqlite':
        
        #engine = create_engine('sqlite:///:memory:')
        engine = create_engine('sqlite:///..\stocks.db3')
        
        try:
                   
            sql = 'select %s, %s from %s order by %s asc' % (cm.KEY_DATE, cm.KEY_CLOSE, cm.PRE_STOCK_KLINE_Sqlite+code, cm.KEY_DATE)
            df = pd.read_sql_query(sql, engine)
            
        except Exception as e:
            print str(e)    
    return df     



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
    try:
        if cm.DB_WAY == 'csv':
        
            df = pd.DataFrame.from_csv(cm.DownloadDir + cm.TABLE_STOCKS_BASIC + '.csv')
            #se = df.loc[int(code)]
            se = df.ix[int(code)]
            
        
        elif cm.DB_WAY == 'redis':
            r = redis.Redis(host='127.0.0.1', port=6379)
            se = pd.Series(r.hgetall(cm.PRE_STOCK_BASIC+code))
        
        elif cm.DB_WAY == 'sqlite': 
            engine = create_engine('sqlite:///..\stocks.db3')
            sql = "select * from %s where %s='%s'" % (cm.INDEX_STOCK_BASIC,cm.KEY_CODE, code)
            df = pd.read_sql_query(sql, engine)
            se = df.ix[0]
            
    except Exception as e:
        print str(e)
            
    return se    
# 获取终止上市股票列表        
def get_stock_terminated():
    return ts.get_terminated()  

if __name__ == "__main__":
    print get_stock_k_line('000001') 
    #get_stock_info('000001')           