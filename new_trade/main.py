#coding: utf-8

import tushare as ts
import pandas as pd

from util.date_convert import GetNowDate

def diagnosis_one_stock(code):
    """
    个股诊断
    :return:
    """

    # 获取股价
    df = get_stock_price(code, True)

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
    df['date'] = df.index

    if include_realtime_price:
        df_today = ts.get_today_all()
        df_code = df_today[df_today['code']==code]
        df_code = df_code[['trade']]
        df_code['date'] = GetNowDate()
        df_code.rename(columns={'trade': 'close'}, inplace=True)
        df = pd.concat([df, df_code], ignore_index=True)

    df.sort(columns='date', inplace=True)
    df = df.drop_duplicates(['date'])
    df.index = range(len(df))
    print '\n'
    # print df.head()
    print df.tail()
    return df

if __name__ == "__main__":
    get_stock_price('600000', True)
