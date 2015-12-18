#!/usr/local/bin/python
#coding=utf-8

import datetime

import pandas as pd
import tushare as ts

from util.stockutil import getSixDigitalStockCode
from init import *
from util.commons import *


# 获取所有股票代码
def get_all_stock_codes():
    if DB_WAY == 'mysql':
        sql = 'select %s from %s' % (KEY_CODE, STOCK_BASIC_TABLE)
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
def get_stock_k_line(code, date_start='', date_end='', all_columns = False):

    if len(date_end) == 0:
        date_end=datetime.date.today().strftime("%Y-%m-%d")

    try:
        if len(date_start) == 0:
            sql = "select * from {0} where {1}='{2}' and {3} <= '{4}' order by {3} asc".format(
                STOCK_KLINE_TABLE, KEY_CODE, code,  KEY_DATE, date_end)
        else:
            sql = "select * from {0} where {1}='{2}' and {3} > '{4}' and {3} <= '{5}' order by {3} asc".format(
                STOCK_KLINE_TABLE, KEY_CODE, code,  KEY_DATE, date_start, date_end)

        df = pd.read_sql_query(sql, engine)
        return df
    except Exception as e:
        print str(e)
        return None

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
        #DB_WAY == 'mysql':
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