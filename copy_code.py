import os
import requests
from bs4 import BeautifulSoup

n = 0
while n<1000:
    n += 1
    n = str(n)
    c = requests.get('http://122.225.19.20/CheckCode.aspx')
    picture = c.content
    local = os.getcwd()
    filelocal = os.path.join(local,"code")
    picture_local = os.path.join(filelocal,n+".jpg")
    with open(picture_local,"wb") as jpg:
        jpg.write(picture)
    n = int(n)

