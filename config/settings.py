#!/usr/local/bin/python
#coding=utf-8
# 定义的常量

import os

##################################
# Redis

#基本信息表
PRE_STOCK_BASIC = 'stock_basic_info:' #股票基本信息的前缀
KEY_CODE = 'code'
KEY_NAME = 'name'
KEY_INDUSTRY = 'industry'
KEY_AREA = 'area'
KEY_PE = 'pe' #市盈率
KEY_EPS = 'eps' #每股收益
KEY_PB = 'pb' #市净率
KEY_TimeToMarket = 'timeToMarket'

#历史K线数据
PRE_STOCK_KLINE = 'kline_'
#PRE_STOCK_KLINE_Sqlite = 'kline_' # sqlite 不支持 ：，改成_
KEY_DATE = 'date'
KEY_OPEN = 'open'
KEY_HIGH = 'high'
KEY_CLOSE = 'close'
KEY_LOW = 'low'
KEY_VOLUME = 'volume'
KEY_AMOUNT = 'amount'



##################################

DATABASES = {
    'tushare': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'stock',
        'USER': 'ts_w',
        'PASSWORD': 'G8y64mPyG9r@',
        'HOST': "sh-cdb-s089fj1s.sql.tencentcdb.com",
        'PORT': 63405,
    },
    'strategy': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'stock',
        'USER': 'ts_r',
        'PASSWORD': '9f#482KrJc6w',
        'HOST': "sh-cdb-s089fj1s.sql.tencentcdb.com",
        'PORT': 63405,
    }
}

STOCK_BASIC_TABLE = 'stock_basic_info' # 索引：获取所有股票
STOCK_KLINE_TABLE = 'stock_kline' # 索引：获取单只股票的所有日期的K线(前复权,后复权) #stock_kline_all

