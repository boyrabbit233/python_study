#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import requests
import pymysql
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from lxml import etree

icp_url = "http://icp.chinaz.com/"
mysql_host="127.0.0.1"
mysql_port=3306
mysql_user=""
mysql_passwd=""
mysql_db=""
receivers=[]
text=""

headers = {
    "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36"
}

def get_domain():
    domain_list = []
    s=pymysql.connect(host=mysql_host, port=mysql_port, user=mysql_user, password=mysql_passwd, db=mysql_db)
    cursor=s.cursor()
    sql="select domain from domain_list"
    cursor.execute(sql)
    result_list=cursor.fetchall()
    for result in result_list:
        domain_list.append(result[0])
    return domain_list
    cursor.close()
    s.close()

def check_state():
    global text
    domain_list = get_domain()
    for domain in domain_list:
        page=requests.get(icp_url+domain, headers=headers)
        tree=etree.HTML(page.text)
        res=tree.xpath('//div[@class="Tool-IcpMainCent wrapper02"]/p/text()')
        #如果列表为空，返回false，则有备案
        if res:
            text += "<font color='red'> 查询结果：{0} 未备案或备案失效!</font><br>".format(domain) 
        else:
            text += "查询结果：{0} 有备案<br>".format(domain)

def send_mail(text):
    sender = ''
    pwd    = ''
    message = MIMEText(text, 'html', 'utf-8')
    message['From'] = Header('', 'utf-8')
    message['To'] = Header('', 'utf-8')
    message['Subject'] = Header('备案查询报告', 'utf-8')

    try:
        smtpobj = smtplib.SMTP('smtp.exmail.qq.com')
        smtpobj.login(sender, pwd)
        smtpobj.sendmail(sender, receivers, message.as_string())
        print('邮件发送成功')
    except smtplib.SMTPException:
        print('Error: 无法发送邮件')

if __name__ == '__main__':
    check_state()
    if text != "":
        send_mail(text)
