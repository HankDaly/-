#-*-coding:utf-8-*-
import os
import os.path
import bs4
import requests
from bs4 import BeautifulSoup
import sys
from clear_up import clear
from request_change import ne_code
import random
import re
import shutil
import tensorflow as tf
import numpy as np
import time
from deal_image import im_deal

from train_tf import convert2gray
from train_tf import vec2text
from train_tf import MAX_CAPTCHA
from train_tf import CHAR_SET_LEN
from train_tf import X
from train_tf import keep_prob
from train_tf import crack_captcha_cnn
from PIL import Image


import importlib


importlib.reload(sys)

n_cod = ne_code()
studentnumber = "0"
password = "0"

def students_message():
    studentnumber = str(input('请输入你的学号'))
    password = str(input('请输入你的密码'))
    return studentnumber,password

#定义new_code函数，实时反馈验证码
def new_code(r):
    if re.search(r"\w{24}",r) == None:
        print("no")
        new_url = "/"
        return new_url
    new = re.search(r"\w{24}",r).group()
    new_url = str("("+new+")")
    return new_url

#定义get_headers函数，可以将复制下来的Headers分成字典
def getHeaders(raw_head):
    headers={}
    for raw in raw_head.split('\n'):
        headerKey = raw.split(':',1)[0]
        headerValue = raw.split(':',1)[1]
        headers[headerKey]=headerValue
    return headers

#登录时的Header
login_head = '''Accept:text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8
Accept-Encoding:gzip, deflate
Accept-Language:zh-CN,zh;q=0.9
Cache-Control:max-age=0
Content-Length:201
Content-Type:application/x-www-form-urlencoded
Host:122.225.19.20
Origin:http://122.225.19.20
Proxy-Connection:keep-alive
Referer:http://122.225.19.20/'''+n_cod+"/"+'''default2.aspx
Upgrade-Insecure-Requests:1
User-Agent:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'''

#构建get的表单，这里很关键
get_headers = '''Accept:text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8
Accept-Encoding:gzip, deflate
Accept-Language:zh-CN,zh;q=0.9
Host:122.225.19.20
Proxy-Connection:keep-alive
Referer:http://122.225.19.20/'''+n_cod+"/"+"xs_main.aspx?xh="+studentnumber+'''
Upgrade-Insecure-Requests:1
User-Agent:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'''

#查询页面头部
mark_head = '''Accept:text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8
Accept-Encoding:gzip, deflate
Accept-Language:zh-CN,zh;q=0.9
Cache-Control:max-age=0
Host:122.225.19.20
Proxy-Connection:keep-alive
Referer:http://122.225.19.20/'''+n_cod+"/"+"xs_main.aspx?xh="+studentnumber+'''
Upgrade-Insecure-Requests:1
User-Agent:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'''


#输入我查表单获得的参数以及不变的参数（学号，密码）
url = "http://122.225.19.20/"+n_cod #学校访问地址，表单中获得
imgurl = "http://122.225.19.20/"+n_cod+"/CheckCode.aspx" #验证码地址，checkcode中获得

output = crack_captcha_cnn()
saver = tf.train.Saver()
sess = tf.Session()
saver.restore(sess, ".model/crack_capcha.model-6900")


#验证码识别
def crack_captcha(image,output,sess):

    image = convert2gray(image).flatten() / 255  # 一维化
    predict = tf.argmax(tf.reshape(output, [-1, MAX_CAPTCHA, CHAR_SET_LEN]), 2)

    text_list = sess.run(predict, feed_dict={X: [image], keep_prob: 1})

    text = text_list[0].tolist()
    vector = np.zeros(MAX_CAPTCHA * CHAR_SET_LEN)
    i = 0
    for n in text:
        vector[i * CHAR_SET_LEN + n] = 1
        i += 1

    predict_text = vec2text(vector)
    return predict_text

def login_in():
    
    #访问教务系统，获取__VIEWSTATE值、验证码
    s = requests.Session()
    response = s.get(url+"/default2.aspx")
    #用正则表达式匹配__VIEWSTAT值,或者直接用beautifulsoup找到valu的值，这里用了后者。
    soup = BeautifulSoup(response.text,"lxml")
    __VIEWSTATE = soup.find("input",attrs={'name':'__VIEWSTATE'}).get("value")
    #获取验证码
    imgresponse = s.get(imgurl,stream=True)
    image = imgresponse.content
    local = os.getcwd() #获取本文件的路径
    filelocal = os.path.join(local,"code.jpg") #验证码名为code
    with open(filelocal,"wb") as jpg:
        jpg.write(image) #将文件保存到本地

    ps_image = im_deal(filelocal)  #处理验证码
    fileps = os.path.join(local,"code.bmp")
    ps_image.save(fileps)
    one_ps_image = np.array(Image.open(fileps))

    code_text = crack_captcha(one_ps_image,output,sess)

    #获得cnn识别后的验证码
    code = code_text
    print(code)
    #数据都拿到后，构建post

    data = {
    "RadioButtonList1":'%D1%A7%C9%FA',
    "__VIEWSTATE":__VIEWSTATE,
    "txtUserName":studentnumber,
    "Textbox1":"",
    "Textbox2":password,
    "txtSecretCode":code,
    "Button1":"",
    "lbLanguage":"",
    "hidPdrs":"",
    "hidsc":""
     }
    #获取登录界面
    headers = getHeaders(login_head)
    #登录教务系统
    res = s.post(url+'/default2.aspx',data=data,headers=headers)

    #登录成功
    #获取验证码

    #主页面
    #获取成绩查询页面的url
    headers = getHeaders(get_headers)
    page = s.get(url+"/xs_main.aspx?xh="+studentnumber,headers=headers)
    print(url+"/xs_main.aspx?xh="+studentnumber)
    soup2 = BeautifulSoup(page.text,'lxml')
    markurl = soup2.find("a",attrs={'onclick':"GetMc('成绩查询');"}).get("href")
    print(markurl)


    #获取头部
    headers = getHeaders(mark_head)
    #表单
    mark_data = {
    "__EVENTTARGET":"",
    "__EVENTARGUMENT":"",
    "__VIEWSTATE":"",
    "hidLanguage":"",
    "ddlXN":"",
    "ddlXQ":"",
    "ddl_kcxz":"",
    "btn_zcj":u"历年成绩".encode('gb2312','replace')
    }
    #获取__VIEWSTATE
    markpage = s.get(url+"/"+markurl,headers=headers)
    soup3 = BeautifulSoup(markpage.text,"lxml")
    __VIEWSTATE = soup3.find("input",attrs={'name':'__VIEWSTATE'}).get("value")
    mark_data['__VIEWSTATE']=__VIEWSTATE

    #提交表单，获取成绩界面
    markpage = s.post(url+"/"+markurl,mark_data,headers=headers)
    soup4 = BeautifulSoup(markpage.text,'lxml')

    marktable = str(soup4.find_all(id="Datagrid1")[0])
    marklist =  clear(marktable)
    return marklist




def deal_marklist(marklist):
    for line in marklist:
            for column in [0,1,3,4,6,7,8]:
                print('%-20s' % line[column],end = '')
            print("")

def error():
    global boom
    try:
        boom = login_in()        
    except AttributeError as e:
        print("验证失败")
        error()


if __name__ == '__main__':
    studentnumber,password = students_message()
    boom = []
    error()
    deal_marklist(boom)    
    
