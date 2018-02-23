#coding:utf8

import tushare as ts
import data_process.data_get as dg

def fibonacci():
    df_gem = ts.get_gem_classified() #创业板

    for ix, row in df_gem.iterrows():
        code = row['code']
        df_price = dg.get_stock_k_line(code, date_start='2015-01-04')
        print df_price.head()
        returns = df_price['close'].pct_change()
        returns[0] = 0
        print returns

fibonacci()