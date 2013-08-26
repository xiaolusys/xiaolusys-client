#-*- coding:utf8 -*-
'''
Created on 2012-6-4

@author: user1
'''
import sqlalchemy 
from sqlalchemy import func
from taobao.dao.dbsession import get_session
from taobao.dao.models import SystemConfig,MergeOrder,MergeTrade,ProductLocation,ClassifyZone
from taobao.dao import configparams as pcfg
from taobao.common.utils import getconfig


def get_oparetor():
    cfg = getconfig()
    return cfg.get('user','username')

def is_normal_print_limit(session=None):
    
    if not session:
        session = get_session()
    try:
        sys_config = session.query(SystemConfig).first()
    except:
        return True
    else:
        return sys_config.normal_print_limit
    
    
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
    counter          = session.query(func.count(MergeTrade.id))
    
    if status_type and status_type != pcfg.SYS_STATUS_ALL:
        datasource = datasource.filter_by(sys_status=status_type)
        counter    = counter.filter_by(sys_status=status_type)
        
    if print_mode == pcfg.DIVIDE_MODE:
        operator         = get_oparetor()
        per_request_num  = get_per_request_num(session)
        locked_num       = 0
        
        unfinish_divid_source     = session.query(MergeTrade).filter(MergeTrade.sys_status.in_(
            (pcfg.SYS_STATUS_PREPARESEND,pcfg.SYS_STATUS_WAITSCANCHECK,pcfg.SYS_STATUS_WAITSCANWEIGHT)))\
            .filter_by(is_locked=True,operator=operator,reason_code='')
        if status_type == pcfg.SYS_STATUS_PREPARESEND and unfinish_divid_source.count() == 0:
            for trade in datasource.filter_by(is_locked=False).order_by(
                            'priority desc',sqlalchemy.func.date(MergeTrade.pay_time),'logistics_company_id'):
                if locked_num >= per_request_num:
                    break
                row = session.query(MergeTrade).filter_by(id=trade.id,is_locked=False).update(
                     {'is_locked':True,'operator':operator},synchronize_session='fetch')
                if row >0:
                    locked_num += 1
        datasource = datasource.filter_by(is_locked=True,operator=operator)  
        counter    = counter.filter_by(sys_status=status_type)
        
    else:
        datasource     = datasource.order_by(sqlalchemy.func.date(MergeTrade.pay_time),'priority desc','shop_trades_mergetrade.pay_time asc')
    
    return datasource,counter
            
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


def get_product_locations(outer_id,outer_sku_id=None,session=None):
    
    if not session:
        session = get_session()
        
    params = {'outer_id':outer_id}    
    if outer_sku_id:
        params['outer_sku_id'] = outer_sku_id
    
    locations = session.query(ProductLocation).filter_by(**params)
    
    sdict = {}
    for d in locations:
        
        dno = d.district.district_no
        pno = d.district.parent_no
        if sdict.has_key(pno):
            sdict[pno].append(dno)
        else:
            sdict[pno] = [dno]
    
    ds = []
    for k,v in sdict.iteritems():
        ds.append(len(v) > 1 and '%s-[%s]'%(k,','.join(v)) or '%s-%s'%(k,v[0]))
    
    return ','.join(ds)
    
    
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
            return czones.first().zone
        
        for czone in czones:
            if czone.city == district or czone.district == district:
                return czone.zone
        
    if city:
        czone = session.query(ClassifyZone).filter(ClassifyZone.state.like(lstate+'%'),
                                                  ClassifyZone.city.like(lcity+'%'),ClassifyZone.district=='').first()
        if czone:
            return czone.zone
    
    return ''        
    
