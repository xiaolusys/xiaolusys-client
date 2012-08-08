#-*- coding:gbk -*-
from distutils.core import setup
import py2exe


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
    description = u'\u91d1\u521a\u7535\u5b50\u5546\u52a1ERP\u5ba2\u6237\u7aef',
    name = u'\u91d1\u521aERP\u5ba2\u6237\u7aef',
    options=options,
    zipfile=None,
    windows=[{"script":"auimain.py"}],
    data_files=[("images",['images/unavailible.png']),
                ("taobao/templates",['taobao/templates/logistics_template.html','taobao/templates/trade_picking_template.html']),
                ("taobao",["taobao/system.conf"])]
    )
