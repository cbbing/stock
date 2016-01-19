#coding=utf-8
"""
K线图 - 技术指标
"""

import wrapcache
from tqdm import tqdm

from data_process.data_get import get_all_stock_codes, get_stock_k_line

@wrapcache.wrapcache(timeout=24*60*60)
def line_hammer_or_hang(code, df_code):
    """
    获取锤子线与上吊线
    :param df_code: 一只股票代码的DataFrame
    :return:
    """

    #print df_code[:3][['code', 'date','open','high','close','close','low']]

    dates_hammer = [] #锤子线
    dates_hang = []   #上吊线
    for ix, row in df_code.iterrows():
        if ix - 3 < 0:
            continue

        len_yingxian_down = min(row['close'], row['open']) - row['low'] #下影线长度
        len_yingxian_up = row['high'] - max(row['close'], row['open'])  #上影线长度
        len_solid = abs(row['close'] - row['open'])  # 实体线高度

        if len_yingxian_down >= 2 * len_solid and len_yingxian_up < len_solid * 0.1:
            trend = _judge_trend(df_code.ix[ix-3:ix+1])
            if trend == -1: # 下降趋势
                dates_hammer.append(str(row['date']))
            elif trend == 1: # 上升趋势
                dates_hang.append(str(row['date']))

    code_dict = {}
    code_dict[code] = {'hammer': dates_hammer, 'hang':dates_hang}

    return code_dict

def form_devour(code, df_code):
    """
    吞没形态
    :param code:
    :param df_code:
    :return:
    """

    dates_devour_raise = []  #看涨
    dates_devour_fall = []   #看跌

    for ix, row in df_code.iterrows():
        if ix - 3 < 0:
            continue

        #判断趋势
        trend = _judge_trend(df_code.ix[ix-3:ix])

        #先判断形态
        row_pre = df_code.ix[ix-1]

        # 1,看涨吞没形态
        if trend == -1 and \
                (row_pre.close < row_pre.open or abs(row_pre.close-row_pre.open)/row_pre.close <= 0.01) and \
                row.close > row_pre.open and \
                row.open < row_pre.close:
            print row_pre
            print row
            dates_devour_raise.append(str(row['date']))

        # 2,看跌吞没形态
        if trend == 1 and \
                (row_pre.close > row_pre.open or abs(row_pre.close-row_pre.open)/row_pre.close <= 0.01) and \
                row.close < row_pre.open and \
                row.open > row_pre.close:
            dates_devour_fall.append(str(row['date']))

    code_dict = {}
    code_dict[code] = {'raise': dates_devour_raise, 'fall':dates_devour_fall}
    print code_dict
    return code_dict


# 辅助函数
def _judge_trend(df_code):
    """
    判断收盘价趋势
    :param df_code:
    :return: 1:上升; -1:下降; 0:震荡
    """
    pct_changes = df_code.close.pct_change()

    if len(pct_changes[pct_changes > 0]) == 0: # 下降趋势
        return -1
    elif len(pct_changes[pct_changes < 0]) == 0: # 上升趋势
        return 1
    else:
        return 0

def run():
    codes = get_all_stock_codes()
    codes = ['000591', '000611']
    for code in tqdm(codes):
        df = get_stock_k_line(code, date_start='2015-10-01')
        #code_dict = line_hammer_or_hang(code, df)
        code_dict = form_devour(code, df)

        for code, d in code_dict.items():
            # if d['hammer']:
            #     print code, " hammer:", d['hammer']
            if d['raise']:
                print code, " raise:", d['raise']

if __name__ == "__main__":
    run()

