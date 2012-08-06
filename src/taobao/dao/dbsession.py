'''
Created on 2012-6-2

@author: user1
'''
import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import ConfigParser
import taobao


def get_session():
    cf = ConfigParser.ConfigParser()
    config_path = os.path.abspath(os.path.dirname(taobao.__file__))
    
    cf.read(config_path+'/system.conf')
 
    db_host = cf.get('db','db_host')
    db_port = cf.get('db','db_port')
    db_name = cf.get('db','db_name')
    db_user = cf.get('db','db_user')
    db_pwd  = cf.get('db','db_pwd')
    engine = create_engine('mysql://%s:%s@%s:%s/%s?charset=utf8'%(db_user,db_pwd,db_host,db_port,db_name), encoding='utf8', echo=False)

    Session = sessionmaker(bind=engine)
    session = Session()
    return session

print 