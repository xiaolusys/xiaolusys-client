#-*- coding:utf8 -*-
'''
Created on 2012-7-23
@author: user1
'''
import re
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

INVALID_XML_CHAR = r'[$><^\|\]\[;\:\&\!\%\"\?]'
FONT_PATH = 'c:\Windows\Fonts\simsun.ttc'
IMAGE_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(taobao.__file__)))+'\\images\\'
MEDIA_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(taobao.__file__)))+'\\media\\'
TEMP_FILE_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(taobao.__file__)))+'\\tmpfile\\'

if not os.path.exists(IMAGE_ROOT):
    os.makedirs(IMAGE_ROOT)
    
if not os.path.exists(MEDIA_ROOT):
    os.makedirs(MEDIA_ROOT)
    
if not os.path.exists(TEMP_FILE_ROOT):
    os.makedirs(TEMP_FILE_ROOT)

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
    config_path = os.path.abspath(os.path.dirname(taobao.__file__))+'/system.conf'
    cf.read(config_path)
    return cf

def writeconfig(config):
    config_path = os.path.abspath(os.path.dirname(taobao.__file__))+'/system.conf'
    with open(config_path, "w") as f:
        config.write(f)


def escape_invalid_xml_char(xml_str):
    """ 过滤非法XML字符 """
    return re.sub(INVALID_XML_CHAR,'*',xml_str)

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
                self.session.flush()
            except Exception,exc:
                from taobao.common.logger import get_sentry_logger
                logger = get_sentry_logger()
                logger.error(exc.message,exc_info=True)

                    
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

def pinghost(hostid):
    try:
        pingurl = 'ping %s -n 2'%hostid
        ret = os.system(pingurl)
    except:
        ret = -1
    return ret
  

#if __name__ == "__main__":
#    app = wx.PySimpleApp(0)
#    wx.InitAllImageHandlers()
#    image = gen_string_image(FONT_PATH,'图片无法显示')
#
#    filename = os.path.abspath(os.path.dirname(os.path.dirname(taobao.__file__)))+'\images\unavailible.png'
#    image.save(filename)
#    app.MainLoop()
#    
    