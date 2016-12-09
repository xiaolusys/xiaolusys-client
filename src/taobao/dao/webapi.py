# -*- encoding:utf8 -*-
import json
import urllib
import urllib2
from taobao.common.utils import getconfig
from taobao.common.logger import *

log = get_file_logger()


class WebApi(object):
    conf = getconfig()
    web_host = conf.get('url', 'web_host')

    @staticmethod
    def operate_packages(package_order_ids, operator_id):
        uri = '/warehouse/operate/'
        params = {'package_order_ids': ','.join([str(p) for p in package_order_ids]),
                  'operator': operator_id}
        try:
            url = getFullWebUrl(uri, params)
            req = urllib.urlopen(url)
            r = req.read()
            resp = json.loads(r)
            sign = resp['isSuccess']
        except Exception, e:
            logging.error(r)
            raise Exception(resp['get response error:' + r])
        if not sign:
            logging.error(r)
            raise Exception(resp['response_error'])
        return True

    @staticmethod
    def express_order(package_order_id, out_sid, is_qrode, qrode_msg):
        uri = '/warehouse/express_order/'

        params = {'package_order_id': package_order_id,
                  'out_sid': out_sid,
                  'is_qrode': is_qrode,
                  'qrode_msg': qrode_msg}
        try:
            url = getFullWebUrl(uri, params)
            req = urllib.urlopen(url)
            r = req.read()
            resp = json.loads(r)
            sign = resp['isSuccess']
        except Exception, e:
            logging.error(r)
            raise Exception(resp['get response error:' + r])
        if not sign:
            logging.error(r)
            raise Exception(resp['response_error'])
        return True

    @staticmethod
    def print_express(package_order_ids):
        uri = '/warehouse/print_express/'
        params = {'package_order_ids': ','.join([str(p) for p in package_order_ids])}
        try:
            url = getFullWebUrl(uri, params)
            req = urllib.urlopen(url)
            r = req.read()
            resp = json.loads(r)
            sign = resp['isSuccess']
        except Exception, e:
            logging.error(r)
            raise Exception(resp['get response error:' + r])
        if not sign:
            logging.error(r)
            raise Exception(resp['response_error'])
        return True

    @staticmethod
    def print_picking(package_order_ids):
        uri = '/warehouse/print_picking/'
        params = {'package_order_ids': ','.join([str(p) for p in package_order_ids])}
        try:
            url = getFullWebUrl(uri, params)
            req = urllib.urlopen(url)
            r = req.read()
            resp = json.loads(r)
            sign = resp['isSuccess']
        except Exception, e:
            logging.error(r)
            raise Exception(resp['get response error:' + r])
        if not sign:
            logging.error(r)
            raise Exception(resp['response_error'])
        return True

    @staticmethod
    def print_post(package_order_ids):
        uri = '/warehouse/print_post/'
        params = {'package_order_ids': ','.join([str(p) for p in package_order_ids])}
        try:
            url = getFullWebUrl(uri, params)
            req = urllib.urlopen(url)
            r = req.read()
            resp = json.loads(r)
            sign = resp['isSuccess']
        except Exception, e:
            logging.error(r)
            raise Exception(resp['get response error:' + r])
        if not sign:
            logging.error(r)
            raise Exception(resp['response_error'])
        return True

    @staticmethod
    def revert_packages(package_order_ids):
        uri = '/warehouse/revert/'

        params = {'package_order_ids': ','.join([str(p) for p in package_order_ids])}
        try:
            url = getFullWebUrl(uri, params)
            req = urllib.urlopen(url)
            r = req.read()
            resp = json.loads(r)
            sign = resp['isSuccess']
        except Exception, e:
            logging.error(r)
            raise Exception(resp['get response error:' + r])
        if not sign:
            logging.error(r)
            raise Exception(resp['response_error'])
        return True

    @staticmethod
    def begin_scan_check(package_no):
        uri = '/warehouse/scancheck/'
        params = {'package_no': package_no}
        try:
            url = getFullWebUrl(uri, params)
            req = urllib.urlopen(url)
            r = req.read()
            resp = json.loads(r)
            sign = resp['code']
        except Exception, e:
            logging.error(r)
            raise Exception(resp['get response error:' + r])
        if sign == 1:
            logging.error(r)
            raise Exception(resp['response_error'])
        return resp['response_content']

    @staticmethod
    def complete_scan_check(package_no):
        uri = '/warehouse/scancheck/'
        params = {'package_no': package_no}
        try:
            url = getFullWebUrl(uri, params)
            req = urllib.urlopen(url, urllib.urlencode(params))
            r = req.read()
            resp = json.loads(r)
            sign = resp['code']
        except Exception, e:
            logging.error(r)
            raise Exception(resp['get response error:' + r])
        if sign == 1:
            logging.error(r)
            raise Exception(resp['response_error'])
        return resp['response_content']

    @staticmethod
    def begin_scan_weight(package_no):
        uri = '/warehouse/scanweight/'
        params = {'package_no': package_no}
        try:
            url = getFullWebUrl(uri, params)
            req = urllib.urlopen(url)
            r = req.read()
            resp = json.loads(r)
            sign = resp['code']
        except Exception, e:
            logging.error(r)
            raise Exception(resp['get response error:' + r])
        if sign == 1:
            logging.error(r)
            raise Exception(resp['response_error'])
        return resp['response_content']

    @staticmethod
    def complete_scan_weight(package_no, weight):
        uri = '/warehouse/scanweight/'
        params = {'package_no': package_no,
                  'package_weight': weight}
        try:
            url = getFullWebUrl(uri, params)
            req = urllib2.urlopen(url, urllib.urlencode(params))
            r = req.read()
            resp = json.loads(r)
            sign = resp['code']
        except Exception, e:
            logging.error(r)
            raise Exception(resp['get response error:' + r])
        if sign == 1:
            logging.error(r)
            raise Exception(resp['response_error'])
        return resp['response_content']

    @staticmethod
    def clear_redo_sign(pid):
        uri = '/warehouse/clear_redo_sign/'
        params = {'package_order_pid': pid}
        try:
            url = getFullWebUrl(uri, params)
            req = urllib2.urlopen(url, urllib.urlencode(params))
            r = req.read()
            resp = json.loads(r)
            sign = resp['isSuccess']
        except Exception, e:
            logging.error(r)
            raise Exception(resp['get response error:' + r])
        if not sign:
            logging.error(r)
            raise Exception(resp['response_error'])
        return True


def getFullWebUrl(uri, params={}):
    conf = getconfig()
    web_host = conf.get('url', 'web_host')

    return 'http://%s%s?%s' % (web_host, uri, urllib.urlencode(params))


if __name__ == '__main__':
    WebApi.operate_packages(['8'], 'huangyan')
    WebApi.express_order()
