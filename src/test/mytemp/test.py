'''
Created on 2012-6-4

@author: user1
'''
from jinja2 import Template,Environment,PackageLoader 
from taobao.dao.models import Trade
from taobao.dao.dbsession import get_session
from taobao.common.filters import datetimeformat

#content = open('trade_picking_template.html','r').read()
#template = Template(content.decode('utf8'))

env = Environment(loader=PackageLoader('taobao.templates',package_path='../../taobao/templates'))

env.filters['datetimeformat'] = datetimeformat

template = env.get_template('trade_picking_template.html')
session = get_session()
trades = session.query(Trade).filter_by(status='WAIT_SELLER_SEND_GOODS')

print 'nick:',trades[0].seller_nick
print 'sku name:',trades[0].orders[0].sku_properties_name
print 'meal name:',trades[0].orders[0].item_meal_name

#tempdate = template.render(trades=trades)

#print tempdate



