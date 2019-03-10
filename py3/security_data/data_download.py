
import tushare as ts
import pandas as pd
import datetime

from util.stockutil import fn_timer as fn_timer_
from util.date_convert import GetNowTime

from util.io_tosql import to_sql
import py3.config.db_config as db


def download_stock_basic_info():
    """
    获取股票基本信息
    :return:
    """
    
    try:
        df = ts.get_stock_basics()

        print(df.columns)
        df['code'] = df.index

        print(df.head())
        if len(df):
            engine = db.get_w_engine()
            to_sql(STOCK_BASIC_TABLE, engine, df, type='replace')
            # df.to_sql(STOCK_BASIC_TABLE, engine, if_exists='append', index=False)

        # 添加指数
        indexs = [('sh', '上证指数', '指数','全国','19910715'),
                  ('sz', '深圳成指', '指数','全国','19940720'),
                  ('hs300', '沪深300指数', '指数','全国','20050408'),
                  ('sz50', '上证50指数', '指数','全国','20040102'),
                  ('zxb', '中小板指数', '指数','全国','20050607'),
                  ('cyb', '创业板指数', '指数','全国','20100531'),]
        df = pd.DataFrame(indexs, columns=[KEY_CODE,KEY_NAME, KEY_INDUSTRY, KEY_AREA, KEY_TimeToMarket])
        print(df)
        to_sql(STOCK_BASIC_TABLE, engine, df, type='replace')

           
    except Exception as e:
        print(str(e))

# 获取所有股票的历史K线
@fn_timer_
def download_all_stock_history_k_line():
    print('download all stock k-line start')

    try:
        engine = db.get_w_engine()
        df = pd.read_sql_table(STOCK_BASIC_TABLE, engine)
        codes = df[KEY_CODE].tolist()
        print('total stocks:{0}'.format(len(codes)))
        for code in codes:
            download_stock_kline_by_code(code)

        # codes = codes[::-1]
        #codes = r.lrange(INDEX_STOCK_BASIC, 0, -1)
        # pool = ThreadPool(processes=10)
        # pool.map(download_stock_kline_by_code, codes)
        # pool.close()
        # pool.join()

    except Exception as e:
        print(str(e))
    print('download all stock k-line finish')

def download_stock_kline_by_code(code, date_start='', date_end=datetime.datetime.now()):
    """
    下载单只股票到数据库
    :param code:
    :param date_start:
    :param date_end:
    :return:
    """
    try:
        engine = db.get_w_engine()

        # 设置日期范围
        if date_start == '':
            # 取数据库最近的时间
            sql = "select MAX(date) as date from {0} where code='{1}'".format(STOCK_KLINE_TABLE, code)
            df = pd.read_sql_query(sql, engine)
            if df is not None and  df.ix[0, KEY_DATE] is not None:
                date_start = df.ix[0, KEY_DATE]
                date_start = datetime.datetime.strptime(str(date_start), "%Y-%m-%d") + datetime.timedelta(1)
                date_start = date_start.strftime('%Y-%m-%d')
            else:
                se = get_stock_info(code)
                date_start = se[KEY_TimeToMarket]
                date_start = datetime.datetime.strptime(str(date_start), "%Y%m%d")
                date_start = date_start.strftime('%Y-%m-%d')

        if isinstance(date_end, datetime.date):
            date_end = date_end.strftime('%Y-%m-%d')

        if date_start >= date_end:
            print('Code:{0} is updated to {1}'.format(code, date_start))
            return

        # 开始下载
        # 日期分隔成一年以内
        dates = pd.date_range(date_start, date_end)
        df = pd.DataFrame(dates, columns=['date'])
        df['year'] = df['date'].apply(lambda x : x.year)
        print(df.head())

        years = list(set(df['year'].get_values()))
        years.sort()

        for year in years:
            df1 = df[df['year']==year]
            if len(df1) > 0:
                date_s = str(df1['date'].get_values()[0])[:10]
                date_e = str(df1['date'].get_values()[-1])[:10]
            print('download ' + str(code) + ' k-line >>>begin (', date_s + u' 到 ' + date_e + ')')
            df_qfq = download_kline_by_date_range(code, date_s, date_e)
            if len(df_qfq):
                df_qfq.to_sql(STOCK_KLINE_TABLE, engine, if_exists='append', index=False)
                print('\ndownload {} k-line to mysql finish ({} to {})'.format(code, date_s, date_e))
            else:
                return 'fail... , and try again'

    except Exception as e:
        print(str(e))
        
    # return None


def download_kline_by_date_range(code, date_start, date_end):
    """
    根据日期范围下载股票行情
    :param code:股票代码，即6位数字代码，或者指数代码（sh=上证指数 sz=深圳成指 hs300=沪深300指数 sz50=上证50 zxb=中小板 cyb=创业板）
    :param date_start:
    :param date_end:
    :return:
    """
    try:
        if len(code)==6:
            df_qfq = ts.get_k_data(str(code), start=date_start, end=date_end, autype='qfq') # 前复权
            df_hfq = ts.get_k_data(str(code), start=date_start, end=date_end, autype='hfq')  # 后复权
        else:
            df_qfq = ts.get_k_data(str(code), start=date_start, end=date_end)
        if len(df_qfq)==0 or (len(code)==6 and len(df_hfq)==0):
            return pd.DataFrame()

        if len(code)==6:
            df_qfq['close_hfq'] = df_hfq['close']
        else:
            df_qfq['close_hfq'] = df_qfq['close']  # 指数后复权=前复权

        print(df_qfq.head())

        return df_qfq
    except Exception as e:
        print(str(e))
        return pd.DataFrame()


def download_realtime_stock_price():
    """
    # 下载股票的实时行情
    :return:
    """
    try:
        engine = db.get_w_engine()

        df_price = ts.get_today_all()

        stock_time = GetNowTime()
        if stock_time[11:] > "15:00:00":
            stock_time = stock_time[:11] + "15:00:00"
        df_price['date'] = stock_time

        # df_price.to_sql(STOCK_REALTIME_TABLE, engine, if_exists='append', index=False)
        to_sql(STOCK_REALTIME_TABLE, engine, df_price, type='replace')

    except Exception as e:
        print(e)

#######################
##  private methods  ##
#######################

@fn_timer_
def get_stock_info(code):
    """
    获取股票基本信息
    :param code:
    :return: Series
    """
    try:
        engine = db.get_w_engine()
        sql = "select * from %s where code='%s'" % (STOCK_BASIC_TABLE, code)
        df = pd.read_sql_query(sql, engine)
        se = df.ix[0]
    except Exception as e:
        print(e)
    return se


 

# def check_unnormal_stock_price():
#     """
#     异常股价检测
#     :return:
#     """
#     sql = "select code,name from stock_basic_all"
#     df_code =  pd.read_sql(sql, engine)
#
#     unnormal_codes = []
#     for code,name in df_code[['code','name']].get_values():
#         sql = "select code, date, close, close_hfq from hq_db.stock_kline_fq where code='{}' and date >'2002-12-06' order by date asc ".format(code)
#         df = pd.read_sql(sql, engine)
#         if len(df) < 2:
#             continue
#         # print code, len(df)
#         df.index = df['date']
#         returns_close = df['close'].pct_change()
#         # returns_close_hfq = df['close_hfq'].pct_change()
#         returns_close[0]= 0
#         # returns_close_hfq[0] = 0
#
#         # print returns_close_hfq[:10]
#
#         df['returns_close'] = returns_close
#         # df['returns_close_hfq'] = returns_close_hfq
#
#         df1 = df[df['returns_close']==df['returns_close'].min()]
#         # print df1
#
#         #print '前复权', min(returns_close), '后复权',min(returns_close_hfq)
#         if returns_close.min() < -0.2:
#             print df1
#             #先删除code对应的行情
#             sql = "delete from stock_kline_fq where code='{}'".format(code)
#             print sql
#             engine.execute(sql)
#             #再重新取
#             download_stock_kline_by_code(code)
#
#             # print ">"*10, name, code, '前复权', returns_close.min()
#             unnormal_codes.append((name, code, '前复权', returns_close.min()))
#         # if returns_close_hfq.min() < -0.15:
#         #     print df1
#         #     # print  ">"*10, name, code, '后复权', returns_close_hfq.min()
#         #     unnormal_codes.append((name, code, '后复权', returns_close_hfq.min()))
#
#     print "\n"*5
#     for un_code in unnormal_codes:
#         print "{}:{}\t{}\t{}".format(un_code[0], un_code[1], un_code[2], un_code[3])
#
#     print "total count", len(unnormal_codes)

if __name__ == '__main__':

    # download_stock_basic_info()
    # download_all_stock_history_k_line()
    # download_realtime_stock_price()

    get_stock_info("600000")

    # check_unnormal_stock_price()
    #calcute_ma_all()
    # download_kline_by_date_range('sh', date_start='2012-09-29',date_end='2012-12-16')