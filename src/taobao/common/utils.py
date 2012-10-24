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
import ConfigParser

FONT_PATH = 'c:\Windows\Fonts\simsun.ttc'
IMAGE_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(taobao.__file__)))+'\\images\\'
def parse_datetime(dt,format='%m/%d/%Y %H:%M:%S'):
    return datetime.datetime(*(time.strptime(dt,format)[0:6]))

def parse_date(dt,format='%m/%d/%Y'):
    return datetime.datetime(*(time.strptime(dt,format)[0:6]))

def format_date(dt,format="%Y-%m-%d"):
    return dt.strftime(format)

def format_datetime(dt,format="%Y-%m-%d %H:%M:%S"):
    return dt.strftime(format)

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

def getconfig():
    cf = ConfigParser.ConfigParser()
    config_path = os.path.abspath(os.path.dirname(taobao.__file__))
    cf.read(config_path+'/system.conf')
    return cf


class create_session():
    def __init__(self,parent):
        self.parent = parent
        if hasattr(parent, 'Session'):
            self.session = parent.Session
        else:
            from taobao.dao.dbsession import get_session
            self.session = get_session()
  
    def __enter__(self):
        from taobao.dao.models import SystemConfig
        from taobao.dao.dbsession import get_session
        try:
            self.session.query(SystemConfig).first()
        except:
            self.session = get_session()
            self.parent.Session = self.session
        return self.session

    def __exit__(self,type,value,traceback):
        
        if self.session:
            try:
                self.session.commit()
            except:
                try:
                    self.session.rollback()
                except:
                    pass


def logtime(tag=''):
    def outer(func):
        def wrap(*args,**kwargs):
            start_time = time.time()
            response = func(*args,**kwargs)
            end_time   = time.time()
            print 'tag(%s) consume seconds:'%tag,end_time-start_time
            return response
        return wrap
    return outer

#if __name__ == "__main__":
#    app = wx.PySimpleApp(0)
#    wx.InitAllImageHandlers()
#    image = gen_string_image(FONT_PATH,'图片无法显示')
#
#    filename = os.path.abspath(os.path.dirname(os.path.dirname(taobao.__file__)))+'\images\unavailible.png'
#    image.save(filename)
#    app.MainLoop()
#    
    