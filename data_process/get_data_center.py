#!/usr/local/bin/python
#coding=utf-8

import os
import datetime
import pandas as pd
from util.stockutil import getSixDigitalStockCode
import util.commons as commons
from data_to_sql import download_stock_kline

# 获取个股K线数据
# input:
# ->code: 股票代码
# output:
# -> DataFrame
def get_stock_k_line(code, date_start='', date_end=datetime.date.today()):
    #code = getSixDigitalStockCode(code)
    #fileName = 'h_kline_' + str(code) + '.csv'
    
    #df = None
    # 如果存在则直接取
#     if os.path.exists(commons.DownloadDir+fileName):
#         df = pd.DataFrame.from_csv(path=commons.DownloadDir+fileName)
#     # 不存在则立即下载
#     else:
    df = download_stock_kline(code, date_start, date_end)
    return df         