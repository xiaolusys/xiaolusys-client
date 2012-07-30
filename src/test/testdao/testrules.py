#-*- coding:utf8 -*-
'''
Created on 2012-6-13

@author: user1
'''
from taobao.dao.dbsession import get_session
from taobao.dao.models import TradeRule,Item,TradeExtraInfo,ProductRuleField,Trade


session = get_session()
#traderules = session.query(TradeRule).all()
#print traderules
#print traderules[0].items
#
#item = traderules[0].items[0]
#print item.rules

#result = session.query(ProductRuleField.outer_id).distinct('shop_app_productrulefield_out_iid').all()
#print 'result:',result
result2 = session.query(Trade).filter(Trade.buyer_nick.like('%a%'.decode('utf8')))
result3 = result2
result3 = result3.filter("seller_nick like :nick").params(nick='%优尼小小%'.decode('utf8'))

print result2.first(),result3.first()
print result2 == result3

result4 = result2.filter(Trade.type.like('fixed'))
print result4.first()