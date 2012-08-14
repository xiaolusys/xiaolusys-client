'''
Created on 2012-6-14

@author: user1
'''
from taobao.dao.models import MergeTrade
from taobao.dao.dbsession import get_session

session =  get_session()
trade = session.query(MergeTrade).filter_by(out_sid=425235235)
print 'trade',trade,trade.count()