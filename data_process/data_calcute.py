#coding=utf-8

__author__ = 'cbb'

import sys
sys.path.append('C:\Code\stock-master')

import MySQLdb
import numpy as np
import pandas as pd
import datetime
from data_get import *


reload(sys)
sys.setdefaultencoding('utf-8')



#计算均线
def calcute_ma_all():
    codes = get_all_stock_codes()
    for code in codes:
        _calcute_ma(code)

# date_start:'2015-01-01'
# date_end: '2015-10-12'
def _calcute_ma(code, date_start='', date_end='', is_calcute_lastest=False):
    try:
        df = get_stock_k_line(code,date_start, date_end)
        close_prices = df['close'].get_values()

        infoLogger.logger.info(str(code) + '  ' + 'calcute ma')
        ma_short = pd.rolling_mean(close_prices, AVR_SHORT) #12
        ma_long = pd.rolling_mean(close_prices, AVR_LONG)   #40

        df[ 'ma_' + str(AVR_SHORT)] = ma_short
        df['ma_' + str(AVR_LONG)] = ma_long

        infoLogger.logger.info(str(code) + '  ' + 'calcute ema')
        ema_short = pd.ewma(close_prices, span=AVR_SHORT)  #12
        ema_long = pd.ewma(close_prices, span=AVR_LONG)    #40

        df['ema_'+str(AVR_SHORT)] = ema_short
        df['ema_'+str(AVR_LONG)] = ema_long

        df = df.replace(np.nan, 0)

        #写数据库

        #连接
        conn=MySQLdb.connect(host=host_mysql,user=user_mysql,passwd=pwd_mysql,db=db_name_mysql,charset="utf8")
        cursor = conn.cursor()

        # 增加列
        table_name = PRE_STOCK_KLINE + code
        ma_s = 'ma_' + str(AVR_SHORT)
        ma_l = 'ma_' + str(AVR_LONG)
        ema_s = 'ema_' + str(AVR_SHORT)
        ema_l = 'ema_' + str(AVR_LONG)
        try:
            sql = "alter table %s add %s double" % (table_name, ma_s)
            cursor.execute(sql)
            sql = "alter table %s add %s double" % (table_name, ma_l)
            cursor.execute(sql)
            sql = "alter table %s add %s double" % (table_name, ema_s)
            cursor.execute(sql)
            sql = "alter table %s add %s double" % (table_name, ema_l)
            cursor.execute(sql)
        except Exception, e:
            str_error = 'column exists'
            print ''

        # 按由近到远的顺序排序
        df = df.sort_index(by='date', ascending=False)

        count = 0

        #更新数据
        for ix, row in df.iterrows():
            sql_update = "update %s set %s=%f,%s=%f,%s=%f,%s=%f where date='%s'" % \
                (table_name, ma_s, row[ma_s], ma_l, row[ma_l],
                 ema_s, row[ema_s], ema_l,row[ema_l], \
                  row['date'])
            cursor.execute(sql_update)
            infoLogger.logger.info( table_name + ' ' + str(row['date']))

            count = count+1
            #只计算最后1个收盘
            if is_calcute_lastest and count >= 7:
                break

        #关闭数据库
        cursor.close()
        conn.commit()
        conn.close()

    except Exception, e:
        errorLogger.logger.error(str(code)+":"+date_start+" ~ "+date_end+str(e))

# 计算最近日期的均线
def calcute_ma_lastest_all():
    codes = get_all_stock_codes()

    for code in codes:
        if int(code) < 657:
            continue
        _calcute_ma_lastest(code)

# 计算最近日期的均线 (单个)
def _calcute_ma_lastest(code):

    d_avr_long = datetime.date.today() + datetime.timedelta(days=-180)
    d_today = datetime.date.today()
    date_start = d_avr_long.strftime('%Y-%m-%d')
    date_end = d_today.strftime('%Y-%m-%d')

    _calcute_ma(code, date_start, date_end, True)



if __name__ == "__main__":
    #_calcute_ma('600000', '2015-01-01', '2015-10-14', True)
    #calcute_ma_all()
    calcute_ma_lastest_all()
    #_calcute_ma_lastest('000033')