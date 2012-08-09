#encoding:utf8
import sys
from distutils.core import setup
import py2exe

#reload(sys)
#sys.setdefaultencoding('utf-8')

includes = ['taobao']
options ={"py2exe":
        {
            "compressed":1,
            "optimize":2,
            "includes":includes,
            "bundle_files":1,
            "packages":['taobao']
        }
    }

setup(
    version = "0.1.0",
    description = '金刚ERP客户端',
    name = '金刚',
    options=options,
    zipfile=None,
    windows=[{"script":"auimain.py"}],
    data_files=[("images",['images/unavailible.png']),
                ("taobao/templates",['taobao/templates/logistics_template.html','taobao/templates/trade_picking_template.html']),
                ("taobao",["taobao/system.conf"])]
    )
