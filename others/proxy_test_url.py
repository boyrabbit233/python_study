#!/usr/bin/env python
#coding:utf-8
#__author__="ybh"
import requests
from lxml import etree
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import pymysql
import threadpool
import threading
inner_list=['福建','广东','广西','江西','江苏','浙江','山东','山西','河北','河南','湖南','湖北','北京','上海','天津','辽宁','黑龙江','内蒙古','新疆','西藏','云南','四川',\
            '重庆','陕西','甘肃','吉林','青海','宁夏','香港','澳门','台湾','贵州','安徽','海南']
url="http://ip.jiangxianli.com/api/proxy_ips?page="
#download_url=""
check_url = "http://ip138.com/ips138.asp"
receivers=['']
download_url=""
mysql_host="127.0.0.1"
mysql_port=3306
mysql_user=''
mysql_passwd=''
mysql_db=""
text=""
def check_fuck(url):
    try:
	    for n in range(0,13)
            r=requests.get(url+n,timeout=60)
            proxy_list=r.json()
        #download_list = get_download()
        for proxy in proxy_list:
            ip=str(proxy.split(':')[0])
            port=str(proxy.split(':')[1])
            p=threadpool.ThreadPool(4)
            params_list=[]
            #for download_url in download_list:
            params_list.append(([download_url,ip,port],None))
            reqs=threadpool.makeRequests(run,params_list)
            [p.putRequest(req) for req in reqs]
            p.wait()


    except Exception as e:
        print(e)


def search_location(ip):
    try:
        req = requests.get(check_url, timeout=3, stream=True, params={'ip': ip})
        tree = etree.HTML(req.content)
        result = tree.xpath(u"//ul[@class='ul1']/li[1]")
        return result[0].text
    except Exception as e:
        return ""


def send_mail(text):
    sender = ''
    pwd = ''
    message = MIMEText(text, 'html', 'utf-8')
    message['From'] = Header('', 'utf-8')
    message['To'] = Header('', 'utf-8')
    message['Subject'] = Header('报告', 'utf-8')

    try:
        smtpobj = smtplib.SMTP('smtp.exmail.qq.com')
        smtpobj.login(sender, pwd)
        smtpobj.sendmail(sender, receivers, message.as_string())
        print('邮件发送成功')
    except smtplib.SMTPException:
        print('Error: 无法发送邮件')


def get_download():
    download_list=[]
    s=pymysql.connect(host=mysql_host,port=mysql_port,user=mysql_user,password=mysql_passwd,db=mysql_db)
    cursor=s.cursor()
    sql="select download_url from web_downloadurl"
    cursor.execute(sql)
    result_list=cursor.fetchall()
    for result in result_list:
        download_list.append(download_domain+result[0])
    return download_list


def run(download_url,ip,port):
    global text
    flag=0
    try:
        req = requests.get(download_url, timeout=3, stream=True, proxies={'http': '%s:%s' % (ip, port)})
        final_url = req.url
        if download_url != final_url:
            location = search_location(ip).encode('utf-8')
            location = location.split('：')[1]
            for i in inner_list:
                if i in location:
                    flag=1
                    break
            if flag:
                if mutex.acquire():
                    if 'xy1758.com' in final_url:
                        text += "<p>IP:{},地区:{} 被劫持,劫持后的url:{}</p>".format(ip,location,final_url)
                    else:
                        text += "<p style='background-color:red'>IP:{},地区:{} 被劫持,劫持后的url:{}</p>".format(ip,location,final_url)
                    mutex.release()
    except Exception as e:
        pass



if __name__=="__main__":
    mutex=threading.Lock()
    check_fuck(url)
    if text != "":
		print(text)
        send_mail(text)



