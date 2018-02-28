#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import xlrd
import pymysql


mysql_host=""
mysql_port=
mysql_user=""
mysql_passwd=""
mysql_db=""


table=xlrd.open_workbook("domain.xlsx")
data=table.sheet_by_index(0)

conn=pymysql.connect(host=mysql_host, port=mysql_port, user=mysql_user, password=mysql_passwd, db=mysql_db)
cursor = conn.cursor()
sql="insert into domain_list (domain) values (%s)"
for num in range(1, data.nrows):
    domain = data.row_values(num)
    try:
        # 防止重复插入
        cursor.execute(sql, domain)
        #执行sql语句,必须得加这条
        conn.commit()
    except:
        conn.rollback()
    
cursor.close()
conn.close()
