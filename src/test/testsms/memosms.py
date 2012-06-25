'''
Created on 2012-6-14

@author: user1
'''
from taobao.tasks.tasks import sendSmsToUnmemoBuyerTask

sendSmsToUnmemoBuyerTask(['0112BK1','0112BK2'],limit_times=1)