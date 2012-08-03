#-*- coding:utf8 -*-
'''
Created on 2012-7-23

@author: user1
'''
import os
import urllib
import wx.grid
import Image
from cStringIO import StringIO
import taobao
from taobao.common.utils import IMAGE_ROOT

class BitmapRenderer(wx.grid.PyGridCellRenderer):
    
    def Draw(self,grid,attr,dc,rect,row,col,is_selected):
        bmp = self.parseUrlToBitmap(grid.GetCellValue(row,col))
        dc.DrawBitmap(bmp,rect.X,rect.Y)
    
    def Clone(self):
        return self.__class__()
    
    def parseUrlToBitmap(self,image_url):
        try:
            fp  = urllib.urlopen(image_url)
            data = fp.read()
            img = wx.ImageFromStream(StringIO(data))
        except:
            image_path = IMAGE_ROOT+'unavailible.png'
            img = Image.open(image_path)
        finally:
            try:
                fp.close()
            except:
                pass
        img = img.Scale(80,80,wx.IMAGE_QUALITY_HIGH)
        return wx.BitmapFromImage(img)
    
            