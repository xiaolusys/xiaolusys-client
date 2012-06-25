'''
Created on 2012-6-2

@author: user1
'''
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String

engine = create_engine('mysql://meixqhi:123123@192.168.1.133:3306/shopmgr', encoding='utf8', echo=True)

Base = declarative_base()

class User(Base):
    __tablename__ = 'test_users'
    id = Column(Integer, primary_key=True,autoincrement=True)
    name = Column(String(20))
    fullname = Column(String(20))
    password = Column(String(30))
    
    def __init__(self, name, fullname, password):
        self.name = name
        self.fullname = fullname
        self.password = password
        
    def __repr__(self):
        print self.name,self.fullname,self.passwords
        return "<User('%s','%s', 's')>" % (self.name.encode('utf8'), self.fullname, self.password)

Base.metadata.create_all(engine)