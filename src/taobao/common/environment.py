'''
Created on 2012-6-5

@author: user1
'''
from jinja2 import Template,Environment,PackageLoader
from taobao.common.filters import datetimeformat,trans_string,slice_string,print_wraps,parse_val,cut_string

def get_template(template_name,package_name='taobao.templates',package_path='../templates',encoding='utf8'):
    env = Environment(loader=PackageLoader(package_name,package_path=package_path,encoding=encoding))
    env.filters['datetimeformat'] = datetimeformat
    env.filters['parse_val']    = parse_val
    env.filters['print_wraps']  = print_wraps
    env.filters['trans_string'] = trans_string
    env.filters['slice_string'] = slice_string
    env.filters['cut_string']   = cut_string
    return env.get_template(template_name)