#-*- coding:utf8 -*-
'''
Created on 2012-7-23

@author: user1
'''
import os
import urllib
import wx.grid
from cStringIO import StringIO
from taobao.common.utils import IMAGE_ROOT

class BitmapRenderer(wx.grid.PyGridCellRenderer):
    
    def Draw(self,grid,attr,dc,rect,row,col,is_selected):
        bmp = self.parseUrlToBitmap(grid.GetCellValue(row,col))
        dc.DrawBitmap(bmp,rect.X,rect.Y)
    
    def Clone(self):
        return self.__class__()
    
    def parseUrlToBitmap(self,image_url):
        try:
            fp  = urllib.urlopen(image_url+'_50x50q90.jpg')
            data = fp.read()
            img = wx.ImageFromStream(StringIO(data))
        except:
            try:
                image_path = IMAGE_ROOT+'unavailible.jpg'
                img = wx.Image(image_path)
            except :
                pass
        finally:
            try:
                fp.close()
            except:
                pass
        img = img.Scale(50,50,wx.IMAGE_QUALITY_NORMAL)
        return wx.BitmapFromImage(img)
    
            