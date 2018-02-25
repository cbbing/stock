#!/usr/local/bin/python
#coding=utf-8

import pandas as pd
import tushare as ts

from init import *
from config.settings import *
from util.codeConvert import *
from util.helper import fn_timer
import wrapcache


# 获取所有股票代码
@wrapcache.wrapcache(timeout=8*60*60)
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
@wrapcache.wrapcache(timeout=8*60*60)
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

@fn_timer
def get_stock_k_line_if_ma_is_null(code):

    sql = 'SELECT min(date) as date FROM {table} where code={code} and ma_12 is NULL'.format(table=STOCK_KLINE_TABLE, code=code)
    df = pd.read_sql_query(sql, engine)

    d_end=datetime.datetime.today()
    #date_end =d_end.strftime('%Y-%m-%d')
    if len(df) > 0:
        date_start = df.ix[0, 'date']
        if date_start is None:
            return None

        date_start = str(date_start)[:10]
        d_start = str_to_datatime(date_start, '%Y-%m-%d')
        delta = d_end - d_start
        days = delta.days + AVR_LONG + 1

    try:
        sql = "select * from {table} where code='{code}' order by date desc limit {count}".format(
               table=STOCK_KLINE_TABLE, code=code,  count=days)

        df = pd.read_sql_query(sql, engine)
        df = df.sort_index(by='date', ascending=True)
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