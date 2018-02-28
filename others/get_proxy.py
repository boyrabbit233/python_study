#!/usr/bin/env python
#coding:utf-8
#__author__="ybh"
import requests
from lxml import etree

url="http://proxy.miguan.com/get_all/"
check_url = "http://ip138.com/ips138.asp"

def search_eduproxy(url):
    try:
        r=requests.get(url,timeout=60)
        proxy_list=r.json()
        for proxy in proxy_list:
            ip=str(proxy.split(':')[0])
            location=search_location(ip)


            if u"深圳" in location:
                print(proxy)
                print(location)

    except Exception as e:
        print(e)


def search_location(ip):
    try:
        req = requests.get(check_url, timeout=5, stream=True, params={'ip': ip})
        tree = etree.HTML(req.content)
        result = tree.xpath(u"//ul[@class='ul1']/li[1]")
        return result[0].text
    except Exception as e:
        return ""




if __name__=="__main__":
    search_eduproxy(url)
