#coding:utf-8
__author__ = 'cbb'

import platform, os
from sqlalchemy import create_engine
from util.MyLogger import Logger
import pymysql
import datetime
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

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
host_mysql = 'localhost'
user_mysql = 'root'
pwd_mysql = '133499'
db_name_mysql = 'wealth_db'

engine = create_engine('mysql+mysqldb://%s:%s@%s/%s' % (user_mysql, pwd_mysql, host_mysql, db_name_mysql), connect_args={'charset':'utf8'})
class get_mysql(object):
    '''链接数据库，并根据提供的数据库名称和关键词信息创建一个表格，表格存在就不创建'''
    def __init__(self,dbname,key,citys):
        self.T = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d%H%M")
        self.dbname = dbname
        self.key = key
        if len(citys) == 1:
            self.city = citys[0]
        elif len(citys) > 1:
            self.city = "&".join(citys)
        else:
            self.city = ""
        self.table_name = "{}_{}_{}".format(self.T,self.key,self.city)
        self.conn = pymysql.Connect(
            host="localhost",
            port=3306,
            user='root',
            password='133499',
            db=self.dbname,
            charset='utf8'
        )
        self.cursor = self.conn.cursor()
        # 直接创建一个表格
        self.create_table()

    # 创建表格的函数，表格名称按照时间和关键词命名
    def create_table(self):
        sql = '''CREATE TABLE `{tbname}`(
        {job_name} varchar(100) not null,
        {gs_name} varchar(100),
        {salary} char(20),
        {job_site} char(20),
        {create_date} char(20),
        {job_link} varchar(100),
        {gs_link} varchar(100)
        )'''
        try:
            self.cursor.execute(sql.format(tbname=self.table_name,job_name="职位名称",gs_name="公司名称",salary="薪资",
                                       job_site="工作地点",create_date="发布时间",job_link="招聘链接",gs_link="公司链接"))
        except Exception as e:
            print("创建表格失败，表格可能已经存在！",e)
        else:
            self.conn.commit()
            print("成功创建一个表格，名称是{}".format(self.table_name))

    # 插入信息函数，每次插入一条信息，插入信息失败会回滚
    def insert_data(self,data):
        '''插入数据，不成功就回滚操作'''
        sql = '''INSERT INTO `{}` VALUES('{}','{}','{}','{}','{}','{}','{}')'''
        try:
            self.cursor.execute(sql.format(self.table_name,data["job_name"],data["gs_name"],data["salary"],data["job_site"],
                                           data["create_date"],data["job_link"],data["gs_link"]))
        except Exception as e:
            self.conn.rollback()
            print("插入信息失败，原因：",e)
        else:
            self.conn.commit()
            print("成功插入一条信息")

    def close_mytable(self):
        '''关闭游标和断开链接，数据全部插入后必须执行这个操作'''
        self.cursor.close()
        self.conn.close()

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
infoLogger = Logger(logname='../Log/info.log', logger='I')
errorLogger = Logger(logname='../Log/error.log', logger='E')

#配置文件 位置
config_file_path = '../config.ini'