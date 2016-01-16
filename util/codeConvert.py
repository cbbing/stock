# -*- coding: utf8 -*-

import sys, time
import datetime

#console stdout
def encode_wrap(str):
    try:
        sse = sys.stdout.encoding
        return str.encode(sse)
    except Exception, e:
        return str

def str_qt_to_utf(qt_str):
    utf_str = unicode(qt_str.toUtf8(), 'utf-8', 'ignore')
    return utf_str

def str_to_datatime(str_time, format='%Y-%m-%d %H:%M:%S'):
    d = datetime.datetime.strptime(str_time, format)
    return d

def GetDate(timefrom1970):
    return time.strftime("%Y-%m-%d",time.localtime(timefrom1970))

def GetTime(timefrom1970):
    return time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(timefrom1970))

def GetNowTime():
    return time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))

def GetNowTime2():
    return time.strftime("%Y-%m-%d 00:00:00",time.localtime(time.time()))

def GetNowTim3():
    return time.strftime("%Y-%m-%d-%H-%M-%S",time.localtime(time.time()))

def GetNowDate():
    return time.strftime("%Y-%m-%d",time.localtime(time.time()))

# 规整化发表时间
def regularization_time(publish_time):
    now = GetNowDate()
    if '分钟前' in publish_time: # 22分钟前
        publish_time = publish_time.replace('分钟前','')
        publish_time = time.time() - int(publish_time)*60
        publish_time = time.strftime("%Y-%m-%d %H:%M",time.localtime(publish_time))
        publish_time = publish_time +  ':00'

    elif '今天' in publish_time:
        publish_time = publish_time.replace('今天', now) + ':00'

    elif '月' in publish_time:
        publish_time = publish_time.replace('月','-').replace('日','')
        publish_time = time.strftime("%Y-",time.localtime(time.time())) + publish_time + ':00'
    elif len(publish_time) == 5: # 形如14:58
        publish_time = now + " " + publish_time + ":00"
    elif len(publish_time) == 11: #形如09-29 12:38
        publish_time = time.strftime("%Y-",time.localtime(time.time())) + publish_time + ':00'
    elif len(publish_time) == 16: #形如2015-09-29 12:38
        publish_time = publish_time + ':00'


    return publish_time