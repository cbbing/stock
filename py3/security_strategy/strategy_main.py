import datetime

from init import *
from py3.security_strategy.strategy.ma_strategy import MAStrategy

def run_one_stock(stock):
    try:
        # 多线程提醒实时买卖
        if float(stock.current) == 0.0:
            # print '>>>', stock.name,'>>>停牌!',  stock.close, stock.time
            return 0, ''

        # 取最近三个月的收盘价
        d_90_day = datetime.date.today() + datetime.timedelta(days=-90)
        date_90_day = d_90_day.strftime("%Y-%m-%y")
        df = get_stock_k_line(stock.code, date_start=date_90_day)
        if len(df) < AVR_LONG:
            return Stock()

        cf = ConfigParser()
        cf.read(config_file_path)
        threshold_buy = cf.get('trade_threshold', 'Threshold_Buy_Count')
        threshold_sale = cf.get('trade_threshold', 'Threshold_Sale_Count')

        maStrategy = MAStrategy(code=stock.code,  trade= stock.current, df_close=df)
        signal = maStrategy.select_Time_Mix(int(threshold_buy), int(threshold_sale))
        # if signal > 0:
        #     print '>' * 5, 'Buy now!', stock.name, stock.current, (float(stock.current)-float(stock.close))/float(stock.close)*100, '%'

        stock.signal = signal
        return stock

    except Exception as e:
        print encode_wrap(stock.name), str(e)
        stock = Stock()
        return stock

