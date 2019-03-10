#!/usr/local/bin/python
#coding=utf-8
import time
from functools import wraps

# 补全股票代码(6位股票代码)
# input: int or string
# output: string
def getSixDigitalStockCode(code):
    strZero = ''
    for _ in range(len(str(code)), 6):
        strZero += '0'
    return strZero + str(code)

# 统计函数耗时
def fn_timer(function):
    @wraps(function)
    def function_timer(*args, **kwargs):
        t0 = time.time()
        result = function(*args, **kwargs)
        t1 = time.time()
        print("Total time running {}: {:.3f} seconds".format(function.__name__, t1-t0))
        return result
    return function_timer

# 将list分为多组
# 例：>>> print group_list(range(10), 3)
#      [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]
def group_list(li,block):
    size = len(li)
#     group=[]
#     for i in range(0,size,block):
#         group.append(li[i:i+block])
#     return group    
    return [li[i:i+block] for i in range(0,size,block)]




