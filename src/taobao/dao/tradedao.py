'''
Created on 2012-6-4

@author: user1
'''
from taobao.dao.dbsession import get_session


def get_or_create_model(session,model_class,**kwargs):
    model = session.query(model_class).filter_by(**kwargs).first()
    if model:
        return model
    else :
        model = model_class(**kwargs)
        session.add(model)
        return model


        