#!/usr/local/bin/python
#coding=utf-8

from data_process.data_get import *
import pandas.io.data as web
import re, urllib, urllib2, cookielib

def find_stock_by(code):
    #print 'find begin'
    code = getSixDigitalStockCode(code)
    # 取六月以来的股价
    df = get_stock_k_line(code, date_start='2015-06-01')
    close_prices = df[cm.KEY_CLOSE].get_values()
    dates = df[cm.KEY_DATE].get_values()
    if len(dates) == 0:
        return
    now_date = dates[-1][:10]
    if now_date != '2015-07-10':
        return
    
    max_price = close_prices.max()
    now_price = close_prices[-1]
    ratio = (max_price - now_price) / max_price
    if ratio >= 0.6 and ratio < 0.:
        print code, '相比六月以来最大值降幅 :%f' % (ratio * 100 ),'%'

def getHtml(url):
    page = urllib.urlopen(url)
    html = page.read()
    html = html.decode('GBK')
    return html

def getImg(html):
    reg = r'"(http://quote.eastmoney.com/(sh|sz)[360].+html)">(.+)\(([0-9]{6})\)</a></li>'
    imgre = re.compile(reg)
    imgList = re.findall(imgre, html)
    
    x = 0
    for imgurl in imgList:
        print imgurl
        #urllib.urlretrieve(imgurl, '%s.jpg' % x)
        x = x + 1
    return len(imgList)

if __name__ == "__main__":
    
#     codes = get_stock_codes()
#     for code in codes:
#         find_stock_by(code)    
#     some_text = 'alpha , beta ,,,gamma delta '
#     print re.split('[,]', some_text)
#     
#     pat = '[a-zA-Z]+'
#     text = '"Hm...err -- are you sure?" he said, sounding insecure.'
#     print re.findall(pat, text)
#     
#     pat = '{name}'
#     text = 'Dear {name}...'
#     print re.sub(pat, 'Mr. Gumby', text)
#     
#     print re.escape('www.python.org')
#     print re.escape('but where is the ambiguity?')
#     
#     m = re.match(r'www\.(.*)\..{3}', 'www.python.org')
#     print m.group(1)
#     print m.start(1), m.end(1), m.span(1)
    
    #print getImg(getHtml('http://quote.eastmoney.com/stocklist.html'))
    values = {"username":"cbbing", "password":"xx"}
    data = urllib.urlencode(values)
    url = "https://passport.csdn.net/account/login?from=http://my.csdn.net/my/mycsdn"
    user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.132 Safari/537.36'
    headers = {'User-Agent':user_agent}
    
    geturl = url+"?"+data
    print geturl
    
    request = urllib2.Request(url, data, headers)
    response = urllib2.urlopen(request)
    #print response.read()
    
    cookie = cookielib.CookieJar()
    handler = urllib2.HTTPCookieProcessor(cookie)
    opener = urllib2.build_opener(handler)
    response = opener.open("http://www.baidu.com")
    for item in cookie:
        print 'Name= ' + item.name
        print 'Value= ' + item.value
    
#     filename='cookie.txt'
#     cookie = cookielib.MozillaCookieJar(filename)
#     handler = urllib2.HTTPCookieProcessor(cookie)
#     opener = urllib2.build_opener(handler)
#     response = opener.open("http://www.baidu.com")
#     cookie.save(ignore_discard=True, ignore_expires=True)
    
    cookie = cookielib.MozillaCookieJar()
    cookie.load('cookie.txt', ignore_discard=True, ignore_expires=True)
    req = urllib2.Request("http://www.baidu.com")
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
    response = opener.open(req)
    print response.read()
    
    
    
    
    
        