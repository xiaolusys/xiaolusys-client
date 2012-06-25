'''
Created on 2012-6-1

@author: user1
'''

class Super1(object):
    '''
    classdocs
    '''
    pass 

class Super2(object):
    '''
    classdocs
    '''
    pass 

class ToAnalyze(Super1,Super2):
    '''
    classdocs
    '''
    def method1(self):
        pass
    def method2(self):
        pass

class Sub1(ToAnalyze):
    '''
    classdocs
    '''
    pass
        