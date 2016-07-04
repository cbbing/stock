#coding: utf-8

"""
均线策略
"""

import pandas as pd

# MA指标择时
def select_time_ma(df_closeprice, ma_short=12, ma_long=40):
    """
    MA指标择时(简单均线SMA)
    :param df_closeprice:  DataFrame, 收盘价
    :param ma_short:
    :param ma_long:
    :return:
    """

    #SMA
    df_closeprice['ma_close_short'] = pd.rolling_mean(df_closeprice['close_price'], ma_short)
    df_closeprice['ma_close_long'] = pd.rolling_mean(df_closeprice['close_price'], ma_long)


    df_closeprice['signal'] = 0

    for ix, row in df_closeprice.iterrows():



    # if ema_close_short[-1] > ema_close_short[-2] and ema_close_short[-1] > ema_close_long[-1] \
    #                     and ema_close_short[-2] < ema_close_long[-2]:
    #     signal = SIGNAL_BUY
    # elif ema_close_long[-1] < ema_close_long[-2] and ema_close_short[-1] < ema_close_long[-1] \
    #                     and ema_close_short[-2] > ema_close_long[-2]:
    #     signal = SIGNAL_SALE

    # return signal