#!coding=utf-8
import requests
import sys
import smtplib
import time
import os
from email.mime.text import MIMEText
from email.header import Header

if sys.getdefaultencoding() != 'utf-8': 
 reload(sys) 
 sys.setdefaultencoding('utf-8')

api = 'http://hq.sinajs.cn/list='
def main(code):
    requests.adapters.DEFAULT_RETRIES = 5
    while True:
        time.sleep(20)
        if not allow_time():
            continue
        #bean_move()
        stock_list = []
        if code:
            stock_list.append(code)
        else:
            f = open("/shell/code.txt",'r')
            while True:
                line = f.readline()
                if line.find('#') != -1:#找到# pass
                    continue
                code_arr = line.split(' ')
                if not line:
                    break
                stock_list.append(code_arr[0])
            f.close()
        while stock_list:
            stock_code = stock_list.pop()
            result = requests.get(api+stock_code,headers={'Connection':'close'})
            stock_con = result.text
            stock_arr = stock_con.split('=')
            if stock_code.find('sz') == -1 and stock_code.find('sh') == -1 and stock_code.find('hk') == -1:
                is_future = True #是期货
            else:
                is_future = False #不是期货
            if stock_code.find('hk') != -1:
            	is_hk = True
            else:
            	is_hk = False

            if is_future: #期货
                stock_info_arr = stock_arr[1].split(',');
                buy_current_value = stock_info_arr[6]
                sale_current_value = stock_info_arr[7]
                stock_name = stock_info_arr[0]
                max_value = stock_info_arr[3]
                min_value = stock_info_arr[4]
                expire_time = stock_info_arr[17]
            else:
                stock_info_arr = stock_arr[1].split(',');
                if is_hk:
                	stock_name = stock_info_arr[1]
                	current_value = stock_info_arr[6]
                else:
                	current_value = stock_info_arr[3]
                	stock_name = stock_info_arr[0]
                max_value = stock_info_arr[4]
                min_value = stock_info_arr[5]
            if is_future:
                msg = '%s，当前buy:%s,当前sale:%s,最高%s,最低%s' % (stock_name,buy_current_value,sale_current_value,max_value,min_value)
            else:
                msg = '%s，当前%s,最高%s,最低%s' % (stock_name,current_value,max_value,min_value)
            print(msg)
            if float(max_value)==0 or float(min_value)==0:
                continue
            if is_future:
                if buy_current_value>=max_value:
                    msg = '%s上升，当前%s,最高%s,最低%s' % (stock_name,buy_current_value,max_value,min_value)
                    send_mail(msg)
                elif sale_current_value<=min_value:
                   msg = '%s下降，当前%s,最高%s,最低%s' % (stock_name,sale_current_value,max_value,min_value)
                   send_mail(msg)
            else:                
                if current_value>=max_value:
                    msg = '%s上升，当前%s,最高%s,最低%s' % (stock_name,current_value,max_value,min_value)
                    send_mail(msg)
                elif current_value<=min_value:
                   msg = '%s下降，当前%s,最高%s,最低%s' % (stock_name,current_value,max_value,min_value)
                   send_mail(msg)

def bean_move():
    date = '1901'
    bean_code = 'B'
    bean_oil_code = 'Y'
    bean_pulp_code = 'M'
    bean_arr = split_arr(api+bean_code+date)
    bean_oil_arr = split_arr(api+bean_oil_code+date)
    bean_pulp_arr = split_arr(api+bean_pulp_code+date)
    bean_current_value = float(bean_arr[7])
    bean_oil_current_value = float(bean_oil_arr[7])
    bean_pulp_current_value = float(bean_pulp_arr[7])
    will_price = bean_oil_current_value*0.2+bean_pulp_current_value*0.8
    if bean_current_value > will_price:
        print('bean[%f] is hight,price well:%s' % (bean_current_value,will_price))
    else:
        print('bean[%f] is low,price well:%s' % (bean_current_value,will_price))


def split_arr(api_url):
    result = requests.get(api_url,headers={'Connection':'close'})
    stock_con = result.text
    stock_arr = stock_con.split('=')
    stock_arr = stock_arr[1].split(',')
    return stock_arr

def send_mail(message):
    sender = '1641439692@qq.com'  
    receiver = '472689331@qq.com'
    subject = '提醒'  
    smtpserver = 'smtp.qq.com'
    smtpport = 465
    username = '1641439692@qq.com'  
    password = 'pvoeqxhfvumtdibe'
    
    msg = MIMEText(message,'html','utf-8')#中文需参数‘utf-8'，单字节字符不需要  
    msg['Subject'] = Header(subject, 'utf-8')
    msg['To'] = receiver
    msg['From'] = sender
    try:
        smtp = smtplib.SMTP_SSL(smtpserver,smtpport)
        smtp.login(username, password)
        smtp.sendmail(sender, receiver, msg.as_string())
        smtp.quit()
    except Exception as e:
        print(e)
    #根据当前星期&&小时段限制脚本运行
def allow_time():
    current_time = get_time()
    hours_min = float(current_time[0])
    week = int(current_time[1])
    allow_time_len = [[9.30,11.30],[13.0,15.0]]
    if week in [0,6]:
        return False
    for time_len in allow_time_len:
            if hours_min>=time_len[0] and hours_min<=time_len[1]:
                    return True
    return False

def get_time():
    # os.system('ntpdate -s 1.cn.pool.ntp.org')
    return [time.strftime("%H.%M"),time.strftime("%w")]


if __name__ == '__main__':
    if len(sys.argv)>1:
        code = sys.argv[1]
        main(code)
    else:
        main(0)
