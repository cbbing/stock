#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
# from url_info import *
# from spider import *
#import itchat
#from sleep import *
# import datetime
# import one_predict
import json,time
import sched

import datetime
import re
# import sys
import urllib2
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from email.mime.application import MIMEApplication
from fund_zf import main_zf
# from strategy.macd_back_test import macdmain
# from numpy import mean, ptp, var, std

import requests
from bs4 import BeautifulSoup


def spider(url):
    r = requests.get(url)
    page = r.text
    soup = BeautifulSoup(page, 'html.parser')
    value = soup.find_all(id='gz_gszzl')
    value = value[0].get_text().replace('%','')
    value=value.encode('utf-8')
    value1 = soup.find_all(id='gz_gsz')
    value1 = value1[0].get_text().encode('utf-8')
    try:
       return [float(value1),float(value1),float(value)]
    except ValueError as e:
       return
# 是否已在list中
def get_index(fund_code, all_fund_list):
    fund_num = len(all_fund_list)
    fund_index = 0
    while fund_index < fund_num:
        if fund_code in all_fund_list[fund_index]:
            break;
        fund_index += 1
    return fund_index


# 获取基金类型
def get_type(fund_code, all_fund_list):
    fund_type = 'none'
    for fund in all_fund_list:
        if fund_code in fund:
            fund_type = fund[3]
            break

    return fund_type

# 获取某一基金在某一日的累计净值数据
def get_jingzhi(strfundcode, strdate,stredate):
    try:
        url = 'http://fund.eastmoney.com/f10/F10DataApi.aspx?type=lsjz&code=' + str(strfundcode) + '&page=1&per=1000&sdate=' + str(strdate) + '&edate=' + str(stredate)
        print u'数据链接：'+url + '\n'
        response = urllib2.urlopen(url)
    except urllib2.HTTPError, e:
        print e
        urllib_error_tag = True
    except StandardError, e:
        print e
        urllib_error_tag = True
    else:
        urllib_error_tag = False

    if urllib_error_tag == True:
        return '-1'

    json_fund_value = response.read().decode('utf-8')
    # print json_fund_value

    tr_re = re.compile(r'<tr>(.*?)</tr>')
    item_re = re.compile(
        r'''<td>(\d{4}-\d{2}-\d{2})</td><td.*?>(.*?)</td><td.*?>(.*?)</td><td.*?>(.*?)</td><td.*?>(.*?)</td><td.*?>(.*?)</td><td.*?></td>''',
        re.X)

    # 获取不到 返回0
    jingzhi ='-1'
    result=[]

    for line in tr_re.findall(json_fund_value):
        # print line + '\n'
        match = item_re.match(line)
        if match:
            entry = match.groups()
            entry[3].rstrip('%')
            date = datetime.datetime.strptime(entry[0], '%Y-%m-%d')
            # jingzhi = entry[2]
            if entry[3]!='':
                result.append([date, float(entry[1]),float(entry[2]), float(entry[3].rstrip('%'))])
            else:
                result.append([date, float(entry[1]), float(entry[2]), 0])
            jingzhi1 = entry[1]
            jingzhi2 = entry[2]
            # print jingzhi2

            if jingzhi2.strip() == '':
                # 040028
                # 净值日期	每万份收益	7日年化收益率（%）	申购状态	赎回状态	分红送配
                # 2017-01-06	1.4414												暂停申购	暂停赎回
                # 2017-01-05	1.4369												暂停申购	暂停赎回
                jingzhi = '-1'
            elif jingzhi2.find('%') > -1:
                # 040003
                # 净值日期	每万份收益	7日年化收益率（%）	申购状态	赎回状态	分红送配
                # 2017-03-27	1.1149	3.9450%	限制大额申购	开放赎回
                # 2017-03-26*	2.2240	3.8970%	限制大额申购	开放赎回
                jingzhi = '-1'
            elif float(jingzhi1) > float(jingzhi2):
                # 502015
                # 净值日期	单位净值	累计净值	日增长率	申购状态	赎回状态	分红送配
                # 2017-03-27	0.6980	0.3785	-2.24%	场内买入	场内卖出
                # 2017-03-24	0.7140	0.3945	5.15%	场内买入	场内卖出
                jingzhi = entry[1]
            else:
                #
                # 净值日期	单位净值	累计净值	日增长率	申购状态	赎回状态	分红送配
                # 2017-03-28	1.7720	1.7720	-0.23%	开放申购	开放赎回
                # 2017-03-27	1.7761	1.7761	-0.43%	开放申购	开放赎回
                jingzhi = entry[2]
    return result

#获取历史数据
def get_histrydata(strfundcode,numdays):
    # 当前日期
    strtoday = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d')
    tdatetime = datetime.datetime.strptime(strtoday, '%Y-%m-%d')
    print u'结束时间：' + strtoday
    url = 'http://fund.eastmoney.com/%s.html' % strfundcode[0]
    todayvalue = spider(url)

    # 昨天
    yestodaytime = tdatetime - datetime.timedelta(days=1)
    yestoday = datetime.datetime.strftime(yestodaytime, '%Y-%m-%d')

    # 前年今日
    sdatetime = tdatetime - datetime.timedelta(days=numdays)
    strsdate = datetime.datetime.strftime(sdatetime, '%Y-%m-%d')
    print u'开始时间：' + strsdate

    # 1.1 起始时间
    strsdate = strsdate  # sys.argv[1]
    stredate = yestoday  # sys.argv[2]

    # 今日零时
    # strtoday = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d')
    # tdatetime = datetime.datetime.strptime(strtoday, '%Y-%m-%d')
    # print tdatetime

    # 开始时间 如果是周六 周日 调整到周五
    # print strsdate
    sdatetime = datetime.datetime.strptime(strsdate, '%Y-%m-%d')
    sdatetime.isoweekday()
    if sdatetime.isoweekday() == 7:
        sdatetime = sdatetime + datetime.timedelta(days=-2)
    elif sdatetime.isoweekday() == 6:
        sdatetime = sdatetime + datetime.timedelta(days=-1)

    strsdate = datetime.datetime.strftime(sdatetime, '%Y-%m-%d')
    # print strsdate

    # 结束时间 如果是周六 周日 调整到周五
    # print stredate
    edatetime = datetime.datetime.strptime(stredate, '%Y-%m-%d')
    edatetime.isoweekday()
    if edatetime.isoweekday() == 7:
        edatetime = edatetime + datetime.timedelta(days=-2)
    elif edatetime.isoweekday() == 6:
        edatetime = edatetime + datetime.timedelta(days=-1)

    stredate = datetime.datetime.strftime(edatetime, '%Y-%m-%d')
    # print stredate

    # 判断时间段 今日净值要下午才出 一律不处理
    if edatetime <= sdatetime or tdatetime <= sdatetime or tdatetime <= edatetime:
        print '判断时间段 今日净值要下午才出 一律不处理'
        print 'date input error!\n'

    jingzhimin = get_jingzhi(strfundcode[0], strsdate, stredate)
    if todayvalue != None:
        jingzhimin.insert(0, [tdatetime, todayvalue[0], todayvalue[1], todayvalue[2]])
    return jingzhimin

#计算交易策略
def fenxi(strfundcode,numdays):
    #获取历史数据
    jingzhimin=get_histrydata(strfundcode,numdays)
    years = [x[0] for x in jingzhimin]
    price = [x[1] for x in jingzhimin]
    changeprice = [x[3]/x[1] for x in jingzhimin]
    price_stre = [((x[1] - (sum(price)/len(price)))/(max(price)-min(price)))*(max(changeprice)-min(changeprice)) for x in jingzhimin]
    # plt.plot(years, changeprice, 'g',label='change')
    starty = [0 for x in jingzhimin]
    jizhipoints=jizhi(jingzhimin)
    celue_point=celue(jingzhimin,jizhipoints)
    # change_fenxi(change5days)
    return celue_point

def stdDeviation(a):
    l = len(a)
    m = sum(a) / l
    d = 0
    for i in a: d += (i - m) ** 2
    return (d * (1 / l)) ** 0.5

#统计
# def caculate(data):
#     # 极差
#     ptp(data)
#     # 方差
#     var(data)
#     # 标准差
#     std(data)
#     # 变异系数
#     mean(data) / std(data)
#     norm.ppf(0.05, mean(data), std(data))

#求极值
def jizhi(funddata):
    jizhipoints={}
    alldata = [x[1] for x in funddata[::-2]]
    jizhipoints['allmax']= [alldata.index(max(alldata)),max(alldata)]
    jizhipoints['allmin']= [alldata.index(min(alldata)),min(alldata)]
    data30days = [x[1] for x in funddata[:-30:-2]]
    jizhipoints['30daysmax'] = [data30days.index(max(data30days)),max(data30days)]
    jizhipoints['30daysmin'] = [data30days.index(min(data30days)),min(data30days)]
    data180days = [x[1] for x in funddata[:-180:-2]]
    jizhipoints['180daysmax'] = [data180days.index(max(data180days)), max(data180days)]
    jizhipoints['180daysmin'] = [data180days.index(min(data180days)), min(data180days)]
    data5days = [x[1] for x in funddata[:-5:-2]]
    jizhipoints['5daysmax'] = [data5days.index(max(data5days)), max(data5days)]
    jizhipoints['5daysmin'] = [data5days.index(min(data5days)), min(data5days)]
    return jizhipoints

#交易策略监测
def celue(funddata,jizhipoints):
    todaydata = funddata[0]
    data5days = [x[1] for x in funddata[:6:1]]
    change = [x[3] for x in funddata[:5:1]]
    change7 = [x[3] for x in funddata[:7:1]]
    change12days= [x[3] for x in funddata[:90:1]]
    if stdDeviation(change12days)<0.3:
        r=1.005;rmax=0.995
    elif stdDeviation(change12days) > 0.6:
        r = 1.005;rmax = 0.995
    else:
        r = 1.005;rmax = 0.995
    buy_points = []
    sell_point = []

    #根据净值比较
    if(todaydata[1]<=r*jizhipoints['allmin'][1]):
        buy_points.append({'today<1.02*allmin':str(todaydata[1])+str('<=')+str(r*jizhipoints['allmin'][1])})
    elif(todaydata[1]<=r*jizhipoints['180daysmin'][1]):
        buy_points.append({'today<1.02*180min': str(todaydata[1])+str('<=')+str(r*jizhipoints['180daysmin'][1])})
    # elif(todaydata[1]<=r*jizhipoints['30daysmin'][1]):
    #     buy_points.append({'today<1.02*30min': str(todaydata[1] )+str('<=')+str( r*jizhipoints['30daysmin'][1])})
    # elif (todaydata[1] <= r*jizhipoints['5daysmin'][1]):
    #     buy_points['today<1.02*5min'] = str(todaydata[1] )+str('<=')+str( r*jizhipoints['5daysmin'][1])
    #----------------------------
    elif (todaydata[1] >= rmax*jizhipoints['allmax'][1]):
        sell_point.append({'today>0.98*allmax': str(todaydata[1] )+str('>=')+str( rmax*jizhipoints['allmax'][1])})
    elif (todaydata[1] >= rmax*jizhipoints['180daysmax'][1]):
        sell_point.append({'today>0.98*180max': str(todaydata[1] )+str('>=')+str( rmax*jizhipoints['180daysmax'][1])})
    # elif (todaydata[1] >= rmax*jizhipoints['30daysmax'][1]):
    #     sell_point.append({'today>0.9*30max': str(todaydata[1] )+str('<=')+str( rmax*jizhipoints['30daysmax'][1])})
    # elif (todaydata[1] >= rmax*jizhipoints['5daysmax'][1]):
    #     sell_point.append({'today>0.9*30max': str(todaydata[1] )+str('<=')+str( rmax*jizhipoints['5daysmax'][1])})

    # def change_fenxi(change):
    if(sum(change)/len(change)>=0.46):
        sell_point.append({'mean5up':round(sum(change)/len(change),5)})
    elif(sum(change)/len(change)<=-0.46):
        buy_points.append({'mean5up':round(sum(change)/len(change),5)})

    big=[];small=[]
    if len(change)>3:
        for i in range(len(change)):
            if (change[i]>0):
                big.append(change[i])
            elif (change[i]<0):
                small.append(change[i])
        if len(big)>=4 and change[0]<0.2  :
            sell_point.append({'go up 4days':change7})
        # elif (change[0]<change[1] and(change[0]<0.04)and len(big)>=3):
        #     sell_point.append({u'go up 4days': big})
        if (len(small)>=4 and change[0]>0) or (len(small)>=3 and change[0]<-0.5 and change[1]<0.1):
            buy_points.append({'go down 3days':change7})
    return {'sell':sell_point,'buy':buy_points}

def main_run(all_fund_list):
    code = [['002963', 'egold'], ['003321', 'eoil'], ['004744', 'eGEI'], ['110003', 'eSSE50'], ['110020', 'HS300'],
            ['110031', 'eHSI'], ['161130', 'eNASDAQ100'], ['110028', 'anxinB'], ['110022', 'eConsumption '],
            ['161125', 'SPX500']]

    buysell = []
    for i in code:
        # save(strfundcode=i ,numdays=365*1)
        sb=fenxi(strfundcode=i, numdays=365 * 1)
        if sb:
            buysell.append([i,sb])
    for i in all_fund_list[0:50]:
        # save(strfundcode=i ,numdays=365*1)
        sb=fenxi(strfundcode=i, numdays=365 * 1)
        if sb:
            buysell.append([i,sb])
    return buysell

s = sched.scheduler(time.time, time.sleep)
class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.__str__()
        return json.JSONEncoder.default(self, obj)

    # sleep()
#@itchat.msg_register(itchat.content.TEXT)
def print_content(msg):
    print msg['Text']
def readmsg(msg):
    return msg
def send_email(text):
        #text = self.claw_content()
        #open('b.txt', 'w').write(str(text[1]) + '\n' + str(text[0]) + '\n')
        username = 'lsl_cug@126.com'  # input("请输入账号:")
        password = '123456lsl'  # input("请输入密码:")
        sender = username
        # sender=''
        receiver = ['1627041882@qq.com','760140853@qq.com']  # '760140853@qq.com','xxxxxxxxxx@qq.com','xxxxxxxxxx@126.com','994992333@qq.com','1847725033@qq.com','1847725033@qq.com','849281511@qq.com'
        if sender =='':
            username = str(raw_input("Please Input Sender Email Address,for example:xxxxxxxxxx@126.com \n"))
            sender = username
            password = str(raw_input("Please Input Sender Password \n"))
            receiver.append(str(raw_input("Please Input Receiver Address,for example:xxxxxxxxxx@qq.com \n")))
        iRec = 1
        while iRec>0:
            CmdRec = ''#raw_input("Whether you want to add another Receiver Address(default n)? \n")
            if CmdRec == 'y' or CmdRec == 'yes':
                iRec = 1
                receiver.append(str(raw_input("Please Input Receiver Address,for example:xxxxxxxxxx@qq.com \n")))
            else:
                iRec = 0

        ConfirmRec = ''#raw_input("Confirm? \n")
        if ConfirmRec == 'n' or ConfirmRec == 'no':
            print("What Do You Want? Maybe run this program again.\n")
            exit(1)
        else:
            for rece in receiver:
                print("OK \n"+ username + " sendto " + rece)
       # 创建一个带附件的实例
        msg = MIMEMultipart()
        # msg = MIMEText(str(text), 'plain', 'utf-8')
        msg['From'] = formataddr(['user', sender])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
        msg['To'] = ",".join(receiver) # 括号里的对应收件人邮箱昵称、收件人邮箱账号

        subject_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        subject = '基金信息'
        msg['Subject'] = subject

        # 邮件正文内容
        # print str(text[0])
        realText = text#sendmsg #str(text)  #'\n'+str(subject_time)+'：主人，有人来招人啦！^—^\n'+ '海投网：'+str(text[1])+'.'#+str(text[0])#'地大就业网招聘公告：'+str(text1[1])+'地大就业网gis等招聘信息：'+str(text2[1])+'.'#+str(text1[0])+'\n'+str(text2[1])+'\n'+str(text2[0])
        print realText
        msg.attach(MIMEText(realText, 'plain', 'utf-8'))

        # 构造附件1，传送当前目录下的 test.txt 文件
        # att1 = MIMEApplication(open('b.txt', 'rb').read())
        # 这里的filename可以任意写，写什么名字，邮件中显示什么名字
        # att1.add_header('Content-Disposition', 'attachment', filename='hjx.txt')
        # msg.attach(att1)
        # # 构造附件1，传送当前目录下的 test.txt 文件
        # att2 = MIMEApplication(open('b1.txt', 'rb').read())
        # # 这里的filename可以任意写，写什么名字，邮件中显示什么名字
        # att2.add_header('Content-Disposition', 'attachment', filename='b1.txt')
        # msg.attach(att2)
        # att3 = MIMEApplication(open('b2.txt', 'rb').read())
        # # 这里的filename可以任意写，写什么名字，邮件中显示什么名字
        # att3.add_header('Content-Disposition', 'attachment', filename='b2.txt')
        # msg.attach(att3)
        smtpserver = 'smtp.126.com'
        try:
            smtp = smtplib.SMTP(smtpserver,25)
            smtp.starttls()
            smtp.login(username, password)
            smtp.sendmail(sender, receiver, msg.as_string())
            smtp.quit()
            print(u"邮件发送成功")
        except smtplib.SMTPException, e:
            print(u"Error: 无法发送邮件:" + str(e))
            smtp.quit()
            try:
                username = 'lishulincug@163.com'  # input("请输入账号:")
                password = '123456lsl'  # input("请输入密码:")
                sender = username
                # sender=''
                # receiver = [ '1627041882@qq.com','994992333@qq.com','1847725033@qq.com']  # 'xxxxxxxxxx@qq.com','xxxxxxxxxx@126.com','994992333@qq.com','1847725033@qq.com'
                msg['From'] = formataddr(['lishulin', sender])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
                msg['To'] = ",".join(receiver)  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
                smtpserver = 'smtp.163.com'
                smtp = smtplib.SMTP(smtpserver,25)
                smtp.starttls()
                smtp.login(username, password)
                for jj in receiver:
                    smtp.sendmail(sender, jj, msg.as_string())
                    time.sleep(35)
                smtp.quit()
                print(u"邮件发送成功")
            except smtplib.SMTPException, e1:
                print(u"Error: 无法发送邮件:"+str(e1))
                smtp.quit()
                try:
                    username = '15623863340@sina.cn'  # input("请输入账号:")
                    password = '133499'  # input("请输入密码:")
                    sender = username
                    # sender=''
                    # receiver = [ '1627041882@qq.com','994992333@qq.com','1847725033@qq.com']  # 'xxxxxxxxxx@qq.com','xxxxxxxxxx@126.com','994992333@qq.com','1847725033@qq.com'
                    msg['From'] = formataddr(['15623863340@sina.cn', sender])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
                    msg['To'] = ",".join(receiver)  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
                    smtpserver = 'smtp.sina.cn'
                    smtp = smtplib.SMTP(smtpserver,25)
                    smtp.starttls()
                    smtp.login(username, password)
                    smtp.sendmail(sender, receiver, msg.as_string())
                    smtp.quit()
                    print(u"邮件发送成功")
                except smtplib.SMTPException, e2:
                    print(u"Error: 无法发送邮件:" + str(e2))
                    smtp.quit()
def deb_print():
    now = time.strftime("%y-%m-%d %H:%M:%S", time.localtime())
    H=now[9:11]
    M = now[12:14]
    S = now[15:]
    # print now
    print H,M, S
    return H,M, S

def check_time(H, M,S):
    strtoday1 = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d')
    sdatetime = datetime.datetime.strptime(strtoday1, '%Y-%m-%d')
    sdatetime.isoweekday()
    #if sdatetime.isoweekday() == 7:
    if(H == "14" and int(M) == 30  and S == "20")and(sdatetime.isoweekday() != 7)and(sdatetime.isoweekday() != 6):#(H == "14" and M == "08" and S == "10") or
        # itchat.auto_login(hotReload=True)
        # itchat.run
        # curTime =  time.strftime("%y-%m-%d %H:%M:%S", time.localtime())
        # itchat.send(curTime, 'filehelper')
        # itchat.send(str(curTime), toUserName='@9f545f6d5c3f89aa63956c3f386733232f7176569f71a26f477909c02828d735')
        buysell = main_run(all_fund_list)
        print(str(buysell))
        sendmsg=[]
        # f = open("buysell.txt",'a')
        for i in buysell:
            # write_str =  str(i) + '\n'
            # f.write(write_str)
            st = ''
            if i[1]['buy'] != []:
                st = ' 买 '
                for j in i[1]['buy']:
                    st += str(j) + ' '
            elif i[1]['sell'] != []:
                st += ' 卖 '
                for k in i[1]['sell']:
                    st += str(k) + ' '
            if st != '':
                sendmsg.append(str(i[0]) + st+(' http://fund.eastmoney.com/%s.html'%i[0][0]) +('   http://www.efunds.com.cn/html/fund/%s_fundinfo.htm      '%i[0][0]))
        send_email(sendmsg)
        #         itchat.send(str(i[0]) + st+('  http://fund.eastmoney.com/%s.html'%i[0][0]) +('--  http://www.efunds.com.cn/html/fund/%s_fundinfo.htm'%i[0][0]), 'filehelper')
        #         itchat.send(str(i[0]) + st, toUserName='@9f545f6d5c3f89aa63956c3f386733232f7176569f71a26f477909c02828d735')
    s.enter(1, 1, check_time, deb_print())


def main1(sign):
    now = time.strftime("%y-%m-%d %H:%M:%S", time.localtime())
    H = now[9:11]
    M = now[12:14]
    S = now[15:]
    code = [['002963', 'egold'], ['003321', 'eoil'], ['004744', 'eGEI'], ['110003', 'eSSE50'], ['110020', 'HS300'],
            ['110031', 'eHSI'], ['161130', 'eNASDAQ100'], ['110028', 'anxinB'], ['110022', 'eConsumption '],
            ['161125', 'SPX500']]
    all_fund_list = main_zf()
    #sign=macdmain(code)
    if (int(H)):  # >= 19(H == "14" and M == "08" and S == "10") or
        buysell1 = main_run(all_fund_list)
        print(str(buysell1))
        sendmsg = ''
        # f = open("buysell.txt",'a')
        for j in sign:
            #sendmsg +=str(j[0])+','+str(j[1])+','+str(j[2][0])+','+str(j[2][1][0])+'\n'
            sendmsg +=str(j[0])+','+str(j[1])+','+str(j[2][0])+','+str(j[2][1][0])+','+ (' http://fund.eastmoney.com/%s.html' % j[0][0])+'\n'
        for i in buysell1:
            # write_str =  str(i) + '\n'
            # f.write(write_str)
            st = ' '
            if i[1]['buy'] != []:
                st = ' 买 '
                for j in i[1]['buy']:
                    for h in j:
                        st += h + str(j[h]) + ' '
            elif i[1]['sell'] != []:
                st += ' 卖 '
                for k in i[1]['sell']:
                    for t in k:
                        st += t + str(k[t]) + ' '
            if st != ' ':
                sendmsg += i[0][0] + ',' + i[0][1] + st + (' http://fund.eastmoney.com/%s.html' % i[0][0]) + (
                '   http://www.efunds.com.cn/html/fund/%s_fundinfo.htm' % i[0][0]) + '\n'
        # print sendmsg
        send_email(sendmsg)
    while True:
        now = time.strftime("%y-%m-%d %H:%M:%S", time.localtime())
        # date = datetime.datetime.strftime(datetime.datetime.now(), "%Y%m%d")
        H = now[9:11]
        M = now[12:14]
        S = now[15:]
        # print H,S,M
        print 'Start:'+'13:05' +' and 14:30 '+'send to email.'+"\n" +'please wait:'

        #    print time.localtime()
        #    print time.strftime("%y-%m-%d %H:%M:%S",time.localtime())
        # xiaozhao = Xiaozhao()
        # xiaozhao.send_email()
        s.enter(1, 1, check_time, deb_print())
        s.run()

if __name__=='__main__':
    # itchat.auto_login(hotReload=True)
    # itchat.run
    #
    # curTime = now = time.strftime("%y-%m-%d %H:%M:%S", time.localtime())
    # itchat.send(curTime, 'filehelper')
    # buysell = one_predict.main_run()
    # f = open("buysell.txt",'a')
    # for i in buysell:
    #     # write_str =  str(i) + '\n'
    #     # f.write(write_str)
    #     st = ''
    #     if i[1]['buy'] != []:
    #         st = u'买入点'
    #         for j in i[1]['buy']:
    #             st += str(j) + ' '
    #     elif i[1]['sell'] != []:
    #         st += u'  卖出点'
    #         for k in i[1]['sell']:
    #             st += str(k) + ' '
    #     if st != '':
    #         itchat.send(str(i[0]) + st, 'filehelper')
    #         itchat.send(str(i[0]) + st,toUserName='@9f545f6d5c3f89aa63956c3f386733232f7176569f71a26f477909c02828d735')
    all_fund_list = main_zf()
    main1()
    # f.close()
    # itchat.send("@fil@%s" % 'buysell.txt', 'filehelper')
    # for (name, fund_id) in ids.items():
    #     url = 'http://fund.eastmoney.com/%s.html' % fund_id
    #     value = spider(url)
    #     sign = value[0]
    #     value_num = value[1:-1]
    #     name = name.decode('utf-8')
    #     buysell=one_predict.main_run()
    #     itchat.send(buysell , 'filehelper')
    # if(sign == '-' and float(value_num)>2.5):
    #     content = u'%s跌幅很大，可以补仓'+sign+value_num
    #     itchat.send(content % name, 'filehelper')
    # else:
    #     content = u'%s 不需要补仓'+sign+value_num
    #     itchat.send(content % name, 'filehelper')
