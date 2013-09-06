#-*- coding:utf8 -*-
import datetime
import MySQLdb
from taobao.dao.dbsession import get_session
from taobao.dao.models import ClassifyZone
from taobao.common.utils import getconfig,format_datetime


def get_classify_zone(state,city,district,session=None):
    """ 根据地址获取分拨中心  """
    if not session:
        session = get_session()
        
    lstate = len(state)>1 and state[0:2] or ''
    lcity  = len(city)>1  and city[0:2]  or ''
    ldistrict  = len(district)>1  and district[0:2]  or ''
    if district:
        czones = session.query(ClassifyZone).filter(ClassifyZone.state.like(lstate+'%'),
                    (ClassifyZone.city.like(ldistrict+'%'))|(ClassifyZone.district.like(ldistrict+'%')))
        
        if czones.count() == 1:
            return czones.first().branch.COMBO_CODE
        
        for czone in czones:
            if czone.city == district or czone.district == district:
                return czone.branch.COMBO_CODE
        
    if city:
        czones = session.query(ClassifyZone).filter(ClassifyZone.state.like(lstate+'%'),
                                                  ClassifyZone.city.like(lcity+'%'),ClassifyZone.district=='')
        if czones.count() == 1:
            return czones.first().branch.COMBO_CODE
        
        for czone in czones:
            if czone.city == city:
                return czone.branch.COMBO_CODE
            
    if state:
        czones = session.query(ClassifyZone).filter(ClassifyZone.state.like(lstate+'%'),
                                                  ClassifyZone.city=='',ClassifyZone.district=='')
        if czones.count() == 1:
            return czones.first().branch.COMBO_CODE
        
        for czone in czones:
            if czone.state == state:
                return czone.branch.COMBO_CODE
    
    return ''        
    


def get_yunda_conn():
    
    conn = MySQLdb.connect(host= "192.168.0.19",
                  user="root",
                  passwd="123",
                  db="ydwd")
    
    return conn

def insert_yunda_fjbak(txm,weight):
    
    conn = get_yunda_conn()
    weight = ('.' in weight) and float(weight) or float(weight)/1000.0
    
    weight = weight>0 and weight-weight*0.06 or 0
    
    cfg = getconfig()
    cr = conn.cursor()
    cr.execute ("INSERT INTO yjsm_bak(TXM,WPZL,DD,XJDD,YSFS,SJ,SMLB,SMY,SFD) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)", 
               (txm,
                str(round(weight,2)),
                cfg.get('custom','DD'),
                cfg.get('custom','XJDD'),
                cfg.get('custom','YSFS'),
                format_datetime(datetime.datetime.now()),
                cfg.get('custom','SMLB'),
                cfg.get('custom','SMY'),
                cfg.get('custom','SFD')))
    
    row = cr.fetchall()
    return row

#conn = get_yunda_conn()
#insert_yunda_fjbak('1200907504556','320')
#cr = conn.cursor()
#cr.execute('select * from yjsm_bak')
#print cr.fetchall()
#
#conn.close()
