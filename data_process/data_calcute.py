#coding=utf-8

__author__ = 'cbb'

import sys
sys.path.append('C:\Code\stock-master')
reload(sys)
sys.setdefaultencoding('utf-8')

import MySQLdb
import numpy as np
import pandas as pd
import datetime
from tqdm import tqdm
from multiprocessing.dummy import Pool as ThreadPool
import wrapcache

from data_get import *







#计算均线
def calcute_ma_all():
    codes = get_all_stock_codes()
    # for code in tqdm(codes):
    #     _calcute_ma(code)

    pool = ThreadPool(processes=4)
    pool.map(_calcute_ma, codes)
    pool.close()
    pool.join()

# date_start:'2015-01-01'
# date_end: '2015-10-12'
def _calcute_ma(code, date_start='', date_end='', is_calcute_lastest=False):
    try:
        df = get_stock_k_line_if_ma_is_null(code)
        if df is None:
            return
        close_prices = df['close'].get_values()

        print str(code) + '  ' + 'calcute ma'
        ma_short = pd.rolling_mean(close_prices, AVR_SHORT) #12
        ma_long = pd.rolling_mean(close_prices, AVR_LONG)   #40

        df[ 'ma_' + str(AVR_SHORT)] = ma_short
        df['ma_' + str(AVR_LONG)] = ma_long

        print str(code) + '  ' + 'calcute ema'
        ema_short = pd.ewma(close_prices, span=AVR_SHORT)  #12
        ema_long = pd.ewma(close_prices, span=AVR_LONG)    #40

        df['ema_'+str(AVR_SHORT)] = ema_short
        df['ema_'+str(AVR_LONG)] = ema_long

        df = df.replace(np.nan, 0)

        #写数据库

        # 增加列
        table_name =STOCK_KLINE_TABLE
        ma_s = 'ma_' + str(AVR_SHORT)
        ma_l = 'ma_' + str(AVR_LONG)
        ema_s = 'ema_' + str(AVR_SHORT)
        ema_l = 'ema_' + str(AVR_LONG)
        # try:
        #     sql = "alter table %s add %s double" % (table_name, ma_s)
        #     engine.execute(sql)
        #     sql = "alter table %s add %s double" % (table_name, ma_l)
        #     engine.execute(sql)
        #     sql = "alter table %s add %s double" % (table_name, ema_s)
        #     engine.execute(sql)
        #     sql = "alter table %s add %s double" % (table_name, ema_l)
        #     engine.execute(sql)
        # except Exception, e:
        #     str_error = 'column exists'
        #     print ''

        # 按由近到远的顺序排序
        df = df.sort_index(by='date', ascending=False)

        count = 0

        #更新数据
        for ix, row in df.iterrows():
            print row
            if row[ma_l] == 0 or row[ema_l] == 0:
                continue

            sql_update = "update %s set %s=%f,%s=%f,%s=%f,%s=%f where date='%s' and %s='%s'" % \
                (table_name, ma_s, row[ma_s], ma_l, row[ma_l],
                 ema_s, row[ema_s], ema_l,row[ema_l], \
                  row['date'], KEY_CODE, code)
            print sql_update
            engine.execute(sql_update)
            print table_name + ' ' + str(row['date'])

            count = count+1
            #只计算最后1个收盘
            if is_calcute_lastest and count >= 7:
                break

    except Exception, e:
        print (str(code)+":"+date_start+" ~ "+date_end+str(e))

# 计算最近日期的均线
def calcute_ma_lastest_all():
    codes = get_all_stock_codes()

    for code in codes:
        _calcute_ma_lastest(code)

# 计算最近日期的均线 (单个)
def _calcute_ma_lastest(code):

    d_avr_long = datetime.date.today() + datetime.timedelta(days=-180)
    d_today = datetime.date.today()
    date_start = d_avr_long.strftime('%Y-%m-%d')
    date_end = d_today.strftime('%Y-%m-%d')

    _calcute_ma(code, date_start, date_end, True)

@wrapcache.wrapcache(timeout=6*60*60)
def calcute_ma(df, avr_short=12, avr_long=40):
    """
    计算ma, ema
    :param df:
    :return:
    """
    if len(df) == 0:
        return

    # print "{} calcute ma".format(df.ix[0,'code'])
    df['ma_' + str(avr_short)] = pd.rolling_mean(df['close'], avr_short)  # 12
    df['ma_' + str(avr_long)] = pd.rolling_mean(df['close'], avr_long)  # 40


    # print "{} calcute ema".format(df.ix[0, 'code'])
    df['ema_' + str(avr_short)] = pd.ewma(df['close'], span=avr_short)  # 12
    df['ema_' + str(avr_long)] = pd.ewma(df['close'], span=avr_long)  # 40

    df = df.replace(np.nan, 0)
    return df



if __name__ == "__main__":
    #_calcute_ma('600000', '2015-01-01', '2015-10-14', True)
    calcute_ma_all()
    #calcute_ma_lastest_all()
    #_calcute_ma_lastest('000033')