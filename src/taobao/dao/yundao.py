#-*- coding:utf8 -*-
import time
import datetime
import MySQLdb
import sys
import re
import hashlib
import base64
import urllib
import urllib2
import subprocess
from xml.dom import minidom
from taobao.dao import configparams as cfg
from taobao.dao.dbsession import get_session
from taobao.common.utils import TEMP_FILE_ROOT,getconfig
from taobao.dao.models import ClassifyZone,MergeTrade,BranchZone
from taobao.common.utils import getconfig,format_datetime
import webbrowser

SELECT    = 'select'
RECEIVE   = 'receive'
RECEIVE_MAILNO = 'receive_mailno'
MODIFY    = 'modify'
CANCEL    = 'cancel'
REPRINT   = 'reprint'
VALID     = 'valid'
ACCEPT    = 'accept'
TRANSITE  = 'transite'
ORDERINFO = 'orderinfo'

RECEIVE_ACTION = 'data'
CANCEL_ACTION = 'cancel_order'
REPRINT_ACTION = 'reprint_order'
VALID_ACTION = 'valid_order'
ACCEPT_ACTION = 'accept_order'
TRANSITE_ACTION = 'transite_info'

SELECT_API    = 'interface_select_reach_package.php'
RECEIVE_API   = 'interface_receive_order.php' 
MODIFY_API    = 'interface_modify_order.php'
CANCEL_API    = 'interface_cancel_order.php'
TRANSITE_API  = 'interface_transite_search.php'
ORDERINFO_API = 'interface_order_info.php'
PRINTFILE_API = 'interface_print_file.php'
RECEIVER_MAILNO_API = 'interface_receive_order__mailno.php'

ACTION_DICT = {
               RECEIVE:RECEIVE_ACTION,
               MODIFY:RECEIVE_ACTION,
               CANCEL:CANCEL_ACTION,
               ORDERINFO:RECEIVE_ACTION,
               TRANSITE:TRANSITE_ACTION,
               VALID:VALID_ACTION,
               REPRINT:REPRINT_ACTION,
               RECEIVE_MAILNO:RECEIVE_ACTION,
               }

API_DICT = {
               RECEIVE:RECEIVE_API,
               MODIFY:RECEIVE_API,
               CANCEL:CANCEL_API,
               ORDERINFO:ORDERINFO_API,
               TRANSITE:TRANSITE_API,
               VALID:CANCEL_API,
               REPRINT:PRINTFILE_API,
               RECEIVE_MAILNO:RECEIVER_MAILNO_API,
               }


#demon_url = 'http://orderdev.yundasys.com:10209/cus_order/order_interface/'
#PARTNER_ID = "YUNDA"
#SECRET     = "123456"

demon_url = 'http://order.yundasys.com:10235/cus_order/order_interface/'
PARTNER_ID = "10134210001"
SECRET     = "123456"


########################################## 分拨中心分配  ################################################

def get_zone_by_code(code,session=None):
    """ 根据编码获取网点及分拨中心   """
    if not session:
        session = get_session()
        
    czones = session.query(BranchZone).filter_by(barcode=code)
    
    return czones.first()

def get_classify_zone(state,city,district,address='',session=None):
    """ 根据地址获取分拨中心   """
    if not session:
        session = get_session()
        
    lstate = len(state)>1 and state[0:2] or ''
    lcity  = len(city)>1  and city[0:2]  or ''
    ldistrict  = len(district)>1  and district[0:2]  or ''
    
    if district:
        
        if address and ldistrict == u'吴江' and lstate == u'江苏':
            
            szds = None
            sz = session.query(BranchZone).filter_by(barcode='215201').first()
            if sz:
                szds = [ z.city for z in sz.classify_zone]
                
            if szds:
                
                rp   = re.compile('|'.join(szds))
                if rp.search(address):
                    return sz
             
            
        czones = session.query(ClassifyZone).filter(ClassifyZone.state.like(lstate+'%'),
                    (ClassifyZone.city.like(ldistrict+'%'))|(ClassifyZone.district.like(ldistrict+'%')))
        
        if czones.count() == 1:
            return czones.first().branch
        
        for czone in czones:
            if czone.city == district or czone.district == district:
                return czone.branch
        
    if city:
        czones = session.query(ClassifyZone).filter(ClassifyZone.state.like(lstate+'%'),
                                                  ClassifyZone.city.like(lcity+'%'),ClassifyZone.district=='')
        if czones.count() == 1:
            return czones.first().branch
        
        for czone in czones:
            if czone.city == city:
                return czone.branch
            
    if state:
        czones = session.query(ClassifyZone).filter(ClassifyZone.state.like(lstate+'%'),
                                                  ClassifyZone.city=='',ClassifyZone.district=='')
        if czones.count() == 1:
            return czones.first().branch
        
        for czone in czones:
            if czone.state == state:
                return czone.branch
    
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


########################################## 韵达二维码  ################################################

def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)

#生成创建订单XML
def gen_orders_xml(objs):
    
    _xml_list = ['<orders>']

    for obj in objs:
        _xml_list.append('<order>')
        _xml_list.append('<order_serial_no>%s</order_serial_no>'%obj['id'])
        _xml_list.append('<khddh>%s</khddh>'%obj['id'])
        _xml_list.append('<nbckh></nbckh>')
        _xml_list.append("""<sender><name>%s</name><company>%s</company>
                            <city>%s</city><address>%s</address>
                            <postcode>%s</postcode><phone>%s</phone>
                            <mobile>%s</mobile><branch></branch></sender>"""%(obj['sender_name'],
                                                                                obj['sender_company'],
                                                                                obj['sender_city'],
                                                                                obj['sender_address'],
                                                                                obj['sender_postcode'],
                                                                                obj['sender_phone'],
                                                                                obj['sender_mobile'],
                                                                                ))
        
        _xml_list.append("""<receiver><name>%s</name><company>%s</company>
                            <city>%s</city><address>%s</address>
                            <postcode>%s</postcode><phone>%s</phone>
                            <mobile>%s</mobile><branch></branch></receiver>"""%(obj['receiver_name'],
                                                                                obj['receiver_company'],
                                                                                obj['receiver_city'],
                                                                                obj['receiver_address'],
                                                                                obj['receiver_postcode'],
                                                                                obj['receiver_phone'],
                                                                                obj['receiver_mobile'],
                                                                                ))
 
        _xml_list.append('<weight></weight><size></size><value></value>')
        _xml_list.append('<collection_value></collection_value><special></special>')
        _xml_list.append('<item></item><remark></remark>')
        _xml_list.append(u'<cus_area1>分拣号:%s</cus_area1>'%obj['zone'])
        _xml_list.append(u'<cus_area2>宝贝亲，给5星+20字以上好评，就会有惊喜哦.</cus_area2>')
        _xml_list.append('<callback_id></callback_id>')
        _xml_list.append('<wave_no></wave_no></order>')
        
    _xml_list.append('</orders>')
    
    return ''.join(_xml_list).encode('utf8')
    
def get_objs_from_trade(trades,session=None):
    
    objs = []
    for trade in trades:
        
        zone = None
#        if trade.reserveo:
#            zone = get_zone_by_code(trade.reserveo,session=session)
        
        if not zone:
            zone = get_classify_zone(trade.receiver_state,trade.receiver_city,trade.receiver_district,address=trade.receiver_address,session=session)
        
        objs.append({"id":trade.id,
                     "sender_name":u"优尼世界",
                     "sender_company":u"优尼世界旗舰店",
                     "sender_city":u"上海,上海市",
                     "sender_address":u"",
                     "sender_postcode":u"",
                     "sender_phone":u"021-37698479",
                     "sender_mobile":u"",
                     "receiver_name":trade.receiver_name,
                     "receiver_company":u'',
                     "receiver_city":','.join([trade.receiver_state,trade.receiver_city,trade.receiver_district]),
                     "receiver_address":','.join([trade.receiver_state,trade.receiver_city,trade.receiver_district+trade.receiver_address]),
                     "receiver_postcode":trade.receiver_zip,
                     "receiver_phone":trade.receiver_phone,
                     "receiver_mobile":trade.receiver_mobile,
                     "zone":zone and zone.code or ''
                     })
        
    return objs
       
def parseTreeID2MailnoMap(doc):
    """ 订单查询结果转换成字典 """
    im_map = {}
    orders = doc.getElementsByTagName('response')
    for order in orders:
        status = getText(order.getElementsByTagName('status')[0].childNodes)
        order_mail_no = order.getElementsByTagName('mailno')
        
        if status != '1' and not order_mail_no:
            continue
        
        order_serial_no = getText(order.getElementsByTagName('order_serial_no')[0].childNodes)
        mailno   = getText(order_mail_no[0].childNodes)
        
        im_map[order_serial_no] = mailno
        
    return im_map
        
       
def handle_demon(action,xml_data,partner_id,secret):
    
    xml_data  = base64.encodestring(xml_data).strip()
    validate = hashlib.md5(xml_data+partner_id+secret).hexdigest()
    
    params = {'partnerid':partner_id,
          'version':'1.0',
          'request':ACTION_DICT[action],
          'xmldata':xml_data,
          'validation':validate
          }
    
    req = urllib2.urlopen(demon_url+API_DICT[action], urllib.urlencode(params))
    rep = req.read()       
    
    if action == REPRINT:
        return rep
        
    doc = minidom.parseString(rep)
    
    return doc
     
     
def create_order(ids,session=None):
    
    assert isinstance(ids,(list,tuple))
    
    trades = session.query(MergeTrade).filter(MergeTrade.id.in_(ids))
    objs   = get_objs_from_trade(trades,session=session)
    
    order_xml = gen_orders_xml(objs)
    
    tree = handle_demon(RECEIVE_MAILNO,order_xml,PARTNER_ID,SECRET)
            
    return tree
    

def modify_order(ids,session=None):
    
    assert isinstance(ids,(list,tuple))
    
    trades = session.query(MergeTrade).filter(MergeTrade.id.in_(ids))
    objs  = get_objs_from_trade([trades],session=session)
    
    order_xml = gen_orders_xml(objs)
    
    tree = handle_demon(MODIFY,order_xml,PARTNER_ID,SECRET)
    
    return tree
    
def cancel_order(ids):
    
    assert isinstance(ids,(list,tuple))
    
    order_xml = "<orders>"
    for i in ids:
        order_xml += "<order><order_serial_no>%s</order_serial_no></order>"%str(i)
        
    order_xml += "</orders>"
    
    tree = handle_demon(CANCEL,order_xml,PARTNER_ID,SECRET)
    
    return tree
    
def search_order(ids,force_update=False,session=None):
    
    assert isinstance(ids,(list,tuple))
    
    order_xml = "<orders>"
    for i in ids:
        order_xml += "<order><order_serial_no>%s</order_serial_no></order>"%str(i)
    
    order_xml += "</orders>"
    
    tree = handle_demon(ORDERINFO,order_xml,PARTNER_ID,SECRET)
    
    if not force_update:
        return parseTreeID2MailnoMap(tree)
    
    im_map = {}
    #更新订单二维码标识
    orders = tree.getElementsByTagName('response')
    for order in orders:
        status  = getText(order.getElementsByTagName('status')[0].childNodes)
        order_serial_no = getText(order.getElementsByTagName('order_serial_no')[0].childNodes)
        order_mail_no   = order.getElementsByTagName('mailno')
        mail_no = order_mail_no and getText(order_mail_no[0].childNodes) or None
        msg     = getText(order.getElementsByTagName('msg')[0].childNodes)
        if status == '1' and mail_no:
            
            session.query(MergeTrade).filter_by(id=order_serial_no,sys_status=cfg.SYS_STATUS_PREPARESEND)\
                .update({'is_qrcode':True,'out_sid':mail_no,},synchronize_session='fetch')
            
            im_map[order_serial_no] = mail_no
        else:
            
            session.query(MergeTrade).filter_by(id=order_serial_no,sys_status=cfg.SYS_STATUS_PREPARESEND)\
                .update({MergeTrade.reason_code:MergeTrade.reason_code+',1,',
                         MergeTrade.sys_memo:MergeTrade.sys_memo+msg,
                         MergeTrade.sys_status:cfg.SYS_STATUS_WAITAUDIT},synchronize_session='fetch')
        
    return im_map


def valid_order(ids):
    
    assert isinstance(ids,(list,tuple))
    
    order_xml = "<orders>"
    for i in ids:
        order_xml += "<order><order_serial_no>%s</order_serial_no></order>"%str(i)
    order_xml += "</orders>"
    
    tree = handle_demon(VALID,order_xml,PARTNER_ID,SECRET)
    
    return tree


def print_order(ids):
    
    assert isinstance(ids,(list,tuple))
    
    order_xml = "<orders>"
    for i in ids:
        order_xml += "<order><order_serial_no>%s</order_serial_no></order>"%str(i)
        
    order_xml += "</orders>"
    
    pdftext = handle_demon(REPRINT,order_xml,PARTNER_ID,SECRET)
    
    return pdftext

################################ 打印韵达pdf文档方法  ####################################

def printYUNDAPDF(trade_ids,direct=False,session=None):
                    
    pdfdoc  = print_order(trade_ids)
    #更新订单打印状态
    session.query(MergeTrade).filter(MergeTrade.id.in_(trade_ids))\
        .update({'is_express_print':True},synchronize_session='fetch')
    
    file_name = '%s%d.pdf'%(TEMP_FILE_ROOT,int(time.time()))
    with open(file_name,'wb') as f:
        f.write(pdfdoc)
    
    if direct:
        conf  =  getconfig()
        gsprint_exe = conf.get('custom','gsprint_exe')
        p = subprocess.Popen([gsprint_exe, file_name], 
                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.communicate()
    else:
        webbrowser.open(file_name)
