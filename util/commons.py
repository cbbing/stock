#!/usr/local/bin/python
#coding=utf-8
# 定义的常量

import os

#DB_WAY:数据存储方式 'csv'  # or 'mysql' or 'redis'
DB_WAY = 'redis'
DB_USER = 'root'
DB_PWD = '1234' # or '123456' in win7
DB_NAME = 'test'
TABLE_STOCKS_BASIC = 'stock_basic_list'
DownloadDir = os.path.pardir + '/stockdata/' # os.path.pardir: 上级目录

# Redis

#基本信息表
PRE_STOCK_BASIC = 'stock_basic_info:' #股票基本信息的前缀
KEY_CODE = 'code'
KEY_NAME = 'name'
KEY_INDUSTRY = 'industry'
KEY_AREA = 'area'
KEY_TimeToMarket = 'timeToMarket'

#历史K线数据
PRE_STOCK_KLINE = 'kline:'
KEY_DATE = 'date'
KEY_OPEN = 'open'
KEY_HIGH = 'high'
KEY_CLOSE = 'close'
KEY_LOW = 'low'
KEY_VOLUME = 'volume'
KEY_AMOUNT = 'amount'

INDEX_STOCK_KLINE = 'index_kline:' # 索引 


