#coding=utf-8
'''
Created on 2012-6-2

@author: user1
'''
import re
import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, BigInteger, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship, backref

Base = declarative_base()
#unuse 
#memo_compile = re.compile('^\((?P<key>\w+),(?P<value>[\w\W]+),(?P<memo>[\w\W]+)\)$')

class Order(Base):
    __tablename__ = 'shop_order'
    
    oid   = Column(BigInteger, primary_key=True)

    trade_id = Column(BigInteger, ForeignKey('shop_trade.id'))

    title =  Column(String(128),nullable=True)
    price =  Column(String(12),nullable=True)
    num_iid      = Column(BigInteger,nullable=True)

    item_meal_id = Column(BigInteger,nullable=True)
    sku_id       = Column(String(20),nullable=True)
    num          = Column(Integer,nullable=True)

    outer_sku_id = Column(String(20),nullable=True)
    total_fee    = Column(String(12),nullable=True)

    payment      = Column(String(12),nullable=True)
    discount_fee = Column(String(12),nullable=True)
    adjust_fee   = Column(String(12),nullable=True)

    modified     = Column(String(19),nullable=True)
    sku_properties_name = Column(String(88),nullable=True)
    refund_id    = Column(BigInteger,nullable=True)

    is_oversold  = Column(Boolean)
    is_service_order = Column(Boolean)

    item_meal_name   = Column(String(88),nullable=True)
    pic_path     = Column(String(128),nullable=True)

    seller_nick  = Column(String(32),nullable=True,index=True)
    buyer_nick   = Column(String(32),nullable=True,index=True)

    refund_status = Column(String(40),nullable=True)
    outer_id     = Column(String(64),nullable=True)

    cid    = Column(BigInteger,nullable=True)
    status = Column(String(32),nullable=True)

    class Meta:
        db_table = 'shop_order'
        
    def __repr__(self):
        return "<Order('%s','%s','%s')>" % (self.oid, self.seller_nick, self.buyer_nick)
        


class Trade(Base):
    __tablename__ = 'shop_trade'
    
    id           =  Column(BigInteger, primary_key=True)
    #serial_id    =  Column(String(16),unique=True,index=True,nullable=True)
    orders       =  relationship("Order", backref="trade")

    seller_id    =  Column(String(64),index=True,nullable=True)
    seller_nick  =  Column(String(64),nullable=True)
    buyer_nick   =  Column(String(64),nullable=True)
    type         =  Column(String(32),nullable=True)

    payment      =  Column(String(10),nullable=True)
    discount_fee =  Column(String(10),nullable=True)
    adjust_fee   =  Column(String(10),nullable=True)
    post_fee     =  Column(String(10),nullable=True)
    total_fee    =  Column(String(10),nullable=True)

    buyer_obtain_point_fee  =  Column(String(10),nullable=True)
    point_fee        =  Column(String(10),nullable=True)
    real_point_fee   =  Column(String(10),nullable=True)
    commission_fee   =  Column(String(10),nullable=True)

    created       =  Column(DateTime,index=True,nullable=True)
    pay_time      =  Column(DateTime,nullable=True)
    end_time      =  Column(DateTime,index=True,nullable=True)
    modified      =  Column(DateTime,index=True,nullable=True)
    consign_time  =  Column(DateTime,index=True,nullable=True)

    buyer_message    =  Column(String(1000),nullable=True)
    buyer_memo       =  Column(String(1000),nullable=True)
    seller_memo      =  Column(String(1000),nullable=True)

    buyer_alipay_no  =  Column(String(128),default='')
    receiver_name    =  Column(String(64),default='')
    receiver_state   =  Column(String(8),default='')
    receiver_city    =  Column(String(8),default='')
    receiver_district   =  Column(String(16),default='')
    
    receiver_address =  Column(String(64),default='')
    receiver_zip     =  Column(String(10),default='')
    receiver_mobile  =  Column(String(20),default='')
    receiver_phone   =  Column(String(20),default='')

    status        =  Column(String(32),nullable=True)
        
    def __repr__(self):
        return "<Trade('%s','%s','%s')>" % (self.id, self.seller_nick, self.buyer_nick)
    
#    def parse_memo2dictandstr(self):
#        if not self.seller_memo:
#            return None
#        memo_list = self.seller_memo.split('&')
#        memo_entries = []
#        property_dict = {}
#        for memo_str in memo_list:
#            memo_dict = memo_compile.search(memo_str)
#            if memo_dict:
#                memo_dict = memo_dict.groupdict()
#                key    = memo_dict['key']
#                value  = memo_dict['value']
#                memo   = memo_dict['memo']
#                property_dict[key] = value
#                memo_entries.append(memo)
#        return property_dict,memo_entries
    
    

class TradeExtraInfo(Base):
    """
    seller_memo:
    { 'sid':sellerid,'tid':tradeid,'post':postExpress,'addr':address,'data':
        [
            {'pid':productid1,'property':{'color':'红色'}}，
            {'pid':productid2,'property':{'color':'红色'，'size':'110*60'}}
        ]
    }
    """
    __tablename__ = 'shop_tradeextrainfo'
    
    tid   =  Column(BigInteger, primary_key=True)
    is_update_amount  =  Column(Boolean,default=False)
    is_picking_print  =  Column(Boolean,default=False)
    is_send_sms       =  Column(Boolean,default=False)
    
    modified          =  Column(DateTime,onupdate=datetime.datetime.now)
    seller_memo       =  Column(String(128),default='')
    
    
    def __repr__(self):
        return str(self.tid)
    
    
    
class Item(Base):
    __tablename__ = 'shop_item'
    
    num_iid   =  Column(String(64),primary_key=True)
    
    outer_id =  Column(String(64),nullable=True)
    num       =  Column(Integer,nullable=True)
    
    seller_cids    = Column(String(126),nullable=True)
    approve_status = Column(String(20),nullable=True)
    type           = Column(String(12),nullable=True)
    valid_thru     = Column(Integer,nullable=True)
    
    cid       =  Column(BigInteger,nullable=True)
    price     =  Column(String(12),nullable=True)
    postage_id     = Column(BigInteger,nullable=True)
    
    has_showcase   = Column(Boolean,default=False)
    modified       = Column(String(19),nullable=True)
    
    user_id   =  Column(String(32),nullable=True)
    nick      =  Column(String(64),nullable=True)
    list_time =  Column(DateTime,nullable=True)
    delist_time    = Column(DateTime,nullable=True)
    has_discount   = Column(Boolean,default=False)
    
    props     =  Column(String(200),nullable=True)
    title     =  Column(String(148),nullable=True)
    
    has_invoice    = Column(Boolean,default=False)
    pic_url   =  Column(String(256),nullable=True)
    detail_url     = Column(String(256),nullable=True)
    
    desc      =  Column(String(64),nullable=True)
    skus      =  Column(String(1500),nullable=True)
    
    def __repr__(self):
        return self.num_iid+'--'+self.outer_id+'--'+self.title
    
    
    
    
itemrulemap_table = Table('shop_app_itemrulemap', Base.metadata,
    Column('item_id', Integer, ForeignKey('shop_item.num_iid')),
    Column('traderule_id', Integer, ForeignKey('shop_app_traderule.id'))
)
    
class TradeRule(Base):
    __tablename__ = 'shop_app_traderule'
    
    id        =  Column(Integer, primary_key=True)
    formula   =  Column(String(64),nullable=True)
    memo      =  Column(String(64),nullable=True)
    
    formula_desc  =  Column(String(256),nullable=True)
    
    scope     =  Column(String(10))
    status    =  Column(String(2))
    
    items     =   relationship("Item",secondary=itemrulemap_table,backref="rules")
    
    def __repr__(self):
        return self.formula_desc+'--'+self.memo
    
    
    
class RuleFieldType(Base):
    __tablename__ =  'shop_app_rulefieldtype'
    
    field_name    = Column(String(64),primary_key=True)
    field_type    = Column(String(10))
    alias         = Column(String(64))
    default_value = Column(String(256),default='')
    
    products      = relationship("ProductRuleField", backref="field")
    def __repr__(self):
        return self.field_name+'--'+self.field_type
    
    
    
class ProductRuleField(Base):
    __tablename__ = 'shop_app_productrulefield'
    
    id        = Column(Integer,primary_key=True)
    outer_id  = Column(String(64),index=True)
    field_id  = Column(String(64), ForeignKey('shop_app_rulefieldtype.field_name'))
    
    custom_alias   = Column(String(256),default=True)
    custom_default = Column(String(256),default=True)
    
    def __repr__(self):
        return self.outer_id+'--'+self.field
       





    
    
    
    
        