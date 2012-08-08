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
    description = "��յ�������ERP�ͻ���",
    name = "���ERP�ͻ���",
    options=options,
    zipfile=None,
    windows=[{"script":"auimain.py"}],
    data_files=[("images",['images/unavailible.png']),
                ("taobao/templates",['taobao/templates/logistics_template.html','taobao/templates/trade_picking_template.html']),
                ("taobao",["taobao/system.conf"])]
    )
