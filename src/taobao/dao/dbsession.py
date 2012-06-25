'''
Created on 2012-6-2

@author: user1
'''
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

default_engine = create_engine('mysql://meixqhi:123123@192.168.1.133:3306/shopmgr?charset=utf8', encoding='utf8', echo=False)

def get_session(engine=default_engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    return session