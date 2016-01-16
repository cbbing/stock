#!/usr/local/bin/python
#coding=utf-8

__author__ = 'bbchen'

import time
from functools import wraps

# 统计函数耗时
def fn_timer(function):
    @wraps(function)
    def function_timer(*args, **kwargs):
        t0 = time.time()
        result = function(*args, **kwargs)
        t1 = time.time()
        print ("Total time running %s: %s seconds" %
               (function.func_name, str(t1-t0))
               )
        return result
    return function_timer