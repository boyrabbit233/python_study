# _*_ coding:utf-8 _*_
import requests
import time
import base64


r = requests.session()

def get_img():
    '''
    获取验证码
    将验证码转换为base64编码
    :return:
    '''
    img_preurl="http://www.chaicp.com/home_cha/g_getcode/nocache="
    img_geturl=img_preurl+str(round(time.time()*1000))
    img_req = r.get(img_geturl)
    base64_data = base64.b64encode(img_req.content)
    print(base64_data)
    return base64_data

def recognize_img(base64_data):
    '''
    识别验证码并返回识别结果
    :return:
    '''
    image_data = "data:image/jpeg;base64," + base64_data.decode('utf-8')
    param = {
        'site': 'icp',
        'image': image_data
    }
    reco_url = "http://xxx.xxx.com/"
    reco = r.post(reco_url, data=param)
    code_text = reco.text
    print(code_text)
    return code_text


def check_icp(code_text):
    '''
    查询备案情况
    :return:
    '''
    icp_url = "http://www.chaicp.com/home_cha/ajax"
    param2 = {
        'ym': "baidu.com",
        'code': code_text
    }
    check_req = r.post(icp_url, data=param2)
    check_text = check_req.json()
    return  check_text


def main():
    flag = 1
#    try:
    while flag:

        base64_data = get_img()
        code_text = recognize_img(base64_data)
        check_text = check_icp(code_text)
        print(check_text['msg'])
        if '验证码错误' in check_text['msg']:
            print('验证码错误，重试ing...')
        elif '未备案或者备案取消' in check_text['msg']:
            flag = 0
            print('域名未备案')
        elif '验证码不能为空' in check_text['msg']:
            print('验证码不能为空，重试ing...')
        else:
            flag = 0
            print('有备案')
#    except Exception as e:
#        print(e)


if __name__ == "__main__":
    main()
