# _*_ coding:utf-8 _*_
import time
import requests
import paramiko
import json
from lxml import etree


url = "http://xxx.xxx.xxx/submit?"
username = 'username'
passwd = 'passwd'
mirror_dir = '/tmp/test'
ip = 'xxx.xxx.xxx'
API=""

r = requests.session()
r.auth = (username, passwd)


def ssh_cmd(ip, port, cmd):
    # 建立 sshclient 对象
    s = paramiko.SSHClient()
    s.load_system_host_keys()
    # 允许将信任的主机自动加入到 host_allow 列表
    s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    s.connect(hostname=ip, username='root', port=port, key_filename='/root/.ssh/id_rsa')
    stdin, stdout, stderr = s.exec_command(cmd)
    result = stdout.readlines()
    s.close()
    return result

# 获取最近3天更新的目录
def get_dir():
    cmd = "find %s -maxdepth 2 -mindepth 2 -mtime -3 -type d" % (mirror_dir)
    dir_result = ssh_cmd(ip, 22, cmd)
    dir_list = [ dir.strip('\n') for dir in dir_result ]
    return dir_list

# 获取全部 ed2k 链接
def getall_ed2k_links():
    link = {
        'q': 'links'
    }
    req = r.get(url, params=link)
    tree = etree.HTML(req.text)
    result = tree.xpath("//pre/text()")[0].split('\n')
    result.pop()
    result.pop(0)
    return result

# 获取最新 ed2k 链接
def getnew_ed2k_links():
    link_text = "## 新增的ed2k链接\n"
    link_list = getall_ed2k_links()
    f = open("/root/ed2k_links.txt", "r")
    link_result = f.readlines()
    link_result = [link.strip('\n') for link in link_result]
    for link in link_list:
        if link not in link_result:
            link_text += "%s\n" % link
            record(link)
    if link_text!="":
        send_to_dingding(link_text)


# 记录下载链接
def record(link):
    f = open("/root/ed2k_links.txt", "a")
    f.write(link)
    f.write('\n')
    f.close()


# 添加目录分享
def add_share(dir_list):
    for dir in dir_list:
        share_cmd = "share 0 " + dir + " incoming_files"
        share = {
            'q': share_cmd
        }
        req = r.get(url, params=share)
        tree = etree.HTML(req.text)
        res = tree.xpath("//body/text()")
        if 'added' in res:
            print("{0} 已成功添加").format(dir)


def send_to_dingding(text):
    headers = {'content-type': 'application/json'}
    parames = {
        "msgtype": "markdown",
        "markdown": {
            "title": "ed2k链接",
            "text": text
        },
    }
    parames = json.dumps(parames)
    r = requests.post(API, data=parames, headers=headers)
    return r.text

if __name__ == '__main__':
    dir_list = get_dir()
    add_share(dir_list)
    time.sleep(180)
    getnew_ed2k_links()
