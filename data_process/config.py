#coding:utf-8
__author__ = 'cbb'

import platform, os
from sqlalchemy import create_engine

#DB_WAY:数据存储方式 'csv'  # or 'mysql' or 'redis' or 'sqlite'
DB_WAY = 'mysql'
DB_USER = 'root'
DB_PWD = 'root' # or '123456' in win7
DB_NAME = 'stock'
DownloadDir = os.path.pardir + '/stockdata/' # os.path.pardir: 上级目录

# mysql Host
if platform.system() == 'Windows':
    host_mysql = 'localhost'
else:
    host_mysql = '101.200.183.216'
user_mysql = 'root'
pwd_mysql = 'root'
db_name_mysql = 'stock'

engine = create_engine('mysql+mysqldb://root:root@%s/stock' % host_mysql)


# 短均线， 长均线
AVR_SHORT = 12
AVR_LONG = 40