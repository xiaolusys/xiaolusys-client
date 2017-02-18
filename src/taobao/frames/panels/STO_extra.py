#-*- coding:utf8 -*-

import sys
sys.path.append("E:\src")
import requests
import json
from websocket import create_connection
from taobao.dao.models import MergeTrade,PackageOrder
import webbrowser
import random

print_info = {
    "cmd": "print",
    "requestID": "123458976",
    "version": "1.0",
    "task": {
        "taskID": "1",
        "preview": True,  
        "printer": "KM-118 LABEL(USB)",
        "notifyMode":"allInOne",
        "documents": []
    }
}

ts_receivers_info = [{'detail':'唐庄小区61栋405','province':'福建省','name':'杨雪丹','mobile':'13959256692','trade_id':'13959256692'},\
                     {'detail':'朝阳门南大街8号中粮福临门大厦','province':'北京','name':'杨雪雪','mobile':'13959256691','trade_id':'13959256691'},\
                     {'detail':'古槐镇竹田村四区90号','province':'福建','name':'刘叶萍','mobile':'15259141326','trade_id':'15259141326'}]

def get_STOthermal_no_print(session=None,*receivers_info,**po_wb):
    url = "http://admin.xiaolumm.com/thermal/STOthermal/get_exp_number"
    url2 = "http://192.168.1.8:8005/thermal/STOthermal/get_exp_number"
    print_info['task']['documents'] = []
    print_info['task']['taskID'] = str(random.uniform(1, 99999))
    auth = ('dev.huideng','yduk9s71')
    auth2 = ('hui.deng','139cnm')
    for i in receivers_info:
        result = requests.get(url=url,params={'detail':i['detail'],'province':i['province'],\
                                             'name':i['name'],'mobile':i['mobile'],\
                                             'city':i['city'],'district':i['district'],\
                                             'trade_id':i['trade_id']},auth=auth)
        params={'detail':i['detail'],'province':i['province'],\
                                             'name':i['name'],'mobile':i['mobile'],\
                                             'city':i['city'],'district':i['district'],\
                                             'trade_id':i['trade_id']}
        print "发货人信息"+json.dumps(params)
        result = json.loads(result.text)
        print result
        try:
            print_data = result['print_data']
        except:
            print u"此单不能申请申通热敏订单",i["trade_id"]
            print_data = dict()
            print_data['error_code'] = result['error_code']
            params={'detail':i['detail'],'province':i['province'],\
                                             'name':i['name'],'mobile':i['mobile'],\
                                             'city':i['city'],'district':i['district'],\
                                             'trade_id':i['trade_id']}
            params = json.dumps(params).encode("UTF-8")
            params = json.loads(params)
            print_data['detail'] = params
            return print_data
        waybill_code = result['waybill_code']
        po_wb[i['trade_id']]=waybill_code
    return po_wb


def get_STOthermal(session=None,*receivers_info):
    url = "http://admin.xiaolumm.com/thermal/STOthermal/get_exp_number"
    url2 = "http://192.168.1.8:8005/thermal/STOthermal/get_exp_number"
    print_info['task']['documents'] = []
    print_info['task']['taskID'] = str(random.uniform(1, 99999))
    auth = ('dev.huideng','yduk9s71')
    auth2 = ('hui.deng','139cnm')
    for i in receivers_info:
        result = requests.get(url=url,params={'detail':i['detail'],'province':i['province'],\
                                             'name':i['name'],'mobile':i['mobile'],\
                                             'city':i['city'],'district':i['district'],\
                                             'trade_id':i['trade_id']},auth=auth)
        params={'detail':i['detail'],'province':i['province'],\
                                             'name':i['name'],'mobile':i['mobile'],\
                                             'city':i['city'],'district':i['district'],\
                                             'trade_id':i['trade_id']}
        print "发货人信息"+json.dumps(params)
        result = json.loads(result.text)
        print result
        try:
            print_data = result['print_data']
        except:
            print_data = dict()
            print_data['error_code'] = result['error_code']
            params={'detail':i['detail'],'province':i['province'],\
                                             'name':i['name'],'mobile':i['mobile'],\
                                             'city':i['city'],'district':i['district'],\
                                             'trade_id':i['trade_id']}
            params = json.dumps(params).encode("UTF-8")
            params = json.loads(params)
            print_data['detail'] = params
            return print_data
        waybill_code = result['waybill_code']
        print u'开始更新面单号'
        print "-------------------------------------------------"
        # se = session.query(PackageOrder).filter(PackageOrder.pid==i['trade_id']).update({'operator':'jiashuai.li','out_sid':waybill_code,'is_express_print':1})
        print "-------------------------------------------------"


        document = {"documentID":waybill_code,"contents":[json.loads(print_data)]}
        print document
        print_info['task']['documents'].append(document)
        
#         print_info['task']['documents'][0]['contents'][0]['data']=result
#     result = requests.get(url=url,param={'detail':detail,'province':province,'name':name,'mobile':mobile})
#     result = json.loads(result)['print_data']
#     print_info['task']['documents'][0]['contents'][0]['data']=result
#     print_info['task']['printer']
    print_info['task']['documents'].sort(key=lambda document:int(document['documentID']),reverse=False)
    ws = create_connection("ws://127.0.0.1:13528")
    ws.send(json.dumps(print_info))
    res = ws.recv()   
    try:
        url = json.loads(res)['previewURL']
    except Exception,exc:
        print exc
        ws.close()
        return "printer error"
    print url 
    
    webbrowser.open(url=url,new=0,autoraise=True)   
    ws.close()       
    return "success"

def get_detail_info(session=None,*trade_id):
    receivers_info = []
    merge_orders = session.query(PackageOrder).filter(PackageOrder.pid.in_(trade_id))
    for i in merge_orders:
        receiver_info = dict()
        receiver_info['detail']=i.receiver_address.encode("UTF-8")
        receiver_info['mobile'] = i.receiver_mobile.encode("UTF-8")
        receiver_info['name'] = i.receiver_name.encode("UTF-8")
        receiver_info['province'] = i.receiver_state.encode("UTF-8")
        receiver_info['city'] = i.receiver_city.encode("UTF-8")
        receiver_info['district'] = i.receiver_district.encode("UTF-8")
        receiver_info['trade_id'] = i.pid
        receivers_info.append(receiver_info)
        #print i.receiver_address,i.receiver_mobile,i.receiver_name,i.receiver_state,i.pid
    return get_STOthermal(session,*receivers_info)
    
def get_detail_info_no_print(session=None,*trade_id):
    receivers_info = []
    po_wb = {}
    merge_orders = session.query(PackageOrder).filter(PackageOrder.pid.in_(trade_id))
    for i in merge_orders:
        receiver_info = dict()
        receiver_info['detail']=i.receiver_address.encode("UTF-8")
        receiver_info['mobile'] = i.receiver_mobile.encode("UTF-8")
        receiver_info['name'] = i.receiver_name.encode("UTF-8")
        receiver_info['province'] = i.receiver_state.encode("UTF-8")
        receiver_info['city'] = i.receiver_city.encode("UTF-8")
        receiver_info['district'] = i.receiver_district.encode("UTF-8")
        receiver_info['trade_id'] = i.pid
        receivers_info.append(receiver_info)
        #print i.receiver_address,i.receiver_mobile,i.receiver_name,i.receiver_state,i.pid
    return get_STOthermal_no_print(session,*receivers_info,**po_wb)


if __name__ == "__main__":
    
    get_STOthermal(*ts_receivers_info)
    
