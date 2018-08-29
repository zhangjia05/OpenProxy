# -*- coding: utf-8 -*-
import re,time,trip,requests,datetime,warnings,asyncio
import pandas as pd
from ipwhois.net import Net
from ipwhois.asn import IPASN
warnings.simplefilter(action='ignore', category=UserWarning)

URL_SET = ['https://www.kuaidaili.com/free','https://31f.cn/region/浙江','https://31f.cn/region/北京/','https://31f.cn/region/广东/#','https://www.kuaidaili.com/free/inha/2/',
           'https://31f.cn/region/安徽/','http://www.31f.cn', 'https://free-proxy-list.net/anonymous-proxy.html', 'http://www.mimiip.com/gngao/1',
           'http://www.mimiip.com/gngao/2','https://www.kuaidaili.com/free/inha/3/','http://www.mimiip.com/gngao/3','http://www.mimiip.com/gngao/4',
           'http://www.mimiip.com/gngao/5','https://www.us-proxy.org/','https://www.kuaidaili.com/free/inha/4/','http://www.mimiip.com/gngao/6',
           'http://www.ip181.com/','https://www.free-proxy-list.net/','https://free-proxy-list.net/anonymous-proxy.html', 
           'https://www.proxynova.com/proxy-server-list/country-us/','https://www.ip-adress.com/proxy-list','https://www.proxynova.com/proxy-server-list/',
           'http://www.proxy-daily.com/','https://www.kuaidaili.com/free/inha/5/','http://202.112.51.31:5010/get_all/','http://www.data5u.com/','http://www.goubanjia.com/']

header = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36'}
localtime = str(datetime.datetime.now().year) + str(datetime.datetime.now().month) + str(datetime.datetime.now().day)#用来给文件命名。
ITL = 0#用来协助遍历URL_SET的常量，用这个常量的原因是，用trip这个协程库之后，不太好往get_proxies()这个函数里面传参。应该可以改进。
#下面四个list是，如果最后需要传出一个包含 "IP PORT ASN ASNinfo" 所有信息的文件，这四个list分别用来装四项信息。
ASNinfolist = []
ASNlist = []
PORTlist = []
IPlist = []



@trip.coroutine
def get_proxies():
    """
    爬代理网站的函数
    """
    global ALL
    global ITL#协助遍历URL_SET的常数，因为需要在这个函数里改动，所以需要在这里global声明一下。
    this_web_has = 0#用来记录这个网站有多少个代理的信息，记录所有的代理数量，包括不好用的。
    ITL += 1 #用来遍历URL_SET。
    #下面这句是正则表达式，能找到IP和端口信息。
    pi = r'(?:((?:\d|[1-9]\d|1\d{2}|2[0-5][0-5])\.(?:\d|[1-9]\d|1\d{2}|2[0-5][0-5])\.(?:\d|[1-9]\d|1\d{2}|2[0-5][0-5])\.(?:\d|[1-9]\d|1\d{2}|2[0-5][0-5]))\D+?(6[0-5]{2}[0-3][0-5]|[1-5]\d{4}|[1-9]\d{1,3}|[0-9]))'
    ipandportlist = []#装找到的代理，回头会返回。
    print(URL_SET[ITL])
    try:
        r = yield trip.get(URL_SET[ITL], timeout=200, headers=header)
        #print(r.text)
        p = re.findall(pi, r.text)
        for each in p:
            str1 = str(each)
            str1 = str1.replace(',', ':')
            str1 = str1.replace('(', '')
            str1 = str1.replace(')', '')
            str1 = str1.replace('\'', '')
            str1 = str1.replace(' ', '')
            ALL.append(str1)
            this_web_has += 1
    except Exception as detail:
        print('This website has a problem.', detail)
        get_proxies()
    print(URL_SET[ITL]+' has '+str(this_web_has)+' proxies.')

@trip.coroutine
def test_proxy(proxy):
    """
    Used global var valid_proxy,this function tests proxy using trip
    """
    global ALL
    global valid_proxy
    try:
        print(proxy)
        r = yield trip.get('http://httpbin.org/get', timeout=200,
            proxies={'http': proxy, 'https': proxy })
        if 'httpbin' in r.text:
            valid_proxy.append(proxy)
            valid_proxy = list(set(valid_proxy))
            print('currently, we have '+str(len(valid_proxy))+' valid proxies')
    except Exception as detail:
        print ("ERROR:", detail)
    else:
        raise trip.Return(proxy)
def main():
    proxies = yield get_proxies()
def test():
    r = yield [test_proxy(p.strip()) for p in IPS]
def test_only():
    r = yield [test_proxy(old.strip()) for old in IPS]
def getip(list):
    """
    Method to extract IP addresses from IP and port combination
    eg: get"207.0.0.1" from "207.0.0.1:8888".
    """
    global IPlist
    global PORTlist
    copy = list.copy()
    for i in range(0, len(copy)):
        oneip = copy[i]
        oneip1 = oneip.split(":")
        oneip2 = oneip1[0]
        IPlist.append(oneip2)
        PORTlist.append(oneip1[1])
def ASN(oneIP):
    str1 = str(oneIP)
    net = Net(str1)
    obj = IPASN(net)
    print('Im looking up '+str1)
    res = yield obj.lookup()
@asyncio.coroutine
def getASN(oneIP):
    putin(next(ASN(oneIP)))
def putin(results):
    global ASNlist
    global ASNinfolist
    result = results
    ASN = result['asn']
    ASNinfo = result['asn_description']
    ASNlist.append(ASN)
    ASNinfolist.append(ASNinfo)
if __name__ == '__main__':
    start_time = time.time()
    j = open('/home/nisl/OpenInformation/OpenProxy/allproxy.txt', 'r')  # 这份文件中包含了上一次抓取所获得的代理。
    allproxy = j.readlines()  # 读。
    print('Old Proxies:  '+str(len(allproxy)))
    ALL = []#用来装所有的代理
    IPS = []#分批测试代理时，用来装每批要测的代理
    valid_proxy = []  # 用来装可以用的代理。

    for n in range(0,len(URL_SET)):
        if ITL <= len(URL_SET)-2:
            trip.run(main)
    everytime = 300
    k  = len(ALL)//300
    for n in range(0,k):
        if n == 0:
            k = 0
        if n != 0:
            k=n*300
        print('I run I run I run')
        IPS = ALL[k:(n+1)*300]
        trip.run(test)
    IPS = ALL[k*300:len(valid_proxy)]
    trip.run(test)

    kk  = len(allproxy)//300
    for n in range(0,kk):
        if n == 0:
            kk = 0
        if n != 0:
            kk=n*300
        print('I run I run I run')
        IPS = allproxy[k:(n+1)*300]
        trip.run(test_only)
    IPS = allproxy[kk*300:len(valid_proxy)]
    trip.run(test_only)
    print('查重前：'+str(len(valid_proxy)))
    valid_proxy = list(set(valid_proxy))
    print('查重后：'+str(len(valid_proxy)))
    j.close()

    f = open('/home/nisl/OpenInformation/OpenProxy/allproxy.txt', 'w')
    for each in valid_proxy:
        f.write(each+'\n')
    f.close()

    print(time.time() - start_time)
