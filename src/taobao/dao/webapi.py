#-*- encoding:utf8 -*-
import json
import urllib
import urllib2
from taobao.common.utils import getconfig


class WebApi(object):

    conf = getconfig()
    web_host = conf.get('url', 'web_host')

    @staticmethod
    def operate_packages(package_order_ids, operator_id):
        uri = '/warehouse/operate/operate_package_order/'
        uri = '/warehouse/operate/'
        params = {'package_order_ids': ','.join([str(p) for p in package_order_ids]),
                  'operator': operator_id}
        url = getFullWebUrl(uri, params)
        req = urllib.urlopen(url)
        resp = json.loads(req.read())
        if not resp['isSuccess']:
            raise Exception(resp['response_error'])
        return True

    @staticmethod
    def express_order(package_order_id, out_sid, is_qrode, qrode_msg):
        uri = '/warehouse/express_order/'

        params = {'package_order_id': package_order_id,
                  'out_sid': out_sid,
                  'is_qrode': is_qrode,
                  'qrode_msg': qrode_msg}

        url = getFullWebUrl(uri, params)

        req = urllib.urlopen(url)
        resp = json.loads(req.read())

        if not resp['isSuccess']:
            raise Exception(resp['response_error'])

        return True

    @staticmethod
    def print_express(package_order_ids):
        uri = '/warehouse/print_express/'
        params = {'package_order_ids': ','.join([str(p) for p in package_order_ids])}
        url = getFullWebUrl(uri, params)
        req = urllib.urlopen(url)
        resp = json.loads(req.read())
        if not resp['isSuccess']:
            raise Exception(resp['response_error'])
        return True

    @staticmethod
    def print_picking(package_order_ids):
        uri = '/warehouse/print_picking/'
        params = {'package_order_ids': ','.join([str(p) for p in package_order_ids])}
        url = getFullWebUrl(uri, params)
        req = urllib.urlopen(url)
        resp = json.loads(req.read())
        if not resp['isSuccess']:
            raise Exception(resp['response_error'])
        return True

    @staticmethod
    def print_post(package_order_ids):
        uri = '/warehouse/print_post/'
        params = {'package_order_ids': ','.join([str(p) for p in package_order_ids])}
        url = getFullWebUrl(uri, params)
        req = urllib.urlopen(url)
        resp = json.loads(req.read())
        if not resp['isSuccess']:
            raise Exception(resp['response_error'])
        return True

    @staticmethod
    def revert_packages(package_order_ids):
        uri = '/warehouse/revert/'

        params = {'package_order_ids': ','.join([str(p) for p in package_order_ids])}

        url = getFullWebUrl(uri, params)

        req = urllib.urlopen(url)
        resp = json.loads(req.read())

        if not resp['isSuccess']:
            raise Exception(resp['response_error'])

        return True

    @staticmethod
    def begin_scan_check(package_no):
        uri = '/warehouse/scancheck/'
        params = {'package_no': package_no}
        url = getFullWebUrl(uri, params)
        req = urllib.urlopen(url)
        resp = json.loads(req.read())
        if resp['code'] == 1:
            raise Exception(resp['response_error'])
        return resp['response_content']

    @staticmethod
    def complete_scan_check(package_no):
        uri = '/warehouse/scancheck/'
        params = {'package_no': package_no}
        url = getFullWebUrl(uri)
        req = urllib.urlopen(url, urllib.urlencode(params))
        resp = json.loads(req.read())
        if resp['code'] == 1:
            raise Exception(resp['response_error'])
        return True

    @staticmethod
    def begin_scan_weight(package_no):
        uri = '/warehouse/scanweight/'
        params = {'package_no': package_no}
        url = getFullWebUrl(uri, params)
        req = urllib2.urlopen(url)
        resp = json.loads(req.read())
        if resp['code'] == 1:
            raise Exception(resp['response_error'])
        return resp['response_content']

    @staticmethod
    def complete_scan_weight(package_no, weight):
        uri = '/warehouse/scanweight/'
        params = {'package_no': package_no,
                  'package_weight': weight}
        url = getFullWebUrl(uri, params)
        req = urllib2.urlopen(url, urllib.urlencode(params))
        resp = json.loads(req.read())
        if resp['code'] == 1:
            raise Exception(resp['response_error'])
        return resp['response_content']

    @staticmethod
    def clear_redo_sign(pid):
        uri = '/warehouse/clear_redo_sign/'
        params = {'package_order_pid': pid}
        url = getFullWebUrl(uri, params)
        req = urllib2.urlopen(url, urllib.urlencode(params))
        resp = json.loads(req.read())
        if resp['isSuccess']:
            return True
        return False

def getFullWebUrl(uri,params={}):

    conf = getconfig()
    web_host = conf.get('url', 'web_host')
    
    return 'http://%s%s?%s'%(web_host,uri,urllib.urlencode(params))


if __name__ == '__main__':
    WebApi.operate_packages(['8'],'huangyan')
    WebApi.express_order()