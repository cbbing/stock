#ecoding:utf-8
# 导入需要使用到的模块
import urllib
import re
import pandas as pd
import pymysql
import os,datetime,time


# 爬虫抓取网页函数
def getHtml(url):
    html = urllib.urlopen(url).read()
    html = html.decode('gbk')
    return html


# 抓取网页股票代码函数
def getStackCode(html):
    s = r'<li><a target="_blank" href="http://quote.eastmoney.com/\S\S(.*?).html">'
    pat = re.compile(s)
    code = pat.findall(html)
    return code
def downlaodDataBycode(code,jj):
    #########################开始干活############################
    Url = 'http://quote.eastmoney.com/stocklist.html'  # 东方财富网股票数据连接地址
    filepath = './stockdata/dongfangcf/'  # 定义数据文件保存路径
    # 实施抓取
    # code = getStackCode(getHtml(Url))
    # 获取所有股票代码（以6开头的，应该是沪市数据）集合
    # CodeList = []
    # for item in code:
    #     if item[0] == '6':
    #         CodeList.append(item)
    file={'stockcodewangyiShangz.txt':0,'stockcodewangyiShenz.txt':1} #'stockcodewangyiqdii.txt':'','stockcodewangyidetail.txt':''
    #
    # CodeList = []
    # stockTxtNewPath =os.path.pardir + "/stockdata/" + jj
    # file_to_read = open(stockTxtNewPath, 'r')
    # lines = file_to_read.readlines()  # 整行读取数据
    # if not lines:
    #     pass
    # else:
    #     for line in lines:
    #         if line != '\n'and line!=' ':
    #             if jj=='stockcodewangyidetail.txt':
    #                 icode=line.split(' ')
    #             else:
    #                 icode = line.split('\t')
    #             CodeList.append(icode[1])
    # 抓取数据并保存到本地csv文件
    # for code in CodeList:
    if not ' 'in code:
        print(u'正在获取股票%s数据' % code)
        strtoday = datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d')
        tdatetime = datetime.datetime.strptime(strtoday, '%Y%m%d')
        # 前年今日
        sdatetime = tdatetime - datetime.timedelta(days=365)
        strsdate = datetime.datetime.strftime(sdatetime, '%Y%m%d')
        url = 'http://quotes.money.163.com/service/chddata.html?code='+str(file[jj]) + code + \
              '&start='+str(strsdate)+'&end='+str(strtoday)+'&fields=TCLOSE;HIGH;LOW;TOPEN;LCLOSE;CHG;PCHG;TURNOVER;VOTURNOVER;VATURNOVER;TCAP;MCAP'
        print url
        # if jj=='stockcodewangyiqdii.txt':
        #     print code
        time.sleep(0.1)
        urllib.urlretrieve(url, filepath + code + '.csv')
    return filepath + code + '.csv'
def downlaodData():
    #########################开始干活############################
    Url = 'http://quote.eastmoney.com/stocklist.html'  # 东方财富网股票数据连接地址
    filepath =os.path.pardir + '/stockdata/dongfangcf/'  # 定义数据文件保存路径
    # 实施抓取
    # code = getStackCode(getHtml(Url))
    # 获取所有股票代码（以6开头的，应该是沪市数据）集合
    # CodeList = []
    # for item in code:
    #     if item[0] == '6':
    #         CodeList.append(item)
    file={'stockcodewangyiShangz.txt':0,'stockcodewangyiShenz.txt':1} #'stockcodewangyiqdii.txt':'','stockcodewangyidetail.txt':''
    for jj in file:
        CodeList = []
        stockTxtNewPath =os.path.pardir + "../stockdata/" + jj
        file_to_read = open(stockTxtNewPath, 'r')
        lines = file_to_read.readlines()  # 整行读取数据
        if not lines:
            pass
        else:
            for line in lines:
                if line != '\n'and line!=' ':
                    if jj=='stockcodewangyidetail.txt':
                        icode=line.split(' ')
                    else:
                        icode = line.split('\t')
                    CodeList.append(icode[1])
        # 抓取数据并保存到本地csv文件
        for code in CodeList:
            if not ' 'in code:
                print(u'正在获取股票%s数据' % code)
                strtoday = datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d')
                tdatetime = datetime.datetime.strptime(strtoday, '%Y%m%d')
                # 前年今日
                sdatetime = tdatetime - datetime.timedelta(days=365)
                strsdate = datetime.datetime.strftime(sdatetime, '%Y%m%d')
                url = 'http://quotes.money.163.com/service/chddata.html?code='+str(file[jj]) + code + \
                      '&start='+str(strsdate)+'&end='+str(strtoday)+'&fields=TCLOSE;HIGH;LOW;TOPEN;LCLOSE;CHG;PCHG;TURNOVER;VOTURNOVER;VATURNOVER;TCAP;MCAP'
                print url
                if jj=='stockcodewangyiqdii.txt':
                    print code
                time.sleep(0.1)
                urllib.urlretrieve(url, filepath + code + '.csv')
                # stockdata=urllib.urlopen(url)
                # print (stockdata)
if __name__ == '__main__':

    downlaodData()
    ##########################将股票数据存入数据库###########################
    # 数据库名称和密码
    name = 'xxxx'
    password = 'xxxx'  # 替换为自己的账户名和密码
    # 建立本地数据库连接(需要先开启数据库服务)
    db = pymysql.connect('localhost', name, password, charset='utf8')
    cursor = db.cursor()
    # 创建数据库stockDataBase
    sqlSentence1 = "create database stockDataBase"
    cursor.execute(sqlSentence1)  # 选择使用当前数据库
    sqlSentence2 = "use stockDataBase;"
    cursor.execute(sqlSentence2)

    # 获取本地文件列表
    fileList = os.listdir(filepath)
    # 依次对每个数据文件进行存储
    for fileName in fileList:
        data = pd.read_csv(filepath + fileName, encoding="gbk")
        # 创建数据表，如果数据表已经存在，会跳过继续执行下面的步骤print('创建数据表stock_%s'% fileName[0:6])
        try:
            sqlSentence3 = "create table stock_%s" % fileName[0:6] + "(日期 date, 股票代码 VARCHAR(10),     名称 VARCHAR(10),\
                               收盘价 float,    最高价    float, 最低价 float, 开盘价 float, 前收盘 float, 涨跌额    float, \
                               涨跌幅 float, 换手率 float, 成交量 bigint, 成交金额 bigint, 总市值 bigint, 流通市值 bigint)"
            cursor.execute(sqlSentence3)
        except:
            print('数据表已存在！')

    # 迭代读取表中每行数据，依次存储（整表存储还没尝试过）
    print('正在存储stock_%s' % fileName[0:6])
    length = len(data)
    for i in range(0, length):
        record = tuple(data.loc[i])
        # 插入数据语句
        try:
            sqlSentence4 = "insert into stock_%s" % fileName[0:6] + "(日期, 股票代码, 名称, 收盘价, 最高价, 最低价, 开盘价,\
                                           前收盘, 涨跌额, 涨跌幅, 换手率, 成交量, 成交金额, 总市值, 流通市值) \
                                           values ('%s',%s','%s',%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)" % record
            # 获取的表中数据很乱，包含缺失值、Nnone、none等，插入数据库需要处理成空值
            sqlSentence4 = sqlSentence4.replace('nan', 'null').replace('None', 'null').replace('none', 'null')
            cursor.execute(sqlSentence4)
        except:
            # 如果以上插入过程出错，跳过这条数据记录，继续往下进行
            break

    # 关闭游标，提交，关闭数据库连接
    cursor.close()
    db.commit()
    db.close()

    ###########################查询刚才操作的成果##################################

    # 重新建立数据库连接
    db = pymysql.connect('localhost', name, password, 'stockDataBase')
    cursor = db.cursor()
    # 查询数据库并打印内容
    cursor.execute('select * from stock_600000')
    results = cursor.fetchall()
    for row in results:
        print(row)
    # 关闭
    cursor.close()
    db.commit()
    db.close()