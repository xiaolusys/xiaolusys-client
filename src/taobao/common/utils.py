#-*- coding:utf-8 -*-
'''
Created on 2012-7-23

@author: user1
'''
import time
import datetime
import os
import cStringIO
import Image
import ImageDraw
import ImageFont
import wx
import taobao

FONT_PATH = 'c:\Windows\Fonts\simsun.ttc'
IMAGE_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(taobao.__file__)))+'\\images\\'

def parse_datetime(dt):
    return datetime.datetime(*(time.strptime(dt,'%m/%d/%Y %H:%M:%S')[0:6]))

def pydate2wxdate(date):
    assert isinstance(date,(datetime.datetime,datetime.date))
    tt=date.timetuple()
    dmy = (tt[2],tt[1]-1,tt[0])
    return wx.DateTimeFromDMY(*dmy)

def wxdate2pydate(date):
    assert isinstance(date,wx.DateTime)
    if date.IsValid():
        ymd = map(int,date.FormatISODate().split("-"))
        return datetime.date(*ymd)
    else:
        return None

def gen_string_image(font_path,code_string):
    
    im   = Image.new("RGB",(250,200), "#2cf200")
    draw = ImageDraw.Draw(im)
    sans16 = ImageFont.truetype(font_path, 18)
    draw.text((40,60),unicode(code_string,'UTF-8'),font=sans16,fill='#0000ff')

    del draw
#    buf = cStringIO.StringIO()
#    im.save(buf,'jpg')
    return im


#if __name__ == "__main__":
#    app = wx.PySimpleApp(0)
#    wx.InitAllImageHandlers()
#    image = gen_string_image(FONT_PATH,'图片无法显示')
#
#    filename = os.path.abspath(os.path.dirname(os.path.dirname(taobao.__file__)))+'\images\unavailible.png'
#    image.save(filename)
#    app.MainLoop()
#    
    