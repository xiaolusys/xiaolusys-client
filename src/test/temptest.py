'''
Created on 2012-6-2

@author: user1
'''
from string import Template
import re as _re

deli = '#'
idp = r'[_a-z][_a-z0-9]*'
pattern = r"""
%(delim)s(?:
  (?P<escaped>%(delim)s) |   # Escape sequence of two delimiters
  (?P<named>%(id)s)      |   # delimiter and a Python identifier
  {(?P<braced>%(id)s)}   |   # delimiter and a braced identifier
  (?P<invalid>)              # Other ill-formed delimiter exprs
)
"""

class MyTemplate(Template):
    """docstring for MyTemplate"""
    #delimiter = '#'
    def __init__(self, template, delimiter=Template.delimiter):
        super(MyTemplate, self).__init__(template)
        MyTemplate.delimiter = delimiter


pattern = pattern % {'delim': _re.escape(deli), 'id': idp}
pattern = _re.compile(pattern, _re.IGNORECASE | _re.VERBOSE)
MyTemplate.pattern = pattern
t = MyTemplate('#who likes #what',delimiter='#')
print t.substitute({'who': 'jianpx', 'what': 'python'})
