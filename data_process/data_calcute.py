#coding=utf-8

__author__ = 'cbb'

import MySQLdb
import numpy as np
import pandas as pd
from data_get import *

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

#计算均线
def calcute_ma():
    codes = get_all_stock_codes()
    for code in codes:
        _calcute_ma(code)


def _calcute_ma(code):
    try:
        df = get_stock_k_line(code)
        close_prices = df['close'].get_values()
        print close_prices[-10:]

        print 'calcute ma'
        ma_short = pd.rolling_mean(close_prices, AVR_SHORT) #12
        ma_long = pd.rolling_mean(close_prices, AVR_LONG)   #40
        print ma_short[-10:]
        print ma_long[-10:]
        df['ma_'+str(AVR_SHORT)] = ma_short
        df['ma_'+str(AVR_LONG)] = ma_long

        print 'calcute ema'
        ema_short = pd.ewma(close_prices, span=AVR_SHORT)  #12
        ema_long = pd.ewma(close_prices, span=AVR_LONG)    #40
        print ema_short[-10:]
        print ema_long[-10:]
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
            print e



        #更新数据
        for ix, row in df.iterrows():
            sql_update = "update %s set %s=%f,%s=%f,%s=%f,%s=%f where date='%s'" % \
                (table_name, ma_s, row[ma_s], ma_l, row[ma_l],
                 ema_s, row[ema_s], ema_l,row[ema_l], \
                  row['date'])
            cursor.execute(sql_update)
            print table_name, row['date']

        #关闭数据库
        cursor.close()
        conn.commit()
        conn.close()

    except Exception, e:
        print e




if __name__ == "__main__":
    #_calcute_ma('600000')
    calcute_ma()