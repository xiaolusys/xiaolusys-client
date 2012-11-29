'''
Created on 2012-6-4

@author: user1
'''
from taobao.dao.dbsession import get_session
from taobao.dao.models import MergeOrder
from taobao.dao import configparams as pcfg


def get_or_create_model(session,model_class,**kwargs):
    model = session.query(model_class).filter_by(**kwargs).first()
    if model:
        return model
    else :
        model = model_class(**kwargs)
        session.add(model)
        return model

def get_used_orders(session,trade_id):
    orders = session.query(MergeOrder).filter_by(merge_trade_id=trade_id,sys_status=pcfg.IN_EFFECT).filter(
                MergeOrder.status.in_((pcfg.TRADE_STATUS_WAIT_SEND_GOODS,pcfg.TRADE_STATUS_WAIT_CONFIRM_GOODS)),
                MergeOrder.refund_status.in_((pcfg.NO_REFUND,pcfg.REFUND_CLOSED,pcfg.SELLER_REFUSE_BUYER,pcfg.WAIT_SELLER_AGREE)))
    return orders