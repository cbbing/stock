#!/usr/local/bin/python
#coding=utf-8

import os
import datetime,time
import pandas as pd

import util.commons as cm
from util.stockutil import getSixDigitalStockCode

import tushare as ts
import redis

from config import *
from util.commons import *

# 获取所有股票代码
def get_all_stock_codes():
    if DB_WAY == 'mysql':
        sql = 'select %s from %s' % (KEY_CODE, INDEX_STOCK_BASIC)
        df = pd.read_sql_query(sql, engine)
        codes = df[KEY_CODE].get_values()
        return codes
    else:
        return []


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
    if DB_WAY == 'csv':
    
        if os.path.exists(DownloadDir+fileName):
            df = pd.read_csv(DownloadDir+fileName)
        # 不存在则立即下载
        #     else:
        #         df = download_stock_kline(code, date_start, date_end)
    elif DB_WAY == 'redis':
        r = redis.Redis(host='127.0.0.1', port=6379)
        if len(date_start) == 0:
            date_start = r.hget(PRE_STOCK_BASIC+code, KEY_TimeToMarket)
        #date_start = '20150101'    
            date_start = datetime.datetime.strptime(str(date_start), "%Y%m%d")
        date_start = date_start.strftime("%Y-%m-%d") 
        date_end = date_end.strftime("%Y-%m-%d")
        
        keys = r.lrange(INDEX_STOCK_KLINE+code, 0, -1)
        
        listSeries = []
        for key in keys:
            if key > date_start and key < date_end:
                dict = r.hgetall(PRE_STOCK_KLINE+code +':'+ key)
                #_se = pd.Series(dict, index=[KEY_DATE, KEY_OPEN, KEY_HIGH, KEY_CLOSE, KEY_LOW, KEY_VOLUME,KEY_AMOUNT]) 
                _se = pd.Series(dict, index=[KEY_DATE, KEY_CLOSE]) 
                listSeries.append(_se)
        df = pd.DataFrame(listSeries)       
    elif DB_WAY == 'mysql':

        date_end = date_end.strftime("%Y-%m-%d")
        try:
            if len(date_start) == 0:
                sql = "select %s, %s from %s where %s <= '%s' order by %s asc" % \
                    (KEY_DATE, KEY_CLOSE, PRE_STOCK_KLINE+code,  \
                    KEY_DATE, date_end, KEY_DATE)
            else:
                sql = "select %s, %s from %s where %s >= '%s' and %s <= '%s' order by %s asc" % \
                    (KEY_DATE, KEY_CLOSE, PRE_STOCK_KLINE+code, KEY_DATE, date_start, \
                    KEY_DATE, date_end, KEY_DATE)

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
        if DB_WAY == 'csv':
        
            df = pd.DataFrame.from_csv(DownloadDir + TABLE_STOCKS_BASIC + '.csv')
            #se = df.loc[int(code)]
            se = df.ix[int(code)]
        
        elif DB_WAY == 'redis':
            r = redis.Redis(host='127.0.0.1', port=6379)
            se = pd.Series(r.hgetall(PRE_STOCK_BASIC+code))
        
        elif DB_WAY == 'mysql':
            sql = "select * from %s where %s='%s'" % (INDEX_STOCK_BASIC,KEY_CODE, code)
            df = pd.read_sql_query(sql, engine)
            se = df.ix[0]
            
    except Exception as e:
        print str(e)
        se = pd.Series()
            
    return se    
# 获取终止上市股票列表        
def get_stock_terminated():
    return ts.get_terminated()  

if __name__ == "__main__":
    print get_stock_k_line('000001') 
    #get_stock_info('000001')           