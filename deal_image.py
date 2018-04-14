#-*-coding:utf-8-*-
from PIL import Image,ImageFilter,ImageCms
import os
import numpy as np
from collections import Counter

#diamon函数定义像素点周围8块的像素值的和
def diamon(x,y,im_1):
    n = 0
    for a in range(x-1,x+2):
        for b in range(y-1,y+2):
            n += im_1.getpixel((a,b))
    n = n - im_1.getpixel((x,y)) #因为中间的不算，所以减去(x,y)
    return n

def im_deal(image_1):

    im = Image.open(image_1)
    width = im.size[0]
    height = im.size[1]

    im_rgb = im.convert("RGB")
    for x in range(width):
        for y in range(height):
            r,g,b = im_rgb.getpixel((x,y))
            if b and g == 0:
                im_rgb.putpixel([x,y],(0,0,0))
            else:
                im_rgb.putpixel([x,y],(255,255,255))
    im_1 = im_rgb.convert('1')
    #编写过滤函数，以像素点为核心的3X3块里的黑块为基准
    for x in range(1,(width-1)):
        for y in range(1,(height-1)):
            z = im_1.getpixel((x,y))
            if z == 0:
                if diamon(x,y,im_1) >= white*7:   #白值不能超过7个
                    im_1.putpixel([x,y],255)


    return im_1

na = 0
white = 255 
black = 0
local = os.getcwd()
filelocal = os.path.join(local,"code")
file_deal = os.path.join(local,"code_deal")
file_list = os.listdir(filelocal)
file_list.remove('Thumbs.db')




for file_name in file_list:
    na += 1 
    image_1 = os.path.join(filelocal,file_name)
    imag = im_deal(image_1)
    file_new = os.path.join(file_deal,str(na) + ".bmp")
    imag.save(file_new)
