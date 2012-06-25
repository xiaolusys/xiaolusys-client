'''
Created on 2012-6-2

@author: user1
'''
from taobao.dao.dbsession import get_session
from taobao.dao.models import Trade, Order


session = get_session()
#trade = session.query(Trade).filter_by(status='TRADE_FINISHED').first()
#trade = session.query(Trade).filter_by(status='TRADE_FINISHED').one()
trade = session.query(Trade).get(173863640941048)

print trade
print trade.orders