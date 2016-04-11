#-*- encoding:utf8 -*-
import json
import urllib
import urllib2
from taobao.common.utils import getconfig


class WebApi(object):

    conf = getconfig()
    web_host = conf.get('url', 'web_host')

    def operate_packages(self, package_order_ids, operator_id):
        uri = '/warehouse/operate_package_order/'
        params = {'package_order_ids': ','.join([str(p) for p in package_order_ids]),
                  'operator': operator_id}
        url = getFullWebUrl(uri, params)
        req = urllib.urlopen(url)
        resp = json.loads(req.read())
        if not resp['isSuccess']:
            raise Exception(resp['response_error'])
        return resp['response_content']

    def express_order(self, package_order_id, out_sid, is_qrode, qrode_msg):
        uri = '/warehouse/revert_package/'

        params = {'package_order_id': package_order_id}

        url = getFullWebUrl(uri, params)

        req = urllib.urlopen(url)
        resp = json.loads(req.read())

        if not resp['isSuccess']:
            raise Exception(resp['response_error'])

        return resp['response_content']

    def revert_packages(self, package_order_ids):
        uri = '/warehouse/revert_package/'

        params = {'package_order_ids': ','.join([str(p) for p in package_order_ids])}

        url = getFullWebUrl(uri, params)

        req = urllib.urlopen(url)
        resp = json.loads(req.read())

        if not resp['isSuccess']:
            raise Exception(resp['response_error'])

        return resp['response_content']


def getFullWebUrl(uri,params={}):

    conf = getconfig()
    web_host = conf.get('url', 'web_host')
    
    return 'http://%s%s?%s'%(web_host,uri,urllib.urlencode(params))

def getTradeScanCheckInfo(package_no):
    
    uri = '/trades/scancheck/'
    
    params = {'package_no':package_no}
    
    url  = getFullWebUrl(uri,params)
    
    req = urllib.urlopen(url)
    resp = json.loads(req.read())
    
    if resp['code'] == 1:
        raise Exception(resp['response_error'])
    
    return resp['response_content']


def completeScanCheck(package_no):
    
    uri = '/trades/scancheck/'
    
    params = {'package_no':package_no}
    
    url  = getFullWebUrl(uri)
    
    req = urllib.urlopen(url,urllib.urlencode(params))
    resp = json.loads(req.read())
    
    if resp['code'] == 1:
        raise Exception(resp['response_error'])
    
    return resp['response_content']


def getWeightTradeInfo(package_no):
    
    uri = '/trades/scanweight/'
    
    params = {'package_no':package_no}
    
    url  = getFullWebUrl(uri,params)
    
    req = urllib2.urlopen(url)
    resp = json.loads(req.read())
    
    if resp['code'] == 1:
        raise Exception(resp['response_error'])
    
    return resp['response_content']

def saveWeight2Trade(package_no,weight):
    
    uri = '/trades/scanweight/'
    
    params = {'package_no':package_no,
              'package_weight':weight}
    
    url  = getFullWebUrl(uri,params)
    
    req = urllib2.urlopen(url,urllib.urlencode(params))
    resp = json.loads(req.read())
    
    if resp['code'] == 1:
        raise Exception(resp['response_error'])
    
    return resp['response_content']


