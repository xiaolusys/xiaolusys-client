#-*- coding:utf8 -*-
'''
Created on 2012-6-4

@author: user1
'''
import sqlalchemy 
from taobao.dao.dbsession import get_session
from taobao.dao.models import SystemConfig
from taobao.dao.models import MergeOrder,MergeTrade
from taobao.dao import configparams as pcfg
from taobao.common.utils import getconfig


def get_oparetor():
    cfg = getconfig()
    return cfg.get('user','username')
    
def get_per_request_num(session=None):
    per_request_num = 1
    
    if not session:
        session = get_session()
    try:
        sys_config = session.query(SystemConfig).first()
    except:
        pass
    else:
        per_request_num = sys_config.per_request_num
    return per_request_num>0 and per_request_num or 1

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
                MergeOrder.gift_type!=pcfg.RETURN_GOODS_GIT_TYPE)
    return orders

def get_return_orders(session,trade_id):
    orders = session.query(MergeOrder).filter_by(merge_trade_id=trade_id,
                                gift_type=pcfg.RETURN_GOODS_GIT_TYPE,sys_status=pcfg.IN_EFFECT)
    return orders

def get_datasource_by_type_and_mode(status_type,print_mode=pcfg.NORMAL_MODE,session=None):
    """ 获取交易数据源   """
    
    if not session:
        session = get_session()
        
    datasource       = session.query(MergeTrade)
    
    if status_type and status_type != pcfg.SYS_STATUS_ALL:
        datasource = datasource.filter_by(sys_status=status_type)

    if print_mode == pcfg.DIVIDE_MODE:
        operator         = get_oparetor()
        per_request_num  = get_per_request_num(session)
        locked_num       = 0
        
        divid_source     = datasource.filter_by(is_locked=True,operator=operator)
        if status_type == pcfg.SYS_STATUS_PREPARESEND and divid_source.count() == 0:

            for trade in datasource.filter_by(is_locked=False).order_by(
                            'priority desc',sqlalchemy.func.date(MergeTrade.pay_time),'logistics_company_id'):
                if locked_num >= per_request_num:
                    break
                row = session.query(MergeTrade).filter_by(id=trade.id,is_locked=False).update(
                     {'is_locked':True,'operator':operator},synchronize_session='fetch')

                if row >0:
                    locked_num += 1
        datasource = divid_source  
    else:
        datasource     = datasource.order_by('priority desc','pay_time asc')
 
    return datasource
            
def locking_trade(trade_id,operator,session=None):
    """ 锁定交易   """
    if not session:
        session = get_session()
    
    is_locked = False
    trade = session.query(MergeTrade).filter_by(id=trade_id).first()

    if not trade.is_locked:
        updaterows = session.query(MergeTrade).filter_by(id=trade_id,is_locked=False).update(
                    {'is_locked':True,'operator':operator},synchronize_session='fetch')
        if updaterows == 1:
            is_locked = True
    elif trade.operator == operator:
        is_locked = True
    
    return is_locked

