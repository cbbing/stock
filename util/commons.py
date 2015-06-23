#!/usr/local/bin/python
#coding=utf-8
# 定义的常量

import os

#DB_WAY:数据存储方式 'csv'  # or 'mysql'
DB_WAY = 'csv'
DB_USER = 'root'
DB_PWD = '1234' # or '123456' in win7
DB_NAME = 'test'
TABLE_STOCKS_BASIC = 'stock_basic_list'
DownloadDir = os.path.pardir + '/stockdata/' # os.path.pardir: 上级目录