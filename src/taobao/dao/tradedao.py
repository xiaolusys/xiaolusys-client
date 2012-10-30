'''
Created on 2012-6-4

@author: user1
'''
from taobao.dao.dbsession import get_session
from taobao.dao.models import MergeOrder
from taobao.dao.configparams import TRADE_TYPE,TRADE_STATUS,SHIPPING_TYPE,SYS_STATUS,SYS_STATUS_FINISHED,SYS_STATUS_PREPARESEND,IN_EFFECT,\
    SYS_STATUS_INVALID,SYS_STATUS_WAITSCANWEIGHT,SYS_STATUS_WAITSCANCHECK,NO_REFUND,REFUND_CLOSED,SELLER_REFUSE_BUYER,TRADE_STATUS_WAIT_CONFIRM_GOODS


def get_or_create_model(session,model_class,**kwargs):
    model = session.query(model_class).filter_by(**kwargs).first()
    if model:
        return model
    else :
        model = model_class(**kwargs)
        session.add(model)
        return model

def get_used_orders(session,trade_id):
    orders = session.query(MergeOrder).filter_by(merge_trade_id=trade_id,sys_status=IN_EFFECT).filter(
                MergeOrder.status.in_(('WAIT_SELLER_SEND_GOODS','WAIT_CONFIRM,WAIT_SEND_GOODS','CONFIRM_WAIT_SEND_GOODS',TRADE_STATUS_WAIT_CONFIRM_GOODS)),
                MergeOrder.refund_status.in_((NO_REFUND,REFUND_CLOSED,SELLER_REFUSE_BUYER)))
    return orders