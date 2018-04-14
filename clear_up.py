#-*-coding:utf-8-*-
import bs4
from bs4 import BeautifulSoup

def clear(document):
    document = str(document)
    soup = BeautifulSoup(document,'lxml')

    #将table标签的每行存入items
    lines = soup.table.find_all('tr')
    items = []
    for line in lines:
        lineList = []
        for item in line.find_all('td'):
            lineList.append(item.string)
        items.append(lineList)

    return items
