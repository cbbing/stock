#coding: utf-8

import tushare as ts

def diagnosis_one_stock(code):
    """
    个股诊断
    :return:
    """


    # 均线指标


    # K线提示

def get_stock_price(code, include_realtime_price):
    """
    获取个股股价
    :param code: 股票代码
    :param include_realtime_price: 是否含实时股价
    :return:
    """

    # 获取历史股价
    df = ts.get_hist_data(code)
    df = df[['close']]

    if include_realtime_price:
        df_today = ts.get_today_all()

