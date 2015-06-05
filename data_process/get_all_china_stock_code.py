#!/usr/local/bin/python
#coding=utf-8

import urllib2
import BeautifulSoup
import re
import sys
import chardet

import logging
import scrapy
from scrapy.spiders import Spider
from scrapy.selector import Selector
#from scrapy import log

from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware  
import random as rd  
import codecs
import json

# http://app.finance.ifeng.com/list/stock.php?t=ha&f=symbol&o=asc&p=1

#url = 'http://quote.eastmoney.com/stock_list.html'
# url = 'http://app.finance.ifeng.com/list/stock.php?t=ha&f=symbol&o=asc&p=1'
# 
# #设置头文件，模拟浏览器访问，防止封IP
# req_header = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
#               'Accept':'text/html;q=0.9,*/*;q=0.8',
#               'Accept-Charset':'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
#               'Accept-Encoding':'gb2312',
#               'Connection':'close',
#               'Referer':None #注意如果依然不能抓取的话，这里可以设置抓取网站的host
#               }
# 
# #建立连接请求，这时返回页面信息给con这个变量，con是一个对象
# req = urllib2.Request(url, headers=req_header)
# con = urllib2.urlopen(req)
# 
# #对con对象调用read()方法，返回的就是html页面，也就是有html标签的纯文本
# doc = con.read()
# typeEncode = sys.getfilesystemencoding()##系统默认编码
# infoencode = chardet.detect(doc).get('encoding','utf-8') #通过第3方模块来自动提取网页的编码
# html = doc.decode(infoencode, 'ignore').encode(typeEncode)##先转换成unicode编码，然后转换系统编码输出  ---------->方式一
# #html = doc.decode('gb2312')#.encode('utf-8') #先转成gb2312编码，然后转换unicode编码输出                                   ---------->方式二
# #html = unicode(doc,'GBK').encode('UTF-8')                                                ----------->方式三
# print html
# 
# # 生成一个soup对象
# # soup = BeautifulSoup.BeautifulSoup(html)
# # for link in soup.findAll('a'):
# #     if link.get('target') == "_blank":
# #         print (link.get('href'))
# 
# # paper_desc = soup.html.body.find('div', {'class' : 'quotebody'}).text
# # #stock_list = re.findall(r'\.html\"\>.*\<\/a\>\<\/li\>', html)
# # stock_list = re.findall(r'\>.*\(\d{6}\)\<\/a\>', html)
# # print paper_desc
# 
# #关闭连接
# con.close()

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

class TTjjItem(scrapy.Item):
    stockCode = scrapy.Field()
    stockName = scrapy.Field()
    
class TTJJi(Spider):

    name = "TTJJ"
    allowed_domains=['eastmoney.com']
    start_urls = ["http://quote.eastmoney.com/stocklist.html#sh"]

    def parse(self, response):

        sel = Selector(response)
        cont=sel.xpath('//div[@class="qox"]/div[@class="quotebody"]/div/ul')[0].extract()
        item = TTjjItem()

        for ii in re.findall(r'<li>.*?<a.*?target=.*?>(.*?)</a>',cont):
            item["stockName"]=ii.split("(")[0].encode('utf-8')
            item["stockCode"]=("sh"+ii.split("(")[1][:-1]).encode('utf-8')
            #log.msg(ii.encode('utf-8'),level="INFO")
            yield item

        #item["stockCode"]="+------------------------------------------------------------------+"
        #yield item
        cont1=sel.xpath('//div[@class="qox"]/div[@class="quotebody"]/div/ul')[1].extract()

        for iii in re.findall(r'<li>.*?<a.*?target=.*?>(.*?)</a>',cont1):
            item["stockName"]=iii.split("(")[0].encode('utf-8')
            item["stockCode"]=("sz"+iii.split("(")[1][:-1]).encode('utf-8')
            #log.msg(iii.encode('utf-8'),level="INFO")
            yield item

class UserAgentMiddle(UserAgentMiddleware):

    def __init__(self, user_agent=''):
        self.user_agent = user_agent

    def process_request(self, request, spider):
        ua = rd.choice(self.user_agent_list)
        if ua:
            #显示当前使用的useragent
            print "********Current UserAgent:%s************" %ua

            #记录
            #log.msg('Current UserAgent: '+ua, level='INFO')
            request.headers.setdefault('User-Agent', ua)

    #the default user_agent_list composes chrome,I E,firefox,Mozilla,opera,netscape
    #for more user agent strings,you can find it in http://www.useragentstring.com/pages/useragentstring.php
    user_agent_list = [\
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 "
        "(KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 "
        "(KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 "
        "(KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 "
        "(KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 "
        "(KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 "
        "(KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 "
        "(KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 "
        "(KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 "
        "(KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 "
        "(KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 "
        "(KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 "
        "(KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 "
        "(KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 "
        "(KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 "
        "(KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 "
        "(KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 "
        "(KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 "
        "(KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
       ]


# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

class TtjjPipeline(object):

    def __init__(self):

        self.file=codecs.open("TTJJ.json",mode="wb",encoding='utf-8')
        self.file.write('{"hah"'+':[')


    def process_item(self, item, spider):
        line = json.dumps(dict(item))+","
        self.file.write(line.decode("unicode_escape"))

        return item



# Scrapy settings for TTJJ project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'TTJJ'  
  
SPIDER_MODULES = ['TTJJ.spiders']  
NEWSPIDER_MODULE = 'TTJJ.spiders'  
download_delay=1  
ITEM_PIPELINES={'TTJJ.pipelines.TtjjPipeline':300}  
COOKIES_ENABLED=False  
# Crawl responsibly by identifying yourself (and your website) on the user-agent  
#USER_AGENT = 'TTJJ (+http://www.yourdomain.com)'  
#取消默认的useragent,使用新的useragent  
DOWNLOADER_MIDDLEWARES = {  
        'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware' : None,  
        'TTJJ.spiders.UserAgentMiddle.UserAgentMiddle':400  
    }  