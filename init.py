#coding:utf-8
__author__ = 'cbb'

import platform, os
from sqlalchemy import create_engine
from util.MyLogger import Logger

#DB_WAY:数据存储方式 'csv'  # or 'mysql' or 'redis' or 'sqlite'
DB_WAY = 'mysql'
DB_USER = 'root'
DB_PWD = 'root' # or '123456' in win7
DB_NAME = 'stock'
DownloadDir = os.path.pardir + '/stockdata/' # os.path.pardir: 上级目录

# mysql Host
# if platform.system() == 'Windows':
#     host_mysql = 'localhost'
# else:
#     host_mysql = '101.200.183.216'
host_mysql = 'rdsw5ilfm0dpf8lee609.mysql.rds.aliyuncs.com'
user_mysql = 'licj'
pwd_mysql = 'AAaa1234'
db_name_mysql = 'wealth_db'

engine = create_engine('mysql+mysqldb://%s:%s@%s/%s' % (user_mysql, pwd_mysql, host_mysql, db_name_mysql), connect_args={'charset':'utf8'})


# 短均线， 长均线
AVR_SHORT = 12
AVR_LONG = 40

#买卖标记
SIGNAL_BUY = 1  #买
SIGNAL_SALE = -1 #卖
SIGNAL_DEFAULT = 0

#阈值
Threshold_Buy_Count = 3
Threshold_Sale_Count = 2

#日志设置
from util.MyLogger import Logger
#infoLogger = Logger(logname='../Log/info.log', logger='I')
#errorLogger = Logger(logname='../Log/error.log', logger='E')

#配置文件 位置
config_file_path = '../config.ini'