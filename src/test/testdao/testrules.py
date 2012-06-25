'''
Created on 2012-6-13

@author: user1
'''
from taobao.dao.dbsession import get_session
from taobao.dao.models import TradeRule,Item,TradeExtraInfo,ProductRuleField


session = get_session()
#traderules = session.query(TradeRule).all()
#print traderules
#print traderules[0].items
#
#item = traderules[0].items[0]
#print item.rules

result = session.query(ProductRuleField.out_iid).distinct('shop_app_productrulefield_out_iid').all()
print 'result:',result