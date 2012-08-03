#-*- coding:utf8 -*-
'''
Created on 2012-7-12

@author: user1
'''
from math import ceil

class InvalidPage(Exception):
    pass

class PageNotAnInteger(InvalidPage):
    pass

class EmptyPage(InvalidPage):
    pass

class Paginator(object):
    def __init__(self,object_list,per_page,orphans=0,allow_empty_first_page=True):
        self.object_list = object_list
        self.per_page    = per_page
        self.orphans     = orphans
        self.allow_empty_first_page = allow_empty_first_page
        self._num_pages  = self._count =None
        
    def validate_number(self,number):
        
        try:
            number = int(number)
        except ValueError:
            raise PageNotAnInteger("页号不是数字")
        if number <1:
            raise EmptyPage("页号小于1")
        if number > self.num_pages:
            if number == 1 and self.allow_empty_first_page:
                pass
            else:
                raise EmptyPage('没有记录')
        return number
    
    def page(self,number):
        number = self.validate_number(number)
        bottom = (number-1)*self.per_page
        top = bottom + self.per_page
        if top+self.orphans >= self.count:
            top = self.count
        return Page(self.object_list[bottom:top],number,self)
    
    def _get_count(self):
        if self._count is None:
            try:
                self._count = self.object_list.count()
            except (AttributeError,TypeError):
                self._count = len(self.object_list)
        return self._count
    count = property(_get_count)
    
    def _get_num_pages(self):
        if self._num_pages is None:
            if self.count == 0 and not self.allow_empty_first_page:
                self._num_pages = 0
            else:
                hits = max(1,self.count-self.orphans)
                self._num_pages = int(ceil(hits/float(self.per_page)))
        return self._num_pages
    num_pages = property(_get_num_pages)
    
    def _get_page_range(self):
        return range(1,self.num_pages+1)
    
    page_range = property(_get_page_range)
    
class Page(object):
    def __init__(self,object_list,number,paginator):
        self.object_list = object_list
        self.number = number
        self.paginator = paginator
        
    def __repr__(self):
        return '<Page %s of %s>'%(self.number,self.paginator.num_pages)
    
    def has_next(self):
        return self.number < self.paginator.num_pages
    
    def has_previous(self):
        return self.number>1
    
    def has_other_pages(self):
        return self.has_previous() or self.has_next()
    
    def next_page_number(self):
        return self.number+1
    
    def previous_page_number(self):
        return self.number-1
    
    def start_index(self):
        if self.paginator.count == 0:
            return 0
        return (self.paginator.per_page*(self.number-1))+1
    
    def end_index(self):
        if self.number == self.paginator.num_pages:
            return self.paginator.count
        return self.number*self.paginator.per_page
    
                
        

