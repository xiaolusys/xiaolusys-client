#coding=utf-8
'''
Created on 2012-6-2

@author: user1
'''
import re
import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, BigInteger,Float , String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship, backref
from . import configparams as cfg 

Base = declarative_base()
#memo_compile = re.compile('^\((?P<key>\w+),(?P<value>[\w\W]+),(?P<memo>[\w\W]+)\)$')

class SystemConfig(Base):
    __tablename__ = 'shop_monitor_systemconfig'
    
    id = Column(Integer, primary_key=True)
    is_rule_auto = Column(Boolean, default=False)
    is_sms_auto = Column(Boolean, default=False)
    
    normal_print_limit = Column(Boolean, default=False)
    per_request_num = Column(Integer)
    client_num = Column(Integer)
    
    def __repr__(self):
        return "<SystemConfig('%s')>" % (str(self.id))
    

    
class User(Base):
    __tablename__ = 'shop_users_user'
        
    id = Column(BigInteger, primary_key=True)
    top_session = Column(String(56), default='')
    top_appkey = Column(String(24), default='')
    top_parameters = Column(String(1000), default='')
    
    visitor_id = Column(String(32), default='')
    nick       = Column(String(32), default='')
    user_code  = Column(String(16), default='')
    
    merge_trades = relationship("MergeTrade", backref="user")
    contacter = Column(String(32), default='')
    phone     = Column(String(20), default='')
    mobile    = Column(String(20), default='')
    area_code = Column(String(10), default='')
    location  = Column(String(256), default='')
    
    type = Column(String(2), default='')
    
    auto_repost = Column(String(16), default='')
    
    alipay_bind = Column(String(10), default='')
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
    
    id       = Column(Integer,primary_key=True)
    outer_id = Column(String(64))
    name     = Column(String(64))
    barcode  = Column(String(64))
    category_id =  Column(Integer, ForeignKey('shop_categorys_category.cid'))
    
    skus = relationship("ProductSku",backref='product')
    
    pic_path    = Column(String(256))
    collect_num = Column(Integer)
    warn_num    = Column(Integer)
    remain_num  = Column(Integer)
    wait_post_num  = Column(Integer)
    std_sale_price = Column(Float)
    
    created = Column(DateTime)
    modified = Column(DateTime)
    
    sync_stock  = Column(Boolean)
    is_assign  = Column(Boolean)
    
    post_check = Column(Boolean)
    
    buyer_prompt = Column(String(40))
    status     = Column(String(16))
    def __repr__(self):
        return "<Product('%s','%s','%s')>" % (str(self.outer_id), str(self.name), str(self.collect_num))   
    
    @property
    def BARCODE(self):
        return self.barcode.strip() or self.outer_id.strip()

class ProductSku(Base):
    __tablename__ = 'shop_items_productsku'
    
    id  = Column(Integer,primary_key=True)
    outer_id = Column(String(64))
    barcode  = Column(String(64))
    product_id = Column(Integer, ForeignKey('shop_items_product.id'))
    
    quantity    = Column(Integer)
    warn_num    = Column(Integer)
    remain_num  = Column(Integer)
    wait_post_num  = Column(Integer)
    std_sale_price = Column(Float)
    
    properties_name  = Column(String(200))
    properties_alias = Column(String(200))
    
    modified = Column(DateTime)
    
    sync_stock  = Column(Boolean)
    is_assign  = Column(Boolean)
    
    post_check = Column(Boolean)
    
    buyer_prompt = Column(String(40))
    status     = Column(String(10))
    def __repr__(self):
        return "<Product('%s','%s')>" % (str(self.outer_id), str(self.properties_name)) 

    @property
    def name(self):
        return self.properties_alias or self.properties_name
    
    @property
    def BARCODE(self):
        return self.barcode.strip() or self.product.barcode.strip() or '%s%s'%(self.product.outer_id.strip(),self.outer_id.strip())

class LogisticsCompany(Base):
    __tablename__ = 'shop_logistics_company'
    
    id = Column(Integer, primary_key=True)
    code = Column(String(64), nullable=True)
    name = Column(String(64), nullable=True)
    reg_mail_no = Column(String(500), nullable=True)
    priority = Column(Integer, default=0)
    
    district = Column(String(1000))
    status   = Column(Boolean)
    
    merge_trades = relationship("MergeTrade",backref='logistics_company')
    def __repr__(self):
        return "<LogisticsCompany('%s','%s','%s')>" % (str(self.id), str(self.code), str(self.name))
    
    
class MergeOrder(Base):
    __tablename__ = 'shop_trades_mergeorder'
    
    id = Column(BigInteger, primary_key=True)
    oid = Column(String(32),index=True)
    
    cid = Column(BigInteger,index=True)
    merge_trade_id = Column(BigInteger, ForeignKey('shop_trades_mergetrade.id'))

    title = Column(String(128), nullable=True)
    price = Column(Float)
    num_iid = Column(BigInteger, nullable=True)

    sku_id = Column(String(20), nullable=True)
    num = Column(Integer, nullable=True)
    
    outer_id = Column(String(64), nullable=True)
    outer_sku_id = Column(String(20), nullable=True)
    total_fee = Column(Float)

    payment = Column(Float)
    discount_fee = Column(Float)
    adjust_fee = Column(Float)

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
        return "<Order('%s','%s','%s')>" % (str(self.id), self.seller_nick, self.buyer_nick)
        

class MergeTrade(Base):
    __tablename__ = 'shop_trades_mergetrade'
    
    id = Column(BigInteger, primary_key=True)
    tid = Column(String(32), index=True)
    merge_orders = relationship("MergeOrder", backref="merge_trade")
    user_id = Column(Integer, ForeignKey('shop_users_user.id'))

#    seller_id = Column(String(64), index=True, nullable=True)
#    seller_nick = Column(String(64), nullable=True)
    buyer_nick = Column(String(64), nullable=True)
    type = Column(String(32), nullable=True)
    shipping_type = Column(String(12), default='')
    trade_from    = Column(Integer)
    
    prod_num   = Column(Integer)
    refund_num = Column(Integer)
    payment = Column(Float)
    discount_fee = Column(Float)
    adjust_fee = Column(Float)
    post_fee = Column(Float)
    total_fee = Column(Float)
    
    seller_cod_fee = Column(Float)
    buyer_cod_fee  = Column(Float)
    cod_fee        = Column(Float)
    cod_status     = Column(Float)

    created = Column(DateTime, index=True, nullable=True)
    pay_time = Column(DateTime, nullable=True)
    modified = Column(DateTime, index=True, nullable=True)
    consign_time = Column(DateTime, index=True, nullable=True)
    weight_time  = Column(DateTime, index=True, nullable=True)
    charge_time  = Column(DateTime, index=True, nullable=True)
    
    buyer_message = Column(String(1000))
    seller_memo   = Column(String(1000))
    sys_memo      = Column(String(500))
    
    out_sid       = Column(String(64),index=True)
    weight        = Column(String(10))
    post_cost     = Column(Float)
    logistics_company_id = Column(Integer,ForeignKey('shop_logistics_company.id'))
    receiver_name = Column(String(64), default='')
    receiver_state = Column(String(8), default='')
    receiver_city = Column(String(8), default='')
    receiver_district = Column(String(16), default='')
    
    receiver_address = Column(String(64), default='')
    receiver_zip = Column(String(10), default='')
    receiver_mobile = Column(String(24), default='')
    receiver_phone = Column(String(24), default='')
    
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
    is_locked        = Column(Boolean)
    is_charged       = Column(Boolean)
    has_merge        = Column(Boolean)
    sys_status       = Column(String(32),index=True)  
    
    is_qrcode        = Column(Boolean)
    qrcode_msg       = Column(String(32))
    
    reserveo       =  Column(String(32))       
    reservet       =  Column(String(32)) 
    reserveh       =  Column(String(32))
    
    def __repr__(self):
        return "<Trade('%s','%s')>" % (str(self.id), self.buyer_nick)
    
    @property
    def total_num(self):
        total_nums = 0
        for order in self.merge_orders:
            total_nums += order.num
        return total_nums
    
    def isPrepareSend(self):
        return self.sys_status == cfg.SYS_STATUS_PREPARESEND
            
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

    modified = Column(DateTime,nullable=True)
    
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
     
    
class DepositeDistrict(Base):
    
    __tablename__ = 'shop_archives_depositedistrict'
    
    id = Column(Integer, primary_key=True)
    
    product_location = relationship("ProductLocation", backref="district")
    
    district_no = Column(String(32), nullable=True)
    parent_no   = Column(String(32), nullable=True)
    
    location    = Column(String(64), nullable=True)
    in_use     = Column(Boolean)
    
    extra_info  = Column(String(1000))
    
    def __repr__(self):
        return "<DepositeDistrict('%d','%s','%s')>" % (self.id, self.parent_no, self.district_no)
    
    @property
    def pos_code(self):
        return '%s-%s'%(self.parent_no,self.district_no)


class ProductLocation(Base):
    
    __tablename__ = 'shop_items_productlocation'
    
    id        = Column(Integer, primary_key=True)

    product_id  = Column(Integer)
    sku_id      = Column(Integer)
    
    outer_id  = Column(String(32))
    name      = Column(String(64))
    
    outer_sku_id     = Column(String(32))
    properties_name  = Column(String(64))
        
    district_id = Column(Integer, ForeignKey('shop_archives_depositedistrict.id'))
    
    def __repr__(self):
        return "<ProductLocation('%s','%s','%s')>" % (self.outer_id, self.outer_sku_id, self.district.pos_code)


class BranchZone(Base):
    
    __tablename__ = 'shop_yunda_branch'
    
    id        = Column(Integer, primary_key=True)
    classify_zone = relationship("ClassifyZone", backref="branch")
    code      = Column(String(32),index=True)
    name      = Column(String(64),index=True)
    barcode   = Column(String(32),index=True)
   
    def __repr__(self):
        return "<BranchZone('%s','%s','%s')>" % (self.code, self.name, self.barcode)
    
    @property
    def COMBO_CODE(self):
        return '%s %s'%(self.name,self.code)

class ClassifyZone(Base):
    
    __tablename__ = 'shop_yunda_zone'
    
    id        = Column(Integer, primary_key=True)
    
    state     = Column(String(32),index=True)
    city      = Column(String(64),index=True)
    district  = Column(String(32),index=True)
    
    branch_id = Column(Integer, ForeignKey('shop_yunda_branch.id'))
    zone      = Column(String(64))
    
    def __repr__(self):
        return "<ClassifyZone('%s','%s','%s')>" % (self.state, self.city, self.district)
    

class YundaCustomer(Base):
    
    __tablename__ = 'shop_yunda_customer'
    
    id      = Column(Integer,primary_key=True)
    name    = Column(String(64)) 
    code    = Column(String(16)) 
    
    company_name = Column(String(32)) 
    company_trade = Column(String(32)) 
    cus_id       = Column(String(32)) 
    
    qr_id       = Column(String(32)) 
    qr_code     = Column(String(32)) 
    
    contacter   = Column(String(32))
    state       = Column(String(16))
    city        = Column(String(16))
    district    = Column(String(16))
    
    address     = Column(String(128))
    zip         = Column(String(10))
    mobile      = Column(String(20))
    phone       = Column(String(20))
    
    on_qrcode   = Column(Boolean)
    memo        = Column(String(20)) 
    reserveo    = Column(String(64))
    reservet    = Column(String(64))
    
    status  = Column(String(10),index=True) 
    
    def __repr__(self):
        return "<YundaCustomer('%s','%s')>" %(self.code,self.name)
    
