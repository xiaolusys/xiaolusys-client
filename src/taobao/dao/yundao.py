import datetime
import MySQLdb
from taobao.common.utils import getconfig,format_datetime

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
