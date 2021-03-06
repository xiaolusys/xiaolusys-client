#-*- coding:utf8 -*-
'''
Created on 2012-7-12

@author: user1
'''
import copy
import wx
import wx.grid as grd
from taobao.frames.tables.renderer import BitmapRenderer
from taobao.dao import configparams as cfg

class GridTable(grd.PyGridTableBase):
    def __init__(self,datasource,rowLabels=None,colLabels=None,selectedcolour="green"):
        '''
        [
            [value1,value2,value3,...],
            [value1,value2,value3,...],
            [value1,value2,value3,...],
            ...
        ]
        '''
        grd.PyGridTableBase.__init__(self)
        self.selectedcolour = selectedcolour
        self.data={}
        self.colLabels = ('√',)
        if colLabels:
            self.colLabels += colLabels
        self.rowLabels = rowLabels
        self.rows=len(datasource)#行数
        self.cols=len(self.colLabels)#行数
        
        self.attr = attr = grd.GridCellAttr()
        attr.SetEditor(grd.GridCellBoolEditor())
        attr.SetRenderer(grd.GridCellBoolRenderer())
         
        self.boolattr = grd.GridCellAttr()
        self.boolattr.SetReadOnly()
        self.boolattr.SetEditor(grd.GridCellBoolEditor())
        self.boolattr.SetRenderer(grd.GridCellBoolRenderer())
        self.sid_cell = grd.GridCellAttr()
        self.sid_cell.SetReadOnly(1)
        
        i=0
        for row in datasource:
            self.data[(i,0)] = ''
            j = 1
            for v in row:
                self.data[(i,j)] = v#给每一个单元格赋值的方法
                j+=1
            i+=1
            
        self.cell=grd.GridCellAttr()
        #self.cell.SetReadOnly()
        self.cell.SetOverflow(False)
        
        self.sid_attr=grd.GridCellAttr()
        self.sid_attr.SetOverflow(True)
        
    # these five are the required methods
    def GetNumberRows(self):
        return self.rows
    
    def GetNumberCols(self):
        return self.cols
         
    def GetColLabelValue(self,col):#列头
        return self.colLabels[col]
     
    #同样你可以实现自己的行头 GetRowLabelValue,只要return适当的值就可以了
    def IsEmptyCell(self, row, col):
        return self.data.get((row, col)) is not None
    
    def GetValue(self, row, col):#为网格提供数据
        value = self.data.get((row, col))
        if value is not None:
            return value
        else:
            return ''
        
    def SetValue(self, row, col, value):#给表赋值
        if col ==0:
            self.data[(row,col)]= True if value else False
        elif col in (cfg.LOCKED_CELL_COL,
                     cfg.EXPRESS_CELL_COL,
                     cfg.PICKLE_CELL_COL,
                     cfg.REVIEW_CELL_COL):
            self.data[(row,col)]= True if value == 'True' or value=='1' else False
        else:    
            self.data[(row,col)] = value
        
    def CanGetValueAs(self,a,b,c):
        return True
    
    def CanSetValueAs(self,a,b,c):
        return True
        
    # the table can also provide the attribute for each cell
    def GetAttr(self, row, col, kind):
        row_select = self.data[(row,0)]  
        if col == 0:
            attr = self.attr
            attr.IncRef()
        elif col in (cfg.LOCKED_CELL_COL,
                     cfg.EXPRESS_CELL_COL,
                     cfg.PICKLE_CELL_COL,
                     cfg.REVIEW_CELL_COL):
            attr = self.boolattr
            attr.IncRef()
        elif col == cfg.OPERATOR_CELL_COL:
            attr = self.sid_attr
            attr.IncRef()
        elif col in (cfg.TRADE_ID_CELL_COL,
                     cfg.OUT_SID_CELL_COL):
            attr = self.sid_cell
            attr.IncRef()
        else:
            attr = self.cell
            attr.IncRef() #引用加1
        if row_select ==True:
            attr.SetBackgroundColour(self.selectedcolour)
        else:
            attr.SetBackgroundColour('white')
        return attr
    
    
    
class SimpleGridTable(grd.PyGridTableBase):
    def __init__(self,datasource,rowLabels=None,colLabels=None):
        '''
        [
            [value1,value2,value3,...],
            [value1,value2,value3,...],
            [value1,value2,value3,...],
            ...
        ]
        '''
        grd.PyGridTableBase.__init__(self)
        self.data={}
        self.colLabels = colLabels
        self.rowLabels = rowLabels
        self.rows=len(datasource)#行数
        self.cols=len(self.colLabels)#行数
        print 'cols=',len(self.colLabels),'label cols=',self.cols
        i=0
        for row in datasource:
            j = 0
            for v in row:
                self.data[(i,j)]=v#给每一个单元格赋值的方法
                j+=1
            i+=1
        print 'data:',self.data
        self.cell=grd.GridCellAttr()
        self.cell.SetOverflow(False)
        
        self.imagecell = grd.GridCellAttr()
        self.imagecell.SetEditor(grd.GridCellTextEditor())
        self.imagecell.SetRenderer(BitmapRenderer())
        
    # these five are the required methods
    def GetNumberRows(self):
        return self.rows
    
    def GetNumberCols(self):
        return self.cols
         
    def GetColLabelValue(self,col):#列头
        return self.colLabels[col]
     
    #同样你可以实现自己的行头 GetRowLabelValue,只要return适当的值就可以了
    def IsEmptyCell(self, row, col):
        return self.data.get((row, col)) is not None
    
    def GetValue(self, row, col):#为网格提供数据
        value = self.data.get((row, col))
        if value is not None:
            return value
        else:
            return ''
        
    def SetValue(self, row, col, value):#给表赋值
        self.data[(row,col)] = value
        
    def CanGetValueAs(self,a,b,c):
        return True
    
    def CanSetValueAs(self,a,b,c):
        return True
        
    # the table can also provide the attribute for each cell
    def GetAttr(self, row, col, kind):
        if col==0:
            attr = self.imagecell
            attr.IncRef()
        else:
            attr = self.cell
            attr.IncRef() #引用加1
        return attr
        

class WeightGridTable(grd.PyGridTableBase):
    def __init__(self,rowLabels=None,colLabels=None):

        grd.PyGridTableBase.__init__(self)
        self.data={}
        self.colLabels = colLabels
        self.rowLabels = rowLabels
        self.rows = 1
        self.cols=len(self.colLabels)#行数
            
        self.cell=grd.GridCellAttr()
        self.cell.SetOverflow(False)

    # these five are the required methods
    def GetNumberRows(self):
        return self.rows
    
    def GetNumberCols(self):
        return self.cols
         
    def GetColLabelValue(self,col):#列头
        return self.colLabels[col]
     
    #同样你可以实现自己的行头 GetRowLabelValue,只要return适当的值就可以了
    def IsEmptyCell(self, row, col):
        return self.data.get((row, col)) is not None
    
    def GetValue(self, row, col):#为网格提供数据
        value = self.data.get((row, col))
        if value is not None:
            return value
        else:
            return ''
        
    def SetValue(self, row, col, value):#给表赋值
        self.data[(row,col)] = value
        
    def CanGetValueAs(self,a,b,c):
        return True
    
    def CanSetValueAs(self,a,b,c):
        return True
        
    # the table can also provide the attribute for each cell
    def GetAttr(self, row, col, kind):
        attr = self.cell
        attr.IncRef() #引用加1
        return attr
    
    def InsertRows(self,pos=0,numRows=1,updateLabels=True):
        rows   = self.NumberRows
        cols   = self.NumberCols
        
        data  = copy.copy(self.data)
        for row in xrange(pos,rows):
            for col in xrange(0,cols):
                self.data[(row+numRows,col)] = data[(row,col)]
        for col in xrange(0,cols):
            for row in xrange(0,numRows):
                self.data[(pos+row,col)] = '' 
        self.rows += numRows
        
        return True
        

class ChargeGridTable(grd.PyGridTableBase):
    def __init__(self,datasource=(),rowLabels=None,colLabels=None):
        
        grd.PyGridTableBase.__init__(self)
        self.data={}
        self.colLabels = colLabels
        self.rowLabels = rowLabels
        self.rows = len(datasource)
        self.cols=len(self.colLabels)#行数
        i=0
        for row in datasource:
            j = 0
            for v in row:
                self.data[(i,j)]=v #给每一个单元格赋值的方法
                j+=1
            i+=1
        
        self.cell=grd.GridCellAttr()
        self.cell.SetOverflow(False)
        
    # these five are the required methods
    def GetNumberRows(self):
        return self.rows
    
    def GetNumberCols(self):
        return self.cols
         
    def GetColLabelValue(self,col):#列头
        return self.colLabels[col]
     
    #同样你可以实现自己的行头 GetRowLabelValue,只要return适当的值就可以了
    def IsEmptyCell(self, row, col):
        return self.data.get((row, col)) is not None
    
    def GetValue(self, row, col):#为网格提供数据
        value = self.data.get((row, col))
        if value is not None:
            return value
        else:
            return ''
        
    def SetValue(self, row, col, value):#给表赋值
        self.data[(row,col)] = value
        
    def CanGetValueAs(self,a,b,c):
        return True
    
    def CanSetValueAs(self,a,b,c):
        return True
        
    # the table can also provide the attribute for each cell
    def GetAttr(self, row, col, kind):
        attr = self.cell
        attr.IncRef() #引用加1
        return attr
    
    def InsertRows(self,pos=0,numRows=1,updateLabels=True):
        rows   = self.NumberRows
        cols   = self.NumberCols
        
        data  = copy.copy(self.data)
        for row in xrange(pos,rows):
            for col in xrange(0,cols):
                self.data[(row+numRows,col)] = data[(row,col)]
        for col in xrange(0,cols):
            for row in xrange(0,numRows):
                self.data[(pos+row,col)] = '' 
        self.rows += numRows
        
        return True        

        
class CheckGridTable(grd.PyGridTableBase):
    def __init__(self,datasource,rowLabels=None,colLabels=None):
        '''
        [
            [value1,value2,value3,...],
            [value1,value2,value3,...],
            [value1,value2,value3,...],
            ...
        ]
        '''
        grd.PyGridTableBase.__init__(self)
        self.data={}
        self.colLabels = colLabels
        self.rowLabels = rowLabels
        self.rows=len(datasource)#行数
        self.cols=len(self.colLabels)#行数
         
        i=0
        for row in datasource:
            j = 0
            for v in row:
                self.data[(i,j)]=v #给每一个单元格赋值的方法
                j+=1
            i+=1
            
        self.cell = grd.GridCellAttr()
        self.cell.SetOverflow(False)
        self.cell.SetReadOnly()
        
        self.imagecell = grd.GridCellAttr()
        self.imagecell.SetEditor(grd.GridCellTextEditor())
        self.imagecell.SetRenderer(BitmapRenderer())
        self.imagecell.SetReadOnly()
        
    # these five are the required methods
    def GetNumberRows(self):
        return self.rows
    
    def GetNumberCols(self):
        return self.cols
         
    def GetColLabelValue(self,col):#列头
        return self.colLabels[col]
     
    #同样你可以实现自己的行头 GetRowLabelValue,只要return适当的值就可以了
    def IsEmptyCell(self, row, col):
        return self.data.get((row, col)) is not None
    
    def GetValue(self, row, col):#为网格提供数据
        value = self.data.get((row, col))
        if value is not None:
            return value
        else:
            return ''
        
    def SetValue(self, row, col, value):#给表赋值
        self.data[(row,col)] = value
        
    def CanGetValueAs(self,a,b,c):
        return True
    
    def CanSetValueAs(self,a,b,c):
        return True
        
    # the table can also provide the attribute for each cell
    def GetAttr(self, row, col, kind):
        check_num = int(self.data[(row,12)])
        origin_num = int(self.data[(row,4)])
        need_check = self.data[(row,8)].upper() == 'Y'
        if col==0:
            attr = self.imagecell
            attr.IncRef()
        else:
            attr = self.cell
            attr.IncRef() #引用加1
            
        if not need_check and check_num == 0:
            attr.SetBackgroundColour('GREY')
        elif check_num>0 and check_num<origin_num:
            attr.SetBackgroundColour('PINK')
        elif check_num >= origin_num:
            attr.SetBackgroundColour('GREEN')
        else :
            attr.SetBackgroundColour('WHITE')
        return attr
       
    
    