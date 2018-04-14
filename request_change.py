#-*-coding:utf-8-*-
import requests
from bs4 import BeautifulSoup
import re

def ne_code():
    url = "http://122.225.19.20/"
    resonse = requests.get(url+"default2.aspx")
    r = resonse.url
    if re.search(r"\w{24}",r) == None:
        print("no")
        new_url = "/"
        return new_url
    new = re.search(r"\w{24}",r).group()
    new_url = str("("+new+")")
    return new_url
ne_code()

input = ""
