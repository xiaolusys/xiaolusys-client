#-*- encoding:utf8 -*-
import json
import urllib
import urllib2
from taobao.common.utils import getconfig

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


