#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import requests
import pymysql
import smtplib
import time
from email.mime.text import MIMEText
from email.header import Header
from lxml import etree

icp_url = "http://whois.chinaz.com"
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

def mysqlconn():
    conn = pymysql.connect(host=mysql_host, port=mysql_port, user=mysql_user, password=mysql_passwd, db=mysql_db)
    return conn

def get_domain():
    domain_list = []
    db = mysqlconn()
    cursor=db.cursor()
    sql="select domain from domain_list where enabled = '1'"
    #sql="select domain from domain_list where id = '934'"
    cursor.execute(sql)
    result_list=cursor.fetchall()
    for result in result_list:
        domain_list.append(result[0])
    return domain_list
    cursor.close()
    db.close()

def update_domain(domain=None):
    db = mysqlconn()
    cursor = db.cursor()
    sql="update domain_list set enabled = '0' where domain = %s"
    try:
        cursor.execute(sql, domain)
        db.commit()
    except Exception as e:
        db.rollback()
    cursor.close()
    db.close()

def get_time(tree):
    try:
        time_text = tree.xpath('//div[@class="WhoisWrap clearfix"]/span/text()')
        latest_time = time_text[0].split('：')[1]
        latest_timestamp = time.mktime(time.strptime(latest_time, '%Y-%m-%d %H:%M:%S'))
        return latest_timestamp, latest_time
    except IndexError as e:
        return None, None

def check_state():
    global text
    current_time = time.time()
    domain_list = get_domain()
    for domain in domain_list:
        try:
            time.sleep(3)
            domain = domain.strip()
            print(domain)
            page=requests.get(icp_url + '/' + domain, headers=headers)
            tree=etree.HTML(page.text)
            res=tree.xpath('//div[@class="div_whois ptb10"]/p[1]/a[1]/text()')
            # 如果列表为空，返回false，则未过期
            if res:
                text += "该域名：{0} 已过期或未注册 <br>".format(domain)
                update_domain(domain)
            else:
                # 获取信息更新时间
                latest_timestamp = get_time(tree)[0]
                latest_time = get_time(tree)[1]
                cache_time = current_time - latest_timestamp
                # 如果更新时间在3天以前，就更新信息
                if cache_time > 259200:
                    update_url = "/?Domain={0}&isforceupdate=1".format(domain)
                    #update_url = tree.xpath('//div[@class="WhoisWrap clearfix"]/a/@href')
                    # if "javascript" in update_url[0]:
                    #     text += "<font color='green'>该域名 {0} 信息更新异常，请前往其他查询商处查询whois信息</font><br>".format(domain)
                    #     continue
                    # print(update_url)
                    page = requests.get(icp_url + update_url, headers=headers)
                    tree = etree.HTML(page.text)
                    # error=tree.xpath('//div[@class="div_whois ptb10"]/p[1]/a[1]/text()')
                    #
                    # if error:
                    #     text += "<font color='green'>该域名 {0} 信息更新异常，请前往其他查询商处查询whois信息</font><br>".format(domain)
                    #     continue
                    # else:
                    latest_time = get_time(tree)[1]
                register = tree.xpath('//*[@id="sh_info"]/li[2]/div[2]/div/span/text()')
                locate_list = tree.xpath('//*[@id="sh_info"]/li/div[1]/text()')
                for locate in locate_list:
                    if locate == "过期时间":
                        num = locate_list.index(locate) + 2
                expire_date = tree.xpath('//*[@id="sh_info"]/li[{}]/div[2]/span/text()'.format(num))
                dns_server = tree.xpath('//*[@id="sh_info"]/li[last()-3]/div[2]/text()')
                expire_time = time.mktime(time.strptime(expire_date[0], '%Y年%m月%d日'))
                free_time = expire_time - current_time

                if 0 < free_time < 2505600:
                    text += "更新时间：{0} <font color='red'> 域名 {1} 过期时间：{2} </font>注册商为：{3} DNS服务器：{4} 请注意及时续费!<br>".format( \
                        latest_time, domain, expire_date[0], register[0], dns_server)
                elif free_time < 0:
                    update_domain(domain)
                    text += "更新时间：{0} <font color='blue'> 域名 {1} 过期时间：{2} </font>注册商为：{3} DNS服务器：{4} 已过期！<br>".format( \
                        latest_time, domain, expire_date[0], register[0], dns_server)
                if expire_date is None:
                    print(domain)
                    break
        except Exception as e:
            print(e)

def send_mail(text):
    sender = ''
    pwd    = ''
    message = MIMEText(text, 'html', 'utf-8')
    message['From'] = Header('', 'utf-8')
    message['To'] = Header('', 'utf-8')
    message['Subject'] = Header('域名到期提醒', 'utf-8')

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
