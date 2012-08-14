#-*- encoding:UTF-8 -*-
'''
Created on 2012-7-12

@author: user1
'''
import copy
import wx
import wx.grid as grd
from taobao.frames.tables.renderer import BitmapRenderer

class GridTable(grd.PyGridTableBase):
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
         
        i=0
        for row in datasource:
            self.data[(i,0)] = attr
            j = 1
            for v in row:
                if j in (8,9,10,11):
                    self.data[(i,j)]= v
                else:
                    self.data[(i,j)]=str(v)#给每一个单元格赋值的方法
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
        elif col in (8,9,10,11):
            self.data[(row,col)]= True if value == 'True' else False
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
        elif col in (8,9,10,11):
            attr = self.boolattr
            attr.IncRef()
        elif col == 13:
            attr = self.sid_attr
            attr.IncRef()
        else:
            attr = self.cell
            attr.IncRef() #引用加1
        if row_select ==True:
            attr.SetBackgroundColour('green')
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
         
        i=0
        for row in datasource:
            j = 0
            for v in row:
                self.data[(i,j)]=str(v)#给每一个单元格赋值的方法
                j+=1
            i+=1
            
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
        