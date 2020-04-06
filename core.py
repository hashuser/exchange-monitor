from urllib import request
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import time
import json
import os

def get_info(currency):
    url = '''http://www.bankcomm.com/BankCommSite/simple/cn/whpj/queryExchangeResult.do?type=simple'''
    response = request.urlopen(url,timeout=20)
    response = response.read().decode('utf-8')
    position = response.find(currency)
    exchoffer = response[position:position+180].split('\r\n')[3].replace(' <td align="center">','').replace('</td>','')
    position = response.find('更新时间')
    update_time = response[position+5:position+24]
    return (exchoffer,update_time)

def send_email(sender,receiver,message,password):
    client = smtplib.SMTP_SSL('smtp.126.com',465)
    client.login(sender,password)
    client.send_message(message,sender,receiver)

def bot(currency,sender,receiver,password):
    info = get_info(currency)
    with open('data.json', 'r') as file:
        past_data = json.load(file)
    avarage = [0,0,0]
    for x in past_data[-720:]:
        avarage[0] += float(x[1])
    avarage[0] = avarage[0] / len(past_data[-720:])
    for x in past_data[-5040:]:
        avarage[1] += float(x[1])
    avarage[1] = avarage[1] / len(past_data[-5040:])
    for x in past_data[-20160:]:
        avarage[2] += float(x[1])
    avarage[2] = avarage[2] / len(past_data[-20160:])
    main_text = '更新时间:' + info[1] + '\n' + currency +'现汇卖出价:' + info[0] + '\n过去24小时平均价:' + str(round(avarage[0],2)) + '\n过去7天平均价:' + str(round(avarage[1],2)) + '\n过去28天平均价:' + str(round(avarage[2],2))
    message = MIMEText(main_text, 'plain', 'utf-8')
    message['Subject'] = Header(currency +'现汇卖出价提醒', 'utf-8')
    message['From'] = sender
    message['To'] = receiver
    send_email(sender,receiver,message,password)

def get_time(hour):
    UTC = time.gmtime(time.time())
    New_time = time.struct_time((UTC.tm_year,UTC.tm_mon,UTC.tm_mday,UTC.tm_hour+hour,UTC.tm_min,UTC.tm_sec,UTC.tm_wday,UTC.tm_yday,UTC.tm_isdst))
    return New_time

if __name__ == '__main__':
    if os.path.exists('config.json'):
        with open('config.json','r') as file:
            data = json.load(file)
    else:
        example = {'Currency':'','Sender_username':'','Sender_password':'','Receiver':''}
        with open('config.json', 'w') as file:
            json.dump(example, file, indent=4)
    if not os.path.exists('data.json'):
        example = []
        with open('data.json', 'w') as file:
            json.dump(example, file)
    while True:
        last_run = get_time(8).tm_hour
        if get_time(8).tm_hour in [9,11,13,15,17]:
            bot(data['Currency'], data['Sender_username'], data['Receiver'], data['Sender_password'])
        while last_run == get_time(8).tm_hour:
            with open('data.json','r') as file:
                past_data = json.load(file)
            info = get_info(data['Currency'])
            past_data.append([time.time(),info[0]])
            past_data.sort()
            with open('data.json','w') as file:
                json.dump(past_data, file)
            time.sleep(120)