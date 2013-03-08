#-*- coding:utf8 -*-
'''
Created on 2012-6-13

@author: user1
'''
from taobao.dao.dbsession import get_session
from taobao.dao.models import Product,ProductSku


session = get_session()
product = session.query(Product).filter_by(outer_id='0112BK1').first()
rows = session.query(ProductSku).filter_by(outer_id='90E',product=product)\
    .update({ProductSku.wait_post_num:ProductSku.wait_post_num-2})
print rows