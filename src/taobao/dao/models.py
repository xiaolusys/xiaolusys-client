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

class SystemConfig(Base):
    __tablename__ = 'shop_monitor_systemconfig'
    
    id = Column(Integer, primary_key=True)
    is_rule_auto = Column(Boolean, default=False)
    is_sms_auto = Column(Boolean, default=False)
    is_confirm_delivery_auto = Column(Boolean, default=False)
    
    def __repr__(self):
        return "<SystemConfig('%s')>" % (str(self.id))
    

class User(Base):
    __tablename__ = 'shop_users_user'
        
    id = Column(BigInteger, primary_key=True)
    top_session = Column(String(56), default='')
    top_appkey = Column(String(24), default='')
    top_parameters = Column(String(1000), default='')
    
    visitor_id = Column(String(32), default='')
    nick = Column(String(32), default='')
    
    type = Column(String(2), default='')
    item_img_num = Column(Integer, nullable=True)
    item_img_size = Column(Integer, nullable=True)
    
    prop_img_num = Column(Integer, nullable=True)
    prop_img_size = Column(Integer, nullable=True)
    auto_repost = Column(String(16), default='')
    promoted_type = Column(String(32), default='')
    
    alipay_bind = Column(String(10), default='')
    alipay_account = Column(String(48), default='')
    alipay_no = Column(String(20), default='')
    created_at = Column(DateTime, nullable=True)
    status = Column(String(12), default='')
    
    def __repr__(self):
        return "<User('%s','%s','%s')>" % (str(self.id), self.visitor_id, self.nick)
    
    

class Category(Base):
    __tablename__ = 'shop_categorys_category'
    
    cid = Column(Integer, primary_key=True)
    
    products = relationship("Product", backref="category")
    items = relationship("Item", backref="category")
    
    parent_cid = Column(Integer, index=True, nullable=True)
    name = Column(String(32))
    
    is_parent = Column(Boolean, default=True)
    status = Column(String(7))
    sort_order = Column(Integer, nullable=True)
    
    def __repr__(self):
        return "<Category('%s','%s','%s')>" % (str(self.cid), str(self.parent_cid), self.name)
 
 
 
class Product(Base):
    __tablename__ = 'shop_items_product'
    outer_id = Column(String(64), primary_key=True)
    name = Column(String(64), nullable=True)
    
    category_id = Column(Integer, ForeignKey('shop_categorys_category.cid'))
    
    collect_num = Column(Integer, nullable=True)
    price = Column(String(10), nullable=True)
    
    created = Column(DateTime, index=True, nullable=True)
    modified = Column(DateTime, index=True, nullable=True)
    
    def __repr__(self):
        return "<Product('%s','%s','%s')>" % (str(self.outer_id), str(self.name), str(self.collect_num))   

class FenxiaoProduct(Base):
    __tablename__ = 'shop_fenxiao_product'
    pid            = Column(String(64), primary_key=True)
    name           = Column(String(64), default='')
    productcat_id  = Column(String(64), default='')
    
    user_id        = Column(BigInteger, nullable=True)
    trade_type     = Column(String(7), default='')
    standard_price = Column(String(10), default='')
    
    item_id        = Column(String(10), default='')
    cost_price     = Column(String(10), default='')
    outer_id       = Column(String(64), default='')
    
    pictures       = Column(String(1000), default='')          
    status         = Column(String(10), default='')
    
    def __repr__(self):
        return "<FenxiaoProduct('%s','%s','%s')>" % (str(self.pid), str(self.item_id), str(self.outer_id))

class LogisticsCompany(Base):
    __tablename__ = 'shop_logistics_company'
    id = Column(Integer, primary_key=True)
    code = Column(String(64), nullable=True)
    name = Column(String(64), nullable=True)
    reg_mail_no = Column(String(500), nullable=True)
    priority = Column(Integer, default=0)
    
    def __repr__(self):
        return "<LogisticsCompany('%s','%s','%s')>" % (str(self.id), str(self.code), str(self.name))
    
    
class Order(Base):
    __tablename__ = 'shop_orders_order'
    
    oid = Column(BigInteger, primary_key=True)

    trade_id = Column(BigInteger, ForeignKey('shop_orders_trade.id'))
    item_id = Column(BigInteger, ForeignKey('shop_items_item.num_iid'))

    title = Column(String(128), nullable=True)
    price = Column(String(12), nullable=True)
    num_iid = Column(BigInteger, nullable=True)

    item_meal_id = Column(BigInteger, nullable=True)
    sku_id = Column(String(20), nullable=True)
    num = Column(Integer, nullable=True)

    outer_sku_id = Column(String(20), nullable=True)
    total_fee = Column(String(12), nullable=True)

    payment = Column(String(12), nullable=True)
    discount_fee = Column(String(12), nullable=True)
    adjust_fee = Column(String(12), nullable=True)

    modified = Column(String(19), nullable=True)
    sku_properties_name = Column(String(88), nullable=True)
    refund_id = Column(BigInteger, nullable=True)

    is_oversold = Column(Boolean)
    is_service_order = Column(Boolean)

    item_meal_name = Column(String(88), nullable=True)
    pic_path = Column(String(128), nullable=True)

    seller_nick = Column(String(32), nullable=True, index=True)
    buyer_nick = Column(String(32), nullable=True, index=True)
    
    refund_status = Column(String(40), nullable=True)
    outer_id = Column(String(64), nullable=True)

    cid = Column(BigInteger, nullable=True)
    status = Column(String(32), nullable=True)

        
    def __repr__(self):
        return "<Order('%s','%s','%s')>" % (str(self.oid), self.seller_nick, self.buyer_nick)
        

class Trade(Base):
    __tablename__ = 'shop_orders_trade'
    
    id = Column(BigInteger, primary_key=True)
    orders = relationship("Order", backref="trade")

    seller_id = Column(String(64), index=True, nullable=True)
    seller_nick = Column(String(64), nullable=True)
    buyer_nick = Column(String(64), nullable=True)
    type = Column(String(32), nullable=True)

    payment = Column(String(10), nullable=True)
    discount_fee = Column(String(10), nullable=True)
    adjust_fee = Column(String(10), nullable=True)
    post_fee = Column(String(10), nullable=True)
    total_fee = Column(String(10), nullable=True)

    buyer_obtain_point_fee = Column(String(10), nullable=True)
    point_fee = Column(String(10), nullable=True)
    real_point_fee = Column(String(10), nullable=True)
    commission_fee = Column(String(10), nullable=True)

    created = Column(DateTime, index=True, nullable=True)
    pay_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, index=True, nullable=True)
    modified = Column(DateTime, index=True, nullable=True)
    consign_time = Column(DateTime, index=True, nullable=True)

    buyer_message = Column(String(1000), nullable=True)
    seller_memo = Column(String(1000), nullable=True)

    shipping_type = Column(String(12), default='')
    buyer_alipay_no = Column(String(128), default='')
    receiver_name = Column(String(64), default='')
    receiver_state = Column(String(8), default='')
    receiver_city = Column(String(8), default='')
    receiver_district = Column(String(16), default='')
    
    receiver_address = Column(String(64), default='')
    receiver_zip = Column(String(10), default='')
    receiver_mobile = Column(String(20), default='')
    receiver_phone = Column(String(20), default='')

    status = Column(String(32), nullable=True)
        
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
    
    fenxiao_id = Column(String(64), primary_key=True)
    id = Column(String(64), nullable=True)
    
    sku_id = Column(String(64), nullable=True)
    tc_order_id = Column(String(64), nullable=True)
    
    item_id = Column(String(64), nullable=True)
    title = Column(String(64), nullable=True)
    
    num = Column(Integer, nullable=True)
    price = Column(String(10), nullable=True)
    
    total_fee = Column(String(10), nullable=True)
    distributor_payment = Column(String(10), nullable=True)
    buyer_payment = Column(String(10), nullable=True)
    
    order_200_status = Column(String(32), nullable=True)
    auction_price = Column(String(10), nullable=True)
    
    old_sku_properties = Column(String(1000), nullable=True)
    
    item_outer_id = Column(String(64), nullable=True)
    sku_outer_id = Column(String(64), nullable=True)
    sku_properties = Column(String(1000), nullable=True)
    
    snapshot_url = Column(String(256), nullable=True)
    created = Column(DateTime, nullable=True)
    
    refund_fee = Column(String(10), nullable=True)
    status = Column(String(32), nullable=True)
    
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
    
    tid = Column(BigInteger, primary_key=True)
    
    is_update_amount = Column(Boolean, default=False)
    is_update_logistic = Column(Boolean, default=False)

    modified = Column(DateTime, onupdate=datetime.datetime.now(), default=datetime.datetime.now)
    seller_memo = Column(String(128), default='')
    
    
    def __repr__(self):
        return "<TradeExtraInfo('%s')>" % str(self.id)
    
    
class MergeTrade(Base):   
    __tablename__ = 'shop_trades_mergetrade'
    
    tid = Column(BigInteger, primary_key=True)

    seller_id = Column(String(64), index=True, nullable=True)
    seller_nick = Column(String(64), nullable=True)
    buyer_nick = Column(String(64), nullable=True)
    
    type = Column(String(32), nullable=True)
    shipping_type = Column(String(12), default='')
    
    total_num = Column(Integer, nullable=True)
    payment = Column(String(10), nullable=True)
    discount_fee = Column(String(10), nullable=True)
    adjust_fee = Column(String(10), nullable=True)
    post_fee = Column(String(10), nullable=True)
    total_fee = Column(String(10), nullable=True)
    alipay_no = Column(String(128), default='')

    seller_cod_fee = Column(String(10), nullable=True)
    buyer_cod_fee = Column(String(10), nullable=True)
    cod_fee = Column(String(10), nullable=True)
    cod_status = Column(String(10), nullable=True)
    
    weight = Column(String(10), nullable=True)
    post_cost = Column(String(10), nullable=True)

    buyer_message = Column(String(1000), nullable=True)
    seller_memo = Column(String(1000), nullable=True)

    created = Column(DateTime, index=True, nullable=True)
    pay_time = Column(DateTime,index=True, nullable=True)
    modified = Column(DateTime, index=True, nullable=True)
    consign_time = Column(DateTime, index=True, nullable=True)

    buyer_message = Column(String(1000), default='')
    seller_memo = Column(String(1000), default='')
    sys_memo = Column(String(1000), default='')
    
    out_sid = Column(String(64),index=True,default='')
    logistics_company_code = Column(String(64), default='')
    logistics_company_name = Column(String(64), default='')
    receiver_name = Column(String(64), default='')
    receiver_state = Column(String(8), default='')
    receiver_city = Column(String(8), default='')
    receiver_district = Column(String(16), default='')
    
    receiver_address = Column(String(64), default='')
    receiver_zip = Column(String(10), default='')
    receiver_mobile = Column(String(20), default='')
    receiver_phone = Column(String(20), default='')

    reverse_audit_times = Column(Integer, nullable=True)
    reverse_audit_reason = Column(String(1000), default='')
    status = Column(String(32), index=True, nullable=True)
    
    is_picking_print = Column(Boolean, default=False)
    is_express_print = Column(Boolean, default=False)
    is_send_sms = Column(Boolean, default=False)
    has_refund = Column(Boolean, default=False)
        
    sys_status = Column(String(32),index=True,default='')    
    def __repr__(self):
        return "<MergeTrade('%s','%s','%s')>" % (str(self.tid), self.seller_nick, self.buyer_nick)
  

class MergeBuyerTrade(Base):
    __tablename__ = 'shop_trades_mergebuyertrade'
    tid   = Column(BigInteger,primary_key=True)
    main_tid = Column(BigInteger)
    
    def __repr__(self):
        return "<MergeTrade('%s','%s','%s')>" % (str(self.tid), self.seller_nick, self.buyer_nick)
  
class Refund(Base):
    __tablename__ = 'shop_refunds_refund'
    
    refund_id = Column(BigInteger, primary_key=True)
    tid = Column(BigInteger, nullable=True)
    
    title = Column(String(64), default='')
    num_iid = Column(BigInteger, nullable=True)
    
    seller_id = Column(String(64), default='')
    buyer_nick = Column(String(64), default='')
    seller_nick = Column(String(64), default='')
    
    total_fee = Column(String(64), default='')
    refund_fee = Column(String(64), default='')
    payment = Column(String(64), default='')
    
    created = Column(DateTime, nullable=True)
    modified = Column(DateTime, nullable=True)
    
    oid = Column(String(64), index=True, default='')
    company_name = Column(String(64), default='')
    sid = Column(String(64), default='')
    
    reason = Column(String(200), default='')
    desc = Column(String(1000), default='')
    has_good_return = Column(Boolean, default=False)
    
    good_status = Column(String(32), default='')
    order_status = Column(String(32), default='')
    status = Column(String(32), default='')
    
    def __repr__(self):
        return "<Refund('%s','%s','%s')>" % (str(self.refund_id), str(self.tid), str(self.oid))
    
    
class Item(Base):
    __tablename__ = 'shop_items_item'
    
    num_iid = Column(String(64), primary_key=True)
    
    user_id = Column(String(32), nullable=True)
    orders = relationship("Order", backref="item")
    category_id = Column(Integer, ForeignKey('shop_categorys_category.cid'))
    
    outer_id = Column(String(64), nullable=True)
    num = Column(Integer, nullable=True)
    
    seller_cids = Column(String(126), nullable=True)
    approve_status = Column(String(20), nullable=True)
    type = Column(String(12), nullable=True)
    valid_thru = Column(Integer, nullable=True)
    
    price = Column(String(12), nullable=True)
    postage_id = Column(BigInteger, nullable=True)
    
    has_showcase = Column(Boolean, default=False)
    modified = Column(String(19), nullable=True)
    
    list_time = Column(DateTime, nullable=True)
    delist_time = Column(DateTime, nullable=True)
    has_discount = Column(Boolean, default=False)
    
    props = Column(String(200), nullable=True)
    title = Column(String(148), nullable=True)
    
    has_invoice = Column(Boolean, default=False)
    pic_url = Column(String(256), nullable=True)
    detail_url = Column(String(256), nullable=True)
    
    desc = Column(String(64), nullable=True)
    skus = Column(String(1500), nullable=True)
    
    def __repr__(self):
        return "<Item('%s','%s','%s')>" % (self.num_iid, self.outer_id, self.title)
     
    
    
itemrulemap_table = Table('shop_memorule_itemrulemap', Base.metadata,
    Column('item_id', Integer, ForeignKey('shop_items_item.num_iid')),
    Column('traderule_id', Integer, ForeignKey('shop_memorule_traderule.id'))
)
    
class TradeRule(Base):
    __tablename__ = 'shop_memorule_traderule'
    
    id = Column(Integer, primary_key=True)
    formula = Column(String(64), nullable=True)
    memo = Column(String(64), nullable=True)
    
    formula_desc = Column(String(256), nullable=True)
    
    scope = Column(String(10))
    status = Column(String(2))
    
    items = relationship("Item", secondary=itemrulemap_table, backref="rules")
    
    def __repr__(self):
        return "<TradeRule('%s','%s')>" % (self.formula_desc, self.memo)

    
    
    
class RuleFieldType(Base):
    __tablename__ = 'shop_memorule_rulefieldtype'
    
    field_name = Column(String(64), primary_key=True)
    field_type = Column(String(10))
    alias = Column(String(64))
    default_value = Column(String(256), default='')
    
    products = relationship("ProductRuleField", backref="field")
    def __repr__(self):
        return "<RuleFieldType('%s','%s')>" % (self.field_name, self.field_type)
    
    
    
class ProductRuleField(Base):
    __tablename__ = 'shop_memorule_productrulefield'
    
    id = Column(Integer, primary_key=True)
    outer_id = Column(String(64), index=True)
    field_id = Column(String(64), ForeignKey('shop_memorule_rulefieldtype.field_name'))
    
    custom_alias = Column(String(256), default=True)
    custom_default = Column(String(256), default=True)
    
    def __repr__(self):
        return "<TradeRule('%s','%s')>" % (self.outer_id, self.field_ido)

       





    
    
    
    
        
