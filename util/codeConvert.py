# -*- coding: utf8 -*-

import sys, time

#console stdout
def encode_wrap(str):
    try:
        sse = sys.stdout.encoding
        return str.encode(sse)
    except Exception, e:
        return str

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