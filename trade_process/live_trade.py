#!/usr/local/bin/python3
#coding=utf-8

import sys
import platform

if platform.system() == 'Windows':
    sys.path.append('../')
else:
    sys.path.append('/Users/cbb/Documents/pythonspace/stock-master/')

import sched
import ctypes
from ConfigParser import ConfigParser

import data_process.online_data as OnlineData
from trade_process.strategy.macd_live_test import MAStrategy
from util.stockutil import fn_timer as fn_timer_
from data_process.data_get import *
from data_process.Stock import Stock
import util.stockutil as util
from util.codeConvert import *
from util.send_mail import send_email_163
from init import *






#stock_list =['600893']




def main():

    cf = ConfigParser()
    cf.read(config_file_path)
    threshold_buy = cf.get('trade_threshold', 'Threshold_Buy_Count')
    threshold_sale = cf.get('trade_threshold', 'Threshold_Sale_Count')
    infoLogger.logger.info(encode_wrap('阈值: Buy(%s) ,Sale(%s)' %(threshold_buy, threshold_sale)))

    try:
        stockClassList =OnlineData.getAllChinaStock()
    except Exception,e:
        errorLogger.logger.error(encode_wrap('获取实时估价失败!  ') + str(e))
        return

    # 监听股票列表
    stock_list = ['600000','600048', '600011', '002600', '002505', '000725', '000783', '300315', '002167', '601001',\
              '600893', '000020', '600111']

    print '>'*5, 'Calcute ...'
    stock_buy_list, stock_sale_list = live_mult_stock(stockClassList)
    if len(stock_buy_list) == 0 and len([stock for stock in stock_sale_list if stock.code in stock_list]) == 0:
        infoLogger.logger.info(encode_wrap('没有合适的买卖机会，请耐心等待'))
        return

    str_all =time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    str_all = str_all + '\n\n\n买入\n'
    #print encode_wrap('买入:')
    infoLogger.logger.info(encode_wrap('买入'))
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

    send_email_163(subject='均线趋势量化结果', content=str_all)

# 获取所有股票的实时股价   
# @fn_timer_
# def get_all_stock_current_price():
#     if DB_WAY == 'redis':
#         r = redis.Redis(host='127.0.0.1', port=6379)
#         stockList = list(r.smembers(INDEX_STOCK_BASIC))
#     elif DB_WAY == 'sqlite':
#         engine = create_engine('sqlite:///..\stocks.db3')
#         sql = 'select %s from %s' % (KEY_CODE, INDEX_STOCK_BASIC)
#         df = pd.read_sql_query(sql, engine)
#         stockList = df[KEY_CODE].get_values()
#
#     stockList_group = util.group_list(stockList, 20)
#
#     stockClassList = []
#     for eachList in stockList_group:
#         #print eachList
#         eachClasses = OnlineData.getLiveMutliChinaStockPrice(eachList)
#         if eachClasses != []:
#             stockClassList.extend(eachClasses)
#     print '交易股票总数：%d' % len(stockClassList)
#     return stockClassList

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
    

##  Styles:
##  0 : OK
##  1 : OK | Cancel
##  2 : Abort | Retry | Ignore
##  3 : Yes | No | Cancel
##  4 : Yes | No
##  5 : Retry | No 
##  6 : Cancel | Try Again | Continue
def Mbox(title, text, style):
    ctypes.windll.user32.MessageBoxA(0, text, title, style)
    

#初始化sched模块的scheduler类
#第一个参数是一个可以返回时间戳的函数，第二个参数可以在定时未到达之前阻塞。
s = sched.scheduler(time.time,time.sleep)

#被周期性调度触发的函数

def event_func():

    infoLogger.logger.info( 'Cycle Start >>>  ' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
    #print 'Cycle Start', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    #交易时间
    trade_time = range(930, 1500)
    trade_break = range(1130, 1300)
    now_time = int(time.strftime('%H%M', time.localtime(time.time())))
    if now_time in trade_time and not now_time in trade_break:
        main()
    elif now_time > 1500:
        infoLogger.logger.info(encode_wrap('交易时间结束'))
        sys.exit(0)
    else:
        print encode_wrap('休市中...')
        #sys.exit(0)
        time.sleep(60)
    #print 'Cycle End', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    infoLogger.logger.info( 'Cycle End >>>  ' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
    print '\n\n'

    
#enter四个参数分别为：间隔事件、优先级（用于同时间到达的两个事件同时执行时定序）、被调用触发的函数，给他的参数（注意：一定要以tuple给如，如果只有一个参数就(xx,)）
def perform(inc):
    s.enter(inc,0,perform,(inc,))
    event_func()
    
def mymain(inc=60*5):
    s.enter(0,0,perform,(inc,))
    s.run()
   
 
if __name__ == "__main__":
    print ">>live trade begin"
    mymain()
    print ">>live trade end"
