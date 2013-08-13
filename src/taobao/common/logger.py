'''
Created on 2012-6-15

@author: user1
'''
import logging

LOG_FORMAT = '%(asctime)s %(levelname)s %(message)s'
default_filename = './errors_log.txt'

def get_file_logger(logfile=default_filename):
    logger = logging.getLogger()
    hdlr   = logging.FileHandler(logfile)
    formatter = logging.Formatter(LOG_FORMAT)
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.NOTSET)
    return logger


import logging.config

def get_sentry_logger():
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': True,
    
        'formatters': {
            'console': {
                'format': '[%(asctime)s][%(levelname)s] %(name)s %(filename)s:%(funcName)s:%(lineno)d | %(message)s',
                'datefmt': '%H:%M:%S',
                },
            },
    
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'console'
                },
            'sentry': {
                'level': 'ERROR',
                'class': 'raven.handlers.logging.SentryHandler',
                'dsn': 'http://44a4775b8f36437b818b3df2b850e961:48ebbb0eb3f04334846aeed660723fc9@sentry.huyi.so/4',
                },
            },
    
        'loggers': {
            'default': {
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': False,
                },
            'taobao.erp.client': {
                'handlers': ['console', 'sentry'],
                'level': 'ERROR',
                'propagate': True,
            },
        }
    })
    logger = logging.getLogger('taobao.erp.client')
    return logger

def log_exception(fn):
    def _wrap(*args,**kwargs):
        try:
            return fn(*args,**kwargs)
        except Exception,exc:
            logger = get_sentry_logger()
            logger.error(exc.message,exc_info=True)
            raise exc
    return _wrap