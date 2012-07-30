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

class Category(Base):
    __tablename__ = 'shop_categorys_category'
    
    cid     = Column(Integer,primary_key=True)
    
    products  =  relationship("Product",backref="category")
    items     =  relationship("Item",backref="category")
    
    parent_cid = Column(Integer,index=True,nullable=True)
    name    = Column(String(32))
    
    is_parent  = Column(Boolean,default=True)
    status  = Column(String(7))
    sort_order = Column(Integer,nullable=True)
    
    def __repr__(self):
        return "<Category('%s','%s','%s')>" % (str(self.cid), str(self.parent_cid), self.name)
 
 
 
class Product(Base):
    __tablename__ = 'shop_items_product'
    outer_id = Column(String(64),primary_key=True)
    name     = Column(String(64),nullable=True)
    
    category_id = Column(Integer, ForeignKey('shop_categorys_category.cid'))
    
    collect_num = Column(Integer,nullable=True)
    price    = Column(String(10),nullable=True)
    
    created  = Column(DateTime,index=True,nullable=True)
    modified = Column(DateTime,index=True,nullable=True)
    
    def __repr__(self):
        return "<Product('%s','%s','%s')>" % (str(self.outer_id), str(self.name), str(self.collect_num))   


class LogisticsCompany(Base):
    __tablename__ = 'shop_logistics_company'
    id      = Column(Integer,primary_key=True)
    code    = Column(String(64),nullable=True)
    name    = Column(String(64),nullable=True)
    reg_mail_no    = Column(String(500),nullable=True)
    is_default     = Column(Boolean,default=False)
    
    def __repr__(self):
        return "<LogisticsCompany('%s','%s','%s')>" % (str(self.id), str(self.code), str(self.name))
    
    
class Order(Base):
    __tablename__ = 'shop_orders_order'
    
    oid   = Column(BigInteger, primary_key=True)

    trade_id = Column(BigInteger, ForeignKey('shop_orders_trade.id'))
    item_id  = Column(BigInteger, ForeignKey('shop_items_item.num_iid'))

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

        
    def __repr__(self):
        return "<Order('%s','%s','%s')>" % (str(self.oid), self.seller_nick, self.buyer_nick)
        

class Trade(Base):
    __tablename__ = 'shop_orders_trade'
    
    id           =  Column(BigInteger, primary_key=True)
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

    shipping_type    =  Column(String(12),default='')
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
        return "<Trade('%s','%s','%s')>" % (str(self.id), self.seller_nick, self.buyer_nick)
    
    @property
    def total_num(self):
        total_nums = 0
        for order in self.orders:
            total_nums += order.num
        return total_nums
    
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
    

class SubPurchaseOrder(Base):
    __tablename__ = 'shop_fenxiao_subpurchaseorder'
    
    fenxiao_id = Column(String(64),primary_key=True)
    id         = Column(String(64),nullable=True)
    
    sku_id     = Column(String(64),nullable=True)
    tc_order_id    = Column(String(64),nullable=True)
    
    item_id     = Column(String(64),nullable=True)
    title       = Column(String(64),nullable=True)
    
    num        = Column(Integer,nullable=True)
    price      = Column(String(10),nullable=True)
    
    total_fee  = Column(String(10),nullable=True)
    distributor_payment  = Column(String(10),nullable=True)
    buyer_payment     = Column(String(10),nullable=True)
    
    order_200_status  = Column(String(32),nullable=True)
    auction_price     = Column(String(10),nullable=True)
    
    old_sku_properties     = Column(String(1000),nullable=True)
    
    item_outer_id     = Column(String(64),nullable=True)
    sku_outer_id     = Column(String(64),nullable=True)
    sku_properties     = Column(String(1000),nullable=True)
    
    snapshot_url     = Column(String(256),nullable=True)
    created          = Column(DateTime,nullable=True)
    
    refund_fee       = Column(String(10),nullable=True)
    status           = Column(String(32),nullable=True)
    
    def __repr__(self):
        return "<SubPurchaseOrder('%s','%s','%s')>" % (str(self.id), self.seller_nick, self.buyer_nick)
    

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
    __tablename__ = 'shop_monitor_tradeextrainfo'
    
    tid   =  Column(BigInteger, primary_key=True)
    
    is_update_amount  =  Column(Boolean,default=False)
    is_update_logistic = Column(Boolean,default=False)

    modified          =  Column(DateTime,onupdate=datetime.datetime.now(),default=datetime.datetime.now)
    seller_memo       =  Column(String(128),default='')
    
    
    def __repr__(self):
        return "<TradeExtraInfo('%s')>" % str(self.id)
    
    
class MergeTrade(Base):   
    __tablename__ = 'shop_trades_mergetrade'
    
    id           =  Column(BigInteger, primary_key=True)

    seller_id    =  Column(String(64),index=True,nullable=True)
    seller_nick  =  Column(String(64),nullable=True)
    buyer_nick   =  Column(String(64),nullable=True)
    
    type         =  Column(String(32),nullable=True)
    shipping_type    =  Column(String(12),default='')
    
    payment      =  Column(String(10),nullable=True)
    discount_fee =  Column(String(10),nullable=True)
    adjust_fee   =  Column(String(10),nullable=True)
    post_fee     =  Column(String(10),nullable=True)
    total_fee    =  Column(String(10),nullable=True)
    alipay_no    =  Column(String(128),default='')

    seller_cod_fee = Column(String(10),nullable=True)
    buyer_cod_fee  = Column(String(10),nullable=True)
    cod_fee        = Column(String(10),nullable=True)
    cod_status     = Column(String(10),nullable=True)
    
    weight    = Column(String(10),nullable=True)
    post_cost = Column(String(10),nullable=True)

    buyer_message = Column(String(1000),nullable=True)
    buyer_memo    = Column(String(1000),nullable=True)
    seller_memo   = Column(String(1000),nullable=True)

    created       =  Column(DateTime,index=True,nullable=True)
    pay_time      =  Column(DateTime,nullable=True)
    modified      =  Column(DateTime,index=True,nullable=True)
    consign_time  =  Column(DateTime,index=True,nullable=True)

    buyer_message    =  Column(String(1000),nullable=True)
    buyer_memo       =  Column(String(1000),nullable=True)
    seller_memo      =  Column(String(1000),nullable=True)

    logistics_company_name = Column(String(64),nullable=True)
    receiver_name    =  Column(String(64),default='')
    receiver_state   =  Column(String(8),default='')
    receiver_city    =  Column(String(8),default='')
    receiver_district   =  Column(String(16),default='')
    
    receiver_address =  Column(String(64),default='')
    receiver_zip     =  Column(String(10),default='')
    receiver_mobile  =  Column(String(20),default='')
    receiver_phone   =  Column(String(20),default='')

    status        =  Column(String(32),nullable=True)
    
    is_picking_print = Column(Boolean,default=False)
    is_express_print = Column(Boolean,default=False)
    is_send_print    = Column(Boolean,default=False)
        
    sys_status   =  Column(String(32),nullable=True)    
    def __repr__(self):
        return "<MergeTrade('%s','%s','%s')>" % (str(self.id), self.seller_nick, self.buyer_nick)
    
    
    
    
class Item(Base):
    __tablename__ = 'shop_items_item'
    
    num_iid   =  Column(String(64),primary_key=True)
    
    user_id   =  Column(String(32),nullable=True)
    orders         =  relationship("Order", backref="item")
    category_id    =  Column(Integer, ForeignKey('shop_categorys_category.cid'))
    
    outer_id =  Column(String(64),nullable=True)
    num       =  Column(Integer,nullable=True)
    
    seller_cids    = Column(String(126),nullable=True)
    approve_status = Column(String(20),nullable=True)
    type           = Column(String(12),nullable=True)
    valid_thru     = Column(Integer,nullable=True)
    
    price     =  Column(String(12),nullable=True)
    postage_id     = Column(BigInteger,nullable=True)
    
    has_showcase   = Column(Boolean,default=False)
    modified       = Column(String(19),nullable=True)
    
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
        return "<Item('%s','%s','%s')>" % (self.num_iid,self.outer_id,self.title)
    
    
    
    
itemrulemap_table = Table('shop_memorule_itemrulemap', Base.metadata,
    Column('item_id', Integer, ForeignKey('shop_items_item.num_iid')),
    Column('traderule_id', Integer, ForeignKey('shop_memorule_traderule.id'))
)
    
class TradeRule(Base):
    __tablename__ = 'shop_memorule_traderule'
    
    id        =  Column(Integer, primary_key=True)
    formula   =  Column(String(64),nullable=True)
    memo      =  Column(String(64),nullable=True)
    
    formula_desc  =  Column(String(256),nullable=True)
    
    scope     =  Column(String(10))
    status    =  Column(String(2))
    
    items     =  relationship("Item",secondary=itemrulemap_table,backref="rules")
    
    def __repr__(self):
        return "<TradeRule('%s','%s')>" % (self.formula_desc,self.memo)

    
    
    
class RuleFieldType(Base):
    __tablename__ =  'shop_memorule_rulefieldtype'
    
    field_name    = Column(String(64),primary_key=True)
    field_type    = Column(String(10))
    alias         = Column(String(64))
    default_value = Column(String(256),default='')
    
    products      = relationship("ProductRuleField", backref="field")
    def __repr__(self):
        return "<RuleFieldType('%s','%s')>" % (self.field_name,self.field_type)
    
    
    
class ProductRuleField(Base):
    __tablename__ = 'shop_memorule_productrulefield'
    
    id        = Column(Integer,primary_key=True)
    outer_id  = Column(String(64),index=True)
    field_id  = Column(String(64), ForeignKey('shop_memorule_rulefieldtype.field_name'))
    
    custom_alias   = Column(String(256),default=True)
    custom_default = Column(String(256),default=True)
    
    def __repr__(self):
        return "<TradeRule('%s','%s')>" % (self.outer_id,self.field_ido)

       





    
    
    
    
        