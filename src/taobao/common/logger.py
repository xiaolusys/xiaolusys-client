'''
Created on 2012-6-15

@author: user1
'''
import logging

LOG_FORMAT = '%(asctime)s %(levelname)s %(message)s'
default_filename = './errors_log.txt'

def get_logger(logfile=default_filename):
    logger = logging.getLogger()
    hdlr   = logging.FileHandler(logfile)
    formatter = logging.Formatter(LOG_FORMAT)
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.NOTSET)
    return logger
