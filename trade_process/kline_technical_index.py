#coding=utf-8
"""
    K线图 - 技术指标
    http://kekefund.com/2015/12/10/japan-candle-diagram-technique/
"""

import wrapcache
from tqdm import tqdm

from data_process.data_get import get_all_stock_codes, get_stock_k_line

@wrapcache.wrapcache(timeout=24*60*60)
def line_hammer_and_hang(code, df_code):
    """
    锤子线(底部反转) | 上吊线(顶部反转)
    :param df_code: 一只股票代码的DataFrame
    :return:
    """

    #print df_code[:3][['code', 'date','open','high','close','close','low']]

    dates_up = [] #锤子线
    dates_down = []   #上吊线
    for ix, row in df_code.iterrows():
        if ix - 3 < 0:
            continue

        len_yingxian_down = min(row['close'], row['open']) - row['low'] #下影线长度
        len_yingxian_up = row['high'] - max(row['close'], row['open'])  #上影线长度
        len_solid = abs(row['close'] - row['open'])  # 实体线高度

        if len_yingxian_down >= 2 * len_solid and len_yingxian_up < len_solid * 0.1:
            trend = _judge_trend(df_code.ix[ix-3:ix+1])
            if trend == -1: # 下降趋势
                dates_up.append(str(row['date']))
            elif trend == 1: # 上升趋势
                dates_down.append(str(row['date']))

    code_dict = {}
    code_dict[code] = {'up': dates_up, 'down':dates_down}

    return code_dict

def shape_devour(code, df_code):
    """
    吞没形态
    --- 看涨吞没形态
    --- 看跌吞没形态
    :param code:
    :param df_code:
    :return:
    """

    dates_up = []  #看涨
    dates_down = []   #看跌

    for ix, row in df_code.iterrows():
        if ix - 3 < 0:
            continue

        #判断趋势
        trend = _judge_trend(df_code.ix[ix-3:ix])

        #先判断形态
        row_pre = df_code.ix[ix-1]

        # 1,看涨吞没形态
        if trend == -1 and \
                row_pre.close < row_pre.open and \
                row.close > row_pre.open and \
                row.open < row_pre.close:
            print row_pre
            print row
            dates_up.append(str(row['date']))

        # 2,看跌吞没形态
        if trend == 1 and \
                (row_pre.close > row_pre.open) and \
                row.close < row_pre.open and \
                row.open > row_pre.close:
            dates_down.append(str(row['date']))

    code_dict = {}
    code_dict[code] = {'up': dates_up, 'down':dates_down}
    #print code_dict
    return code_dict

def shape_dark_cloud_cover_top(code, df_code):
    """
    乌云盖顶形态(顶部反转) | 透刺形态(底部反转)
    :param code:
    :param df_code:
    :return:
    """

    dates_up = []  #看涨
    dates_down = []   #看跌

    for ix, row in df_code.iterrows():
        if ix - 5 < 0:
            continue

        #判断趋势
        pct_changes = df_code.ix[ix-5:ix].close.pct_change()

        if len(pct_changes[pct_changes > 0]) >= 3: # 必须近期总体趋势是向上的

            row_pre = df_code.ix[ix-1]
            if row_pre.close > row_pre.open and row.close < row.open: # 前一天是坚挺的白色实体, 当前天是黑色实体
                if row.open > row_pre.high + (row_pre.close + row_pre.open) * 0.2: # 当前天的开盘价超过了(前一天的最高价 + 系数)
                    if row.close < (row_pre.open + row_pre.close)/2 and row.close > row_pre.open: # 当前天的收盘价下穿到前一天白色实体的50%
                        dates_down.append(str(row.date))

        elif len(pct_changes[pct_changes < 0]) >= 3: # 必须近期总体趋势是向下的

            row_pre = df_code.ix[ix-1]
            if row_pre.close < row_pre.open and row.close > row.open: # 前一天是黑色实体, 当前天是白色实体
                if row.open < row_pre.low - (row_pre.close + row_pre.open) * 0.2: # 当前天的开盘价低于(前一天的最低价 - 系数)
                    if row.close > (row_pre.open + row_pre.close)/2 and row.close < row_pre.open: # 当前天的收盘价上穿到前一天白色实体的50%
                        dates_up.append(str(row.date))
    code_dict = {}
    code_dict[code] = {'up': dates_up, 'down':dates_down}
    #print code_dict
    return code_dict

def shape_morning_and_evening_star(code, df_code):
    """
    启明星形态(底部反转) | 黄昏星形态(顶部反转)
    含十字线形态
    :return: dict
    """
    dates_up = []  #看涨
    dates_down = []   #看跌

    len_df = len(df_code)
    for ix, row in df_code[1:len_df-1].iterrows():

        row_pre = df_code.ix[ix-1]
        row_post = df_code.ix[ix+1]

        if abs(row.open - row.close)/row.open < 0.02: # 星线 或 十字线
            if row_pre.close < row_pre.open and (row_pre.open-row_pre.close)/row_pre.open > 0.03: #前一天是黑色实体 且跌幅>3%
                if max(row.open, row.close) < min(row_pre.close, row_pre.open): #当前天的实体部分与前一天的实体形成价格跳空
                    if row_post.close > row_post.open and row_post.close > row_pre.close: #后一天是白色实体 且收盘价向上推进到前一天的黑色实体之内
                        dates_up.append(str(row.date))

            elif row_pre.close > row_pre.open and (row_pre.close-row_pre.open)/row_pre.open > 0.03: #前一天是白色实体 且涨幅>3%
                if min(row.open, row.close) > max(row_pre.close, row_pre.open): #当前天的实体部分与前一天的实体形成价格跳空
                    if row_post.close < row_post.open and row_post.close < row_pre.close: #后一天是黑色实体 且收盘价向下推进到前一天的白色实体之内
                        dates_down.append(str(row.date))


    code_dict = {}
    code_dict[code] = {'up': dates_up, 'down':dates_down}
    #print code_dict
    return code_dict

def shape_meteor_and_invertedhammer_star(code, df_code):
    """
    流星形态 | 倒锤子线
    -- 非主要反转信号
    :return: dict
    """
    dates_up = []  #看涨
    dates_down = []   #看跌

    len_df = len(df_code)
    for ix, row in df_code[5:len_df-1].iterrows():

        row_pre = df_code.ix[ix-1]
        row_post = df_code.ix[ix+1]
        pct_changes = df_code.ix[ix-5:ix].close.pct_change()

        #定义流星: 1,流星实体部分较小; 2,白色或黑色皆可#流星上影线较长; 3,下影线几乎没有(长度小于实体的1/10)
        meteor_star = abs(row.open - row.close)/row.open < 0.02 and \
                        row.high-max(row.open, row.close) > abs(row.open - row.close) * 2 and \
                        abs(row.low-min(row.open, row.close)) < abs(row.open - row.close) * 0.1
        if meteor_star:
            #流星
            if len(pct_changes[pct_changes > 0]) >= 3: # 必须近期总体趋势是向上的
                if min(row.open, row.close) > max(row_pre.close, row_pre.open): # 当前天的实体部分与前一天的实体形成价格跳空
                    if max(row_post.open, row_post.close) < min(row.close, row.open) or \
                            (row_post.open - row_post.close)/row_post.open > 0.03: # 后一天向下跳空 或 跌幅>3%
                        dates_down.append(str(row.date))
            #倒锤子线
            if len(pct_changes[pct_changes < 0]) >= 3: # 必须近期总体趋势是向下的
                if max(row.open, row.close) < min(row_pre.close, row_pre.open): # 当前天的实体部分与前一天的实体形成价格跳空
                    if min(row_post.open, row_post.close) > max(row.close, row.open) or \
                            (row_post.close - row_post.open)/row_post.open > 0.03: # 后一天向上跳空 或 涨幅>3%
                        dates_up.append(str(row.date))


    code_dict = {}
    code_dict[code] = {'up': dates_up, 'down':dates_down}
    #print code_dict
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
    codes = list(get_all_stock_codes())
    codes.reverse()
    codes = ['000725']
    result_list = []
    for code in tqdm(codes):
        df = get_stock_k_line(code, date_start='2016-01-01')

        code_dict = line_hammer_and_hang(code, df)
        result_list.append(code_dict)

        code_dict = shape_dark_cloud_cover_top(code, df)
        result_list.append(code_dict)

        code_dict = shape_devour(code, df)
        result_list.append(code_dict)

        code_dict = shape_morning_and_evening_star(code, df)
        result_list.append(code_dict)

        code_dict = shape_meteor_and_invertedhammer_star(code, df)
        result_list.append(code_dict)



    for result in result_list:
        for code, d in result.items():
            if d['up']:
                print code, " up:", d['up']

    for result in result_list:
        for code, d in result.items():
            if d['down']:
                print code, " down:", d['down']

    print 'end'
if __name__ == "__main__":
    run()

