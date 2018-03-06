#!/usr/local/bin/python3
#coding=utf-8

import sys
import platform
from apscheduler.schedulers.blocking import BlockingScheduler
import logging
logging.basicConfig()

if platform.system() == 'Windows':
    sys.path.append('../')
else:
    sys.path.append('/Users/cbb/Documents/pythonspace/stock-master/')

import ctypes
from ConfigParser import ConfigParser

import data_process.online_data as OnlineData
from trade_process.strategy.macd_live_test import MAStrategy
from util.stockutil import fn_timer as fn_timer_
from data_process.data_get import *
from data_process.Stock import Stock
import util.stockutil as util
from util.date_convert import GetNowTime
from util.send_mail import send_email_163
from init import *
from strategy.stop_loss import stop_loss_by_price





#stock_list =['600893']




def main():

    #获取实时股价
    try:
        stockList = OnlineData.getAllChinaStock()
    except Exception, e:
        errorLogger.logger.error(encode_wrap('获取实时估价失败!  ') + str(e))
        return

    #止盈止损判断
    judgements = stop_loss_by_price()
    if judgements:
        for judgement in judgements:
            infoLogger.logger.info(encode_wrap('卖出:{}'.format(judgement[0])))


    cf = ConfigParser()
    cf.read(config_file_path)
    threshold_buy = cf.get('trade_threshold', 'Threshold_Buy_Count')
    threshold_sale = cf.get('trade_threshold', 'Threshold_Sale_Count')
    infoLogger.logger.info(encode_wrap('阈值: Buy(%s) ,Sale(%s)' %(threshold_buy, threshold_sale)))

    # 监听股票列表
    stock_list = ['600000','600048', '600011', '002600', '002505', '000725', '000783', '300315', '002167', '601001',\
              '600893', '000020', '600111']

    print '>>>>>Calcute ...'
    stock_buy_list, stock_sale_list = live_mult_stock(stockList)
    if len(stock_buy_list) == 0 and len([stock for stock in stock_sale_list if stock.code in stock_list]) == 0:
        infoLogger.logger.info(encode_wrap('没有合适的买卖机会，请耐心等待'))
        return

    str_all = '{}\n\n\n买入\n'.format(GetNowTime())

    infoLogger.logger.info(encode_wrap('{}\n\n买入'.format(GetNowTime())))
    for stock in stock_buy_list:
        infoLogger.logger.info('Buy now! ' + stock.str_print())
        str_all = str_all + stock.str_print() + '\n'

    #print encode_wrap('\n卖出:')f
    print '\n'
    infoLogger.logger.info(encode_wrap('卖出'))
    str_all = '\n\n\n' + str_all + '卖出\n'
    for stock in stock_sale_list:
        # if stock.code in stock_list:
            infoLogger.logger.info('Sale now! ' + stock.str_print())
            #print '>' * 3, 'Sale now!', encode_wrap(stock.name), stock.code, stock.current, (float(stock.current)-float(stock.close))/float(stock.close)*100, '%'
            str_all = str_all + stock.str_print() + '\n'

    send_email_163(subject='MA Strategy Results', content=str_all)


@fn_timer_        
def live_mult_stock(stockClassList):  
#     pool = ThreadPool(processes=4)
#     pool.map(live_single_stock, stockClassList)
#     pool.close()
#     pool.join()    
    
    stock_buy_list = []
    stock_sale_list = []
    for stock in stockClassList:
        try:
            live_single_stock(stock)
            if stock.signal > 0:
                stock_buy_list.append(stock)
            elif stock.signal < 0:
                stock_sale_list.append(stock)
        except Exception, e:
            errorLogger.logger.error((str(e)))
    return stock_buy_list, stock_sale_list      

def live_single_stock(stock):
    try:
        # 多线程提醒实时买卖
        if float(stock.current) == 0.0:
            #print '>>>', stock.name,'>>>停牌!',  stock.close, stock.time
            return 0, ''

        #取最近三个月的收盘价
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
    

   
 
if __name__ == "__main__":
    print ">>live trade begin"
    main()

    sched = BlockingScheduler()
    sched.add_job(main, 'cron', day_of_week='0-4', hour='9-12,13-15', minute='*/5')

    print ">>live trade end"
