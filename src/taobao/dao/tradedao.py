#-*- coding:utf8 -*-
'''
Created on 2012-6-4

@author: user1
'''
import sqlalchemy 
from sqlalchemy import func
from taobao.dao.dbsession import get_session
from taobao.dao.models import SystemConfig,ProductLocation, PackageOrder, PackageSkuItem
from taobao.dao import configparams as pcfg
from taobao.common.utils import getconfig


def get_oparetor():
    cfg = getconfig()
    return cfg.get('user','username')

def get_seller_ids():
    cfg = getconfig()
    return [i.strip() for i in cfg.get('user','seller_ids').split(',') if i.strip()]

def get_ware_id():
    cfg = getconfig()
    return cfg.get('user','ware_id')

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
    orders = session.query(PackageOrder).filter_by(merge_trade_id=trade_id,sys_status=pcfg.IN_EFFECT
                            ).filter(PackageOrder.gift_type!=pcfg.RETURN_GOODS_GIT_TYPE)
    return orders

def get_return_orders(session,trade_id):
    orders = session.query(PackageSkuItem).filter_by(merge_trade_id=trade_id,
                                                 gift_type=pcfg.RETURN_GOODS_GIT_TYPE, sys_status=pcfg.IN_EFFECT)
    return orders

def get_datasource_by_type_and_mode(status_type,print_mode=pcfg.NORMAL_MODE,session=None):
    """ 获取交易数据源   """
    
    if not session:
        session = get_session()
        
    datasource       = session.query(PackageOrder)
    counter          = session.query(func.count(PackageOrder.id))

    seller_ids = get_seller_ids()
    if seller_ids:
        datasource = datasource.filter(PackageOrder.seller_id.in_(seller_ids))
        counter    = counter.filter(PackageOrder.seller_id.in_(seller_ids))
        
    ware_id = get_ware_id()
    if int(ware_id) == 1:
        datasource = datasource.filter(PackageOrder.ware_by.in_([1, 3]))
        counter = counter.filter(PackageOrder.ware_by.in_([1, 3]))
    else:
        datasource = datasource.filter_by(ware_by=ware_id)
        counter = counter.filter_by(ware_by=ware_id)
    if status_type and status_type != pcfg.SYS_STATUS_ALL:
        datasource = datasource.filter_by(sys_status=status_type)
        counter    = counter.filter_by(sys_status=status_type)
    print 'debug:',ware_id,seller_ids
    datasource     = datasource.order_by(PackageOrder.pid,
                                             'priority desc','pid asc')
    
    return datasource,counter
            
def locking_trade(trade_id,operator,session=None):
    """ 锁定交易   """
    from taobao.dao.webapi import WebApi
    if not session:
        session = get_session()
    is_locked = False
    trade = session.query(PackageOrder).filter_by(pid=trade_id).first()
    if not trade.is_locked:
        WebApi.operate_packages([trade.id], operator)
    elif trade.operator == operator:
        is_locked = True
    
    return is_locked


def get_product_locations(product_id,sku_id=None,opn=False,session=None):
    
    if not session:
        session = get_session()
        
    params = {'product_id':product_id}    
    if sku_id:
        params['sku_id'] = sku_id

    locations = session.query(ProductLocation).filter_by(**params)
    
    sdict = {}
    for d in locations:
        
        dno = d.district.district_no
        pno = d.district.parent_no
        if sdict.has_key(pno):
            sdict[pno].add(dno)
        else:
            sdict[pno] = set([dno])
    
    if opn :
        pnos = sdict.keys()
        pnos.sort()
        return ''.join(pnos)
        
    ds = []
    for k,v in sdict.iteritems():
        ds.append(len(v) > 1 and '%s-[%s]'%(k,','.join(list(v))) or '%s-%s'%(k,v.pop()))
    
    return ','.join(ds)
    
  
