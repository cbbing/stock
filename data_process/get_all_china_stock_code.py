#!/usr/local/bin/python
#coding=utf-8

import urllib2
import BeautifulSoup
import re
import sys
import chardet

# http://app.finance.ifeng.com/list/stock.php?t=ha&f=symbol&o=asc&p=1

#url = 'http://quote.eastmoney.com/stock_list.html'
url = 'http://app.finance.ifeng.com/list/stock.php?t=ha&f=symbol&o=asc&p=1'

#设置头文件，模拟浏览器访问，防止封IP
req_header = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
              'Accept':'text/html;q=0.9,*/*;q=0.8',
              'Accept-Charset':'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
              'Accept-Encoding':'gb2312',
              'Connection':'close',
              'Referer':None #注意如果依然不能抓取的话，这里可以设置抓取网站的host
              }

#建立连接请求，这时返回页面信息给con这个变量，con是一个对象
req = urllib2.Request(url, headers=req_header)
con = urllib2.urlopen(req)

#对con对象调用read()方法，返回的就是html页面，也就是有html标签的纯文本
doc = con.read()
typeEncode = sys.getfilesystemencoding()##系统默认编码
infoencode = chardet.detect(doc).get('encoding','utf-8') #通过第3方模块来自动提取网页的编码
html = doc.decode(infoencode, 'ignore').encode(typeEncode)##先转换成unicode编码，然后转换系统编码输出  ---------->方式一
#html = doc.decode('gb2312')#.encode('utf-8') #先转成gb2312编码，然后转换unicode编码输出                                   ---------->方式二
#html = unicode(doc,'GBK').encode('UTF-8')                                                ----------->方式三
print html

# 生成一个soup对象
# soup = BeautifulSoup.BeautifulSoup(html)
# for link in soup.findAll('a'):
#     if link.get('target') == "_blank":
#         print (link.get('href'))

# paper_desc = soup.html.body.find('div', {'class' : 'quotebody'}).text
# #stock_list = re.findall(r'\.html\"\>.*\<\/a\>\<\/li\>', html)
# stock_list = re.findall(r'\>.*\(\d{6}\)\<\/a\>', html)
# print paper_desc

#关闭连接
con.close()
