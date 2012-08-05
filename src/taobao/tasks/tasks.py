#coding=utf-8
'''
Created on 2012-6-4
@author: user1
'''
import time
import json
import datetime
from taobao.dao.dbsession import get_session
from taobao.dao.tradedao import get_or_create_model
from taobao.dao.models import MergeTrade,Item,Order,SubPurchaseOrder
from taobao.common.environment import get_template
from taobao.dao.configparams import SYS_STATUS_PREPARESEND ,TRADE_STATUS_WAIT_SEND_GOODS
import logging

logger = logging.getLogger('task.exception')

"""
trade_dict = {
            'trade_serial':None,
            'trade_id':None,
            'seller_nick':None,
            'post_date':None,
            'seller_nick':None,
            'order_nums':None,
            'total_fee':None,
            'discount_fee':None,
            'payment':None,
            'receiver_name':None,
            'receiver_phone':None,
            'receiver_mobile':None,
            'receiver_state':None,
            'receiver_city':None,
            'receiver_district':None,
            'receiver_address':None,
            'buyer_memo':None,
            'seller_memo':None,
            'orders':[
                {
                    'outer_iid':None,
                    'item_name':None,
                    'properties':None,
                    'num':None,
                    'price':None,
                    'discount_fee':None,
                    'payment':None
                }
            ]
        }
"""


def get_order_property_memo(oid,item_data):
    if not item_data:
        return None 
    for data in item_data:
        if data['pid']==oid:
            return data['property']
    return None


def fields_for_propertys(fields,properties):
    field_properties = ''
    for field in fields:
        field_name = field.field.field_name
        if field_name in properties.keys:
            field_properties += properties[field_name]+' '
        else :
            return None
    
    return field_properties    


def getTradePickingData(trade_ids=[]):
    session = get_session()
    send_trades  = session.query(MergeTrade).filter(MergeTrade.tid.in_(trade_ids))
    
    picking_data_list = []
    for trade in send_trades:
        trade_data = {}
        dt         = datetime.datetime.now() 
                
        trade_data['trade_serial'] = int(time.time()*100%10000000)
        trade_data['trade_id']     = trade.id
        trade_data['seller_nick']  = trade.seller_nick
        trade_data['post_date']    = dt
        trade_data['buyer_nick']        = trade.buyer_nick
        
        trade_data['order_nums']   = 0
        trade_data['total_fee']    = trade.total_fee
        trade_data['discount_fee'] = trade.discount_fee
        trade_data['payment']      = trade.payment
        
        
        trade_data['receiver_name']     = trade.receiver_name
        trade_data['receiver_phone']    = trade.receiver_phone
        trade_data['receiver_mobile']   = trade.receiver_mobile
        
        trade_data['receiver_state']    = trade.receiver_state
        trade_data['receiver_city']     = trade.receiver_city
        trade_data['receiver_district'] = trade.receiver_district
        trade_data['receiver_address']  = trade.receiver_address
        trade_data['sys_memo']   = trade.sys_memo
        trade_data['orders']       = [] 
        
        gather_memo = []
        is_fenxiao = trade.type == 'fenxiao'
        if is_fenxiao:
            orders = session.query(SubPurchaseOrder).filter_by(id=trade.tid,order_200_status=TRADE_STATUS_WAIT_SEND_GOODS)
        else:
            orders = session.query(Order).filter_by(trade_id=trade.tid,refund_status='')
            
        for order in trade.orders:
            order_data = {} 
            trade['order_nums']  += order.num
            order_data['outer_id']  = order.item_outer_id if is_fenxiao else order.outer_id 
            order_data['item_name'] = order.title
            order_data['num']       = order.num
            order_data['price']     = order.price
            order_data['discount_fee'] = order.discount_fee
            order_data['payment']   = order.payment
            order_data['properties'] = order.sku_properties if is_fenxiao else order.sku_properties_name
            
            trade_data['orders'].append(order_data)
                                       
    return picking_data_list
                
                    
#            #商品备注需要的自定义字段
#            fields = session.query(ProductRuleField).filter_by(outer_id=order.outer_id)
#            #该交易客服备注的订单属性 
#            property = get_order_property_memo(order.oid,item_data) 
#            #判断交易备注是否与定义的字段匹配，否则该不能发货
#            field_properties = fields_for_propertys(fields,property)
#            if field_properties == None: 
#                can_print = False
#                break 
#            
#            sku_properties = ''
#            for sku in order.sku_properties_name.split(';'):
#                if sku:
#                    skus = sku.split(':')
#                    if len(skus) == 2:
#                        sku_properties += skus[1]
#                    elif len(skus) == 1:
#                        sku_properties += skus[0] 
#                
#            order_data['properties']  = sku_properties+field_properties
#            for rule in item.rules:
#                try:
#                    if eval(rule.formula):
#                        gather_memo.append(rule.memo)
#                except Exception,exc:
#                    pass
        
#        if can_print:             
#            for rule in global_rules:
#                try:
#                    if eval(rule.formula):
#                        gather_memo.append(rule.memo)
#                except Exception,exc:
#                    pass
#            trade_data['seller_memo'] = ','.join(gather_memo)
#            picking_data_list.append(trade_data)

#def sendSmsToUnmemoBuyerTask(limit_times=10000):
#    
#    session = get_session()
#    item_outer_iids = session.query(ProductRuleField.outer_id)\
#                .distinct('shop_app_productrulefield_outer_id').all()
#    trades  = session.query(Trade).filter_by(status='WAIT_SELLER_SEND_GOODS')
#    template = get_template('send_sms_template.txt',encoding='utf8')
#    
#    counts = 0
#    for trade in trades:
#        trade_extra_info = get_or_create_model(session,TradeExtraInfo,tid=trade.id)
#        for order in trade.orders:
#            if order.outer_id in item_outer_iids \
#                and not trade.buyer_memo \
#                and not trade_extra_info.is_send_sms:
#                
#                item  = session.query(Item).filter_by(num_iid=order.num_iid).first()
#                trade_memo = template.render(trade=trade,item=item)
#                
#                buyer_call = trade.receiver_mobile
#                #send_message_to_buyer(trade_memo,buyer_call)
#                trade_extra_info.is_send_sms = True 
#                session.commit()              
#                time.sleep(1)
#                counts += 1
#        print 'counts:',counts
#        if counts >= limit_times:        
#            break         

    
    