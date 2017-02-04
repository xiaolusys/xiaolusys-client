'''
Created on 2012-6-2

@author: user1
'''
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from taobao.common.utils import getconfig
from taobao.common.logger import get_sentry_logger

logger = get_sentry_logger()

from taobao.common.utils import logtime


def get_session2():
    try:
        cf = getconfig()
        db_host = cf.get('db', 'db_host')
        db_port = cf.get('db', 'db_port')
        db_name = cf.get('db', 'db_name')
        db_user = cf.get('db', 'db_user')
        db_pwd = cf.get('db', 'db_pwd')
        engine = create_engine('mysql://%s:%s@%s:%s/%s?charset=utf8' % (db_user, db_pwd, db_host, db_port, db_name),
                               encoding='utf8', echo=True)

        Session = sessionmaker(bind=engine, autoflush=True, expire_on_commit=True)  #
    except Exception, exc:
        logger.error(exc.message, exc_info=True)
        raise exc
    return Session()


class SessionProvider(object):
    session = get_session2()
    __instance = None

    def __init__(self):
        pass

    def __new__(cls, *args, **kwd):
        if SessionProvider.__instance is None:
            SessionProvider.__instance = object.__new__(cls, *args, **kwd)
        return SessionProvider.__instance


@logtime(tag="get_session")
def get_session():
    return SessionProvider().session
