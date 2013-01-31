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
    
    merge_trades = relationship("MergeTrade", backref="user")
    contacter = Column(String(32), default='')
    phone     = Column(String(20), default='')
    mobile    = Column(String(20), default='')
    area_code = Column(String(10), default='')
    location  = Column(String(256), default='')
    
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
    
    id  = Column(Integer,primary_key=True)
    outer_id = Column(String(64))
    name = Column(String(64))
    category_id =  Column(Integer, ForeignKey('shop_categorys_category.cid'))
    
    skus = relationship("ProductSku", backref="product")
    
    pic_path    = Column(String(256))
    collect_num = Column(Integer)
    warn_num    = Column(Integer)
    remain_num  = Column(Integer)
    price = Column(String(10))
    
    created = Column(DateTime)
    modified = Column(DateTime)
    
    sync_stock  = Column(Boolean)
    out_stock  = Column(Boolean)
    is_assign  = Column(Boolean)
    
    status     = Column(String(16))
    def __repr__(self):
        return "<Product('%s','%s','%s')>" % (str(self.outer_id), str(self.name), str(self.collect_num))   


class ProductSku(Base):
    __tablename__ = 'shop_items_productsku'
    
    id  = Column(Integer,primary_key=True)
    outer_id = Column(String(64))
    prod_outer_id = Column(String(64))
    product_id = Column(Integer, ForeignKey('shop_items_product.id'))
    
    quantity    = Column(Integer)
    warn_num    = Column(Integer)
    remain_num  = Column(Integer)
    
    properties_name  = Column(String(200))
    properties       = Column(String(200))
    
    modified = Column(DateTime)
    
    sync_stock  = Column(Boolean)
    out_stock  = Column(Boolean)
    is_assign  = Column(Boolean)
    
    status     = Column(String(10))
    def __repr__(self):
        return "<Product('%s','%s')>" % (str(self.outer_id), str(self.properties_name)) 


class LogisticsCompany(Base):
    __tablename__ = 'shop_logistics_company'
    
    id = Column(Integer, primary_key=True)
    code = Column(String(64), nullable=True)
    name = Column(String(64), nullable=True)
    reg_mail_no = Column(String(500), nullable=True)
    priority = Column(Integer, default=0)
    
    district = Column(String(1000))
    status   = Column(Boolean)
    
    merge_trades = relationship("MergeTrade", backref="logistics_company")
    def __repr__(self):
        return "<LogisticsCompany('%s','%s','%s')>" % (str(self.id), str(self.code), str(self.name))
    
    
class MergeOrder(Base):
    __tablename__ = 'shop_trades_mergeorder'
    
    id = Column(BigInteger, primary_key=True)
    oid = Column(BigInteger,index=True)
    tid = Column(BigInteger,index=True)
    
    cid = Column(BigInteger,index=True)
    merge_trade_id = Column(BigInteger, ForeignKey('shop_trades_mergetrade.id'))

    title = Column(String(128), nullable=True)
    price = Column(String(12), nullable=True)
    num_iid = Column(BigInteger, nullable=True)

    sku_id = Column(String(20), nullable=True)
    num = Column(Integer, nullable=True)
    
    outer_id = Column(String(64), nullable=True)
    outer_sku_id = Column(String(20), nullable=True)
    total_fee = Column(String(12), nullable=True)

    payment = Column(String(12), nullable=True)
    discount_fee = Column(String(12), nullable=True)
    adjust_fee = Column(String(12), nullable=True)

    sku_properties_name = Column(String(256), nullable=True)
    
    refund_id = Column(BigInteger, nullable=True)
    refund_status = Column(String(40))

    gift_type = Column(Integer, nullable=True)
    pic_path  = Column(String(128), nullable=True)

    seller_nick = Column(String(32), nullable=True, index=True)
    buyer_nick = Column(String(32), nullable=True, index=True)
    
    created = Column(DateTime)
    consign_time = Column(DateTime)
    
    status = Column(String(32), nullable=True)
    sys_status = Column(String(32), nullable=True)
        
    def __repr__(self):
        return "<Order('%s','%s','%s')>" % (str(self.oid), self.seller_nick, self.buyer_nick)
        

class MergeTrade(Base):
    __tablename__ = 'shop_trades_mergetrade'
    
    id = Column(BigInteger, primary_key=True)
    tid = Column(BigInteger, primary_key=True)
    merge_orders = relationship("MergeOrder", backref="merge_trade")
    user_id = Column(Integer, ForeignKey('shop_users_user.id'))

    seller_id = Column(String(64), index=True, nullable=True)
    seller_nick = Column(String(64), nullable=True)
    buyer_nick = Column(String(64), nullable=True)
    type = Column(String(32), nullable=True)
    shipping_type = Column(String(12), default='')
    
    total_num = Column(Integer)
    payment = Column(String(10), nullable=True)
    discount_fee = Column(String(10), nullable=True)
    adjust_fee = Column(String(10), nullable=True)
    post_fee = Column(String(10), nullable=True)
    total_fee = Column(String(10), nullable=True)
    alipay_no = Column(String(128), default='')
    
    seller_cod_fee = Column(String(10), nullable=True)
    buyer_cod_fee  = Column(String(10), nullable=True)
    cod_fee        = Column(String(10), nullable=True)
    cod_status     = Column(String(10), nullable=True)

    created = Column(DateTime, index=True, nullable=True)
    pay_time = Column(DateTime, nullable=True)
    modified = Column(DateTime, index=True, nullable=True)
    consign_time = Column(DateTime, index=True, nullable=True)

    buyer_message = Column(String(1000))
    seller_memo   = Column(String(1000))
    sys_memo      = Column(String(500))
    
    out_sid       = Column(String(64),index=True)
    weight        = Column(String(10))
    post_cost     = Column(String(10))
    logistics_company_id = Column(Integer,ForeignKey('shop_logistics_company.id'))
    receiver_name = Column(String(64), default='')
    receiver_state = Column(String(8), default='')
    receiver_city = Column(String(8), default='')
    receiver_district = Column(String(16), default='')
    
    receiver_address = Column(String(64), default='')
    receiver_zip = Column(String(10), default='')
    receiver_mobile = Column(String(20), default='')
    receiver_phone = Column(String(20), default='')
    
    reason_code = Column(String(100), nullable=True)
    status      = Column(String(32) ,index=True ,nullable=True)
        
    is_picking_print = Column(Boolean)
    is_express_print = Column(Boolean)
    is_send_sms      = Column(Boolean)
    has_refund       = Column(Boolean)
    has_memo         = Column(Boolean)
    remind_time      = Column(DateTime)
    
    can_review       = Column(Boolean)
    priority         = Column(Integer,index=True)
    operator         = Column(String(32))
    sys_status       = Column(String(32),index=True)  
    def __repr__(self):
        return "<Trade('%s','%s','%s','%s')>" % (str(self.id),str(self.tid), self.seller_nick, self.buyer_nick)
    
    @property
    def total_num(self):
        total_nums = 0
        for order in self.merge_orders:
            total_nums += order.num
        return total_nums
     

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
    
    def __repr__(self):
        return "<TradeExtraInfo('%s')>" % str(self.id)
    
    
class Item(Base):
    __tablename__ = 'shop_items_item'
    
    num_iid = Column(String(64), primary_key=True)
    
    user_id = Column(String(32), nullable=True)
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
     
    

       





    
    
    
    
        
