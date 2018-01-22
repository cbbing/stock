#coding=utf-8
from trade_process.strategy.macd_back_test import macdmain
from trade_process.strategy.tread_tracking import stock_trader_main
from trade_process.strategy.macd_live_test import macd_live_main
from trade_process.efund_mail2 import main1
if __name__ == '__main__':
    stockList = ['000725', '000783', '002167', '002505', '002600', '300315', '600000', '600011', '600048', '601001']
    ChinaStockIndexList = [
        "000001",  # sh000001 上证指数
        "399001",  # sz399001 深证成指
        "000300",  # sh000300 沪深300
        "399005",  # sz399005 中小板指
        "399006",  # sz399006 创业板指
        "000003",  # sh000003 B股指数
        "000016",  # 上证50
        "000012",  # 国债指数
    ]
    code = [ ['160222', '国泰国证食品饮料行业指数分级'],['110022', 'eConsumption '],['110003', 'eSSE50'], ['110020', 'HS300'], ['110028', 'anxinB'],
             ['002963', 'egold'], ['003321', 'eoil'], ['004744', 'eGEI'],
                    ['110031', 'eHSI'], ['161130', 'eNASDAQ100'],['161125', 'SPX500']]
    #均线策略
    macd=macdmain(code)
    print macd
    main1(macd)
    # stock_trader_main(code)
    # macd_live_main(code)
