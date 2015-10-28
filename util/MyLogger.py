# -*- coding: utf-8 -*-
#!/usr/bin/env python

__author__ = 'cbb'

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import logging
import logging.handlers
import ConfigParser
from codeConvert import *

#用字典保存日志级别
format_dict = {
   1 : logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(filename)s - %(funcName)s() - line:%(lineno)d - %(message)s'), #error
   2 : logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(filename)s - %(message)s'),  # debug
   3 : logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'),   #info
   4 : logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
   5 : logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
}


#日志系统， 既把日志输出到控制台， 还要写入日志文件
class Logger():
    def __init__(self, logname='', loglevel=1, logger='logger'):
        '''
           指定保存日志的文件路径，日志级别，以及调用文件
           将日志存入到指定的文件中
        '''

        # 创建一个logger
        self.logger = logging.getLogger(logger)
        self.logger.setLevel(logging.DEBUG)

        if len(logname) == 0:
            cf = ConfigParser.ConfigParser()
            cf.read('./config.ini')
            logname = cf.get('log','info_log_name')


        #hdlr=logging.basicConfig(logname,level=logging.NOTSET,format='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

        # 创建一个handler，用于写入日志文件
        #fh = logging.handlers.TimedRotatingFileHandler(logname, 'D')
        #fh.suffix = "%Y%m%d.log"
        fh = logging.FileHandler(logname)
        fh.setLevel(logging.DEBUG)

        # 再创建一个handler，用于输出到控制台
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        # 定义handler的输出格式
        #formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        formatter = format_dict[int(loglevel)]
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        # 给logger添加handler
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)


    def getlog(self):
        return self.logger

    #自定义
    def addLog(self, msg, level='info'):
        if level == 'info':
            self.logger.info(encode_wrap(msg))
        elif level == 'debug':
            self.logger.debug(encode_wrap(msg))
        elif level == 'error':
            self.logger.error(encode_wrap(msg))


#ErrorLogger = Logger(logname='./data/log/error.log', logger='error')
#InfoLogger = Logger(logname='./data/log/info.log', logger='info')

if __name__ == "__main__":



    logger = Logger()
    logger.addLog('百度')

