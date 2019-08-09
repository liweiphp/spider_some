#coding:utf-8
import requests
from recognise import *
from PIL import Image
import base64
import getpass
import time
import traceback
import sys


def login(username,passwd):
    try:
        session=requests.session()
        session.get("https://qypassport.xin.com/?returnUrl=http%3a%2f%2fqy.xin.com%2f").text
        imageRecognize=CaptchaRecognize()
        # image=Image.open('captcha.jpeg')
        # result=imageRecognize.recognise(image)
        result = imageRecognize.recogniseBaidu(session)
        string=''
        for item in result:
            string+=item
        print(string)
        data={
        'CheckCode':string,
        'LoginName':username,
        'Password':passwd,
        'returnUrl':'http://qy.xin.com/'
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:39.0) Gecko/20100101 Firefox/39.0"
            ,"X-Requested-With":"XMLHttpRequest"}
        result = session.post('https://qypassport.xin.com/Account/LoginPost',data=data,headers=headers).text
        res1 = json.loads(result)
        if not res1['IsSucess']:
        	signIn()
        session.get('https://qy.xin.com/').text
        api = 'https://qy.xin.com/user/integralsign'
        res2 = session.post(api).text
        print(res2)
        return session

    except Exception as e:
        print('exception',e.message)
        print sys._getframe().f_lineno, 'traceback.format_exc():\n%s' % traceback.format_exc()


def signIn():
    username='liwei16'
    # passwd=getpass.getpass('pwd:')
    passwd='We15300347187'
    session = login(username,passwd)
    

signIn()