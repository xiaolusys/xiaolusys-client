#setup.py
from distutils.core import setup
import py2exe


#includes = []
options ={"py2exe":
        {
            "compressed":1,
            "optimize":2,
            #"includes":includes,
            "bundle_files":1,
            "packages":[],
            "dll_excludes": ["MSVCP90.dll"],
        }
    }

setup(
    version = "0.1.0",
    description = "Super ERP Cient",
    name = "SUPER ERP MGR",
    options=options,
    zipfile=None,
    windows=[{"script":"wxprint.py"}],
#    data_files=[("images",['images/unavailible.png']),
#                ("taobao/templates",['taobao/templates/logistics_template.html','taobao/templates/trade_picking_template.html']),
#                ("taobao",["taobao/system.conf"])]
    )
