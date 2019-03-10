#coding: utf-8

"""
止盈止损策略
"""

import pandas as pd
import copy
from operator import itemgetter

from py3.config.db_config import get_r_engine
from util.date_convert import GetNowDate
from data_process.online_data import get_real_price_dataframe

#限价止损
def stop_loss_by_price():
    """
    限价止损
    :return:
    """
    #查询持仓股票
    symbolAccount = SymbolAccount()
    symbolAccount.init_position_from_db()

    threshold_profit_open = 0.08 #止盈开启阈值
    threshold_profit_pretect = 0.02 #止盈保护阈值
    threshold_loss_pretect = 0.1 #止损保护阈值

    judgements = []

    #计算持仓股票的最初价格
    for symbol in symbolAccount.avail_secpos.keys():
        orders = symbolAccount.order_history[symbol]
        if len(orders) == 0:
            continue

        trade_date_begin = orders[0][0]

        #止盈保护
        close_prices = get_close_prices(symbol, trade_date_begin[:10], GetNowDate())
        if len(close_prices) < 1:
            continue

        close_price_begin = close_prices[0]
        realtime_price = get_realtime_price(symbol)
        if realtime_price == -1:
            continue

        if max(close_prices) >= (1 + threshold_profit_open)*close_price_begin: #止盈策略启动
            max_price = max(close_prices)
            if realtime_price <= (1 - threshold_profit_pretect) * max_price:
                #符合止盈策略,卖出
                reason = '符合止盈策略:相比最高价,下跌了{:.2}%'.format((max_price - realtime_price) / max_price * 100)
                symbolAccount.order(symbol, symbolAccount.avail_secpos[symbol], realtime_price, GetNowDate())
                judgements.append((symbol, -1, reason))

        elif realtime_price <= (1 - threshold_loss_pretect) * close_price_begin:
            #符合止损策略,卖出
            down = (close_price_begin-realtime_price)/close_price_begin*100
            reason = '符合止损策略:相比成本价,下跌了{:.2f}%'.format(down)
            symbolAccount.order(symbol, symbolAccount.avail_secpos[symbol], realtime_price, GetNowDate())
            judgements.append((symbol, -1, reason))

    return judgements




class SymbolAccount():
    """
    股票账户类
    """

    def __init__(self, account=100000):
        self.account = account #初始资金
        self.cash = self.account
        self.avail_secpos = {} # 字典，键为证券代码，值为持有的证券数量, {'000001': 100, '600000': 100}
        self.order_history = {} #dict, {symbol:000001, [(order_time:2016-07-11, , order_amount:100, order_price)]} , order_amount为正时买入,为负时卖出
        self.position_history = [] # 持仓历史[2016-07-11, cash, {'600000':100, '600031':300}]

        self.engine = get_r_engine()

    def init_position_from_db(self):
        """
        从数据库初始化持仓情况
        :return:
        """
        sql = "SELECT * FROM security_transaction order by trading_date asc"
        df = pd.read_sql(sql, self.engine)
        #剩余现金
        if len(df):
            self.cash = df['cash'].get_values()[-1]

        for code in df['code'].drop_duplicates():
            df_code = df[df['code'] == code]
            self.avail_secpos[code] = df_code['trade_count'].sum()

            self.order_history.setdefault(code, [])
            for _, row in df_code.iterrows():
                self.order_history[code].append([str(row['trade_time']), row['trade_count'], row['trade_price']])





    def order(self, smybol, amount, price, trade_date):
        """

        Parameters
        ----------
        smybol: 股票代码
        amount: 数量, 正数为买入,负数为卖出
        price: 下单价格
        trade_date: 下单日期

        Returns: True,成功; False,失败
        -------

        """
        self.avail_secpos.setdefault(smybol, 0)
        self.order_history.setdefault(smybol, [])

        if amount > 0: # 买入
            if amount * price < self.cash:
                self.cash -= amount * price
                self.avail_secpos[smybol] += amount
                self.order_history[smybol].append([str(trade_date)[:10], amount, price])
            else:
                return False

        else: #卖出
            if abs(amount) <= self.avail_secpos[smybol]:
                self.cash += abs(amount) * price
                self.avail_secpos[smybol] += amount
                self.order_history[smybol].append([str(trade_date)[:10],amount, price])

        for smybol in self.avail_secpos.keys():
            if self.avail_secpos[smybol] == 0: #删除持仓为0的股票
                del self.avail_secpos[smybol]

        self.position_history.append([trade_date, self.cash, copy.deepcopy(self.avail_secpos)])


    # def order_pct(self, smybol, pct, price):
    #     """
    #
    #     Parameters
    #     ----------
    #     smybol: 股票代码
    #     pct: 买入比例
    #     price: 买入价格
    #
    #     Returns
    #     -------
    #
    #     """
    #     pass


    def get_current_account(self, current_date):
        """
        获取当前时间的持仓市值
        Parameters
        ----------
        current_date: 当前日期

        Returns
        -------

        """

        smybol_market_values = 0
        for symbol in self.avail_secpos.keys():

            # 获取股票价格
            close_hfq = get_close_price(symbol, current_date)
            if close_hfq == -1:
                msg = "{},{},get code close_price error!".format(symbol, current_date)
                # raise Exception(msg)
                print(msg)
                return 0

            smybol_market_values += close_hfq * self.avail_secpos[symbol]

        return smybol_market_values + self.cash

    def get_sorted_symbols_by_return_rate(self, trade_date):
        """
        持仓股票按收益率排序
        Returns
        -------

        """
        smybol_rate_list = []
        for smybol in self.order_history.keys():
            #单只股票持仓成本
            total_count = 0
            total_cost = 0.0
            for one_order in self.order_history[smybol]:
                total_count += one_order[1]
                total_cost += one_order[1] * one_order[2]
            if total_count == 0:
                continue

            aver_price = total_cost/total_count #平均持仓成本
            now_price = get_close_price(smybol, trade_date)
            smybol_rate_list.append((smybol, (now_price-aver_price)/aver_price))

        smybol_rate_list = sorted(smybol_rate_list, key=itemgetter(1), reverse=True)
        return smybol_rate_list

    def get_all_order_history_by_date(self):
        orders = []
        for smybol in self.order_history.keys():
            smybol_orders = self.order_history[smybol]
            smybol_orders = [[smybol] +one for one in smybol_orders]
            orders.extend(smybol_orders)
        orders = sorted(orders, key =lambda x : x[1])
        print(orders[:3])
        print(orders[-3:])
        return orders

    def calcute_maximun_drawdown(self):
        """
        计算最大回撤
        Returns
        -------
        """

        jingzhi_list = self.get_jingzhi_daliy()

        if len(jingzhi_list) >= 2:
            jingzhi_list_sorted = sorted(jingzhi_list, key=lambda x : x[1], reverse=True)
            max_vale = jingzhi_list_sorted[0][1]
            max_value_date = jingzhi_list_sorted[0][0]
            jingzhi_list_after = [jingzhi for jingzhi in jingzhi_list if jingzhi[0] > max_value_date]
            jingzhi_list_sorted = sorted(jingzhi_list, key=lambda x : x[1])
            min_value = jingzhi_list_sorted[0][1]

            max_drawdown = (max_vale-min_value)/max_vale * 100.0
            return max_drawdown

        return 0

    def get_jingzhi_daliy(self):
        """
        获取每日净值
        Returns
        -------
        """
        if len(self.position_history) < 2:
            return []

        # 持仓起止日期范围
        rng = pd.date_range(self.position_history[0][0], self.position_history[-1][0], freq='D')
        jingzhi_list = []

        for trade_date in rng:
            # 获取现金,持仓股票及数量
            position = self.get_position_by_trade_date(trade_date)
            if not position:
                continue

            # 此刻的持仓成本
            cash = position[1]  # cash
            avail_secpos = position[2]
            is_trade_date = True

            for smybol in avail_secpos.keys():
                close_price = get_close_price(smybol, trade_date)
                if close_price == -1:
                    is_trade_date = False
                    break
                cash += avail_secpos[smybol] * close_price

            if not is_trade_date:
                continue

            jingzhi_list.append([trade_date, cash * 1.0 / self.account])

        return jingzhi_list

    def get_position_by_trade_date(self, trade_date):
        """
        获取持仓股票及数量
        Parameters
        ----------
        trade_date

        Returns
        -------
        """
        for i in range(1,len(self.position_history)):
            # print type(trade_date.to_datetime()), str(position[0])
            if str(trade_date.to_datetime()) >= str(self.position_history[i-1][0]) and str(trade_date.to_datetime()) < str(self.position_history[i][0]):
                return self.position_history[i-1]

        # if len(self.position_history):
        #     return self.position_history[-1]
        return None

def get_close_price(symbol, trade_date):
    """
    获取后复权价格
    Parameters
    ----------
    symbol
    trade_date

    Returns
    -------

    """
    engine = get_r_engine()
    if len(symbol) == 6:
        sql = "SELECT close FROM hq_db.stock_kline_fq where code='{}' and date>='{}' order by date asc".format(symbol, trade_date)
    else:
        sql = "SELECT close FROM hq_db.stock_kline_fq where code='{}' and date>='{}' order by date asc".format(
            symbol, trade_date)
    df = pd.read_sql(sql, engine)
    closes = df['close'].get_values()
    if len(closes) == 0:
        # raise Exception("get code close_price error!")
        return -1

    return closes[0]


def get_close_prices(symbol, trade_date_begin, trade_date_end):

    """
    获取前复权价格序列
    :param symbol:
    :param trade_date_begin:
    :param trade_date_end:
    :return:
    """
    engine = get_r_engine()
    if len(symbol) == 6:
        sql = "SELECT date, close FROM hq_db.stock_kline_fq where code='{}' and date>='{}' and date <='{}' order by date asc".format(
                symbol, trade_date_begin, trade_date_end)
    else:
        sql = "SELECT date, close FROM hq_db.stock_kline_fq where code='{}' and date>='{}' and date <='{}'  order by date asc".format(
            symbol, trade_date_begin, trade_date_end)
    df = pd.read_sql(sql, engine)
    closes = df['close'].get_values()

    return closes

def get_realtime_price(symbol):
    """
    获取实时股价
    :param symbol:
    :return:
    """
    try:
        df = get_real_price_dataframe()
        df_s = df[df['code'] == symbol]
        if len(df_s['trade'].get_values()):
            return df_s['trade'].get_values()[0]
        else:
            return -1
    except:
        return -1

if __name__ == "__main__":
    stop_loss_by_price()