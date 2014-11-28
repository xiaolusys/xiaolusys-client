#-*- coding:utf8 -*-
'''
Created on 2012-7-27

@author: user1
'''
import re
import weakref
import wx,wx.grid
from taobao.common.utils import create_session
from taobao.dao.models import MergeTrade,LogisticsCompany,MergeOrder,Product,ProductSku
from taobao.frames.panels.gridpanel import CheckGridPanel
from taobao.dao.tradedao import get_used_orders,get_oparetor
from taobao.dao import configparams as cfg 
from taobao.dao import webapi as api
from taobao.dao.yundao import printYUNDAPDF
from taobao.common.logger import get_sentry_logger,log_exception

logger = get_sentry_logger()
RESET_CODE    = '11110000'   #验货框重置条码
NOTSCAN_CODE  = '00001111'   #不需扫描条码

class ScanCheckPanel(wx.Panel):
    
    def __init__(self,parent,id=-1):
        wx.Panel.__init__(self,parent,id)
        self.is_auto_save = False
        self.trade = None

        self.out_sid_label = wx.StaticText(self,-1,u'快递单号')
        self.out_sid_text  = wx.TextCtrl(self,-1,size=(200,-1),style=wx.TE_PROCESS_ENTER)
        self.barcode_label = wx.StaticText(self,-1,u'商品条码')
        self.barcode_text  = wx.TextCtrl(self,-1,size=(200,-1),style=wx.TE_PROCESS_ENTER)
        self.cancel_button   = wx.Button(self,-1,u'清除')
        
        self.status_bar = wx.Button(self,-1,'', size=(20, 20), style=wx.SUNKEN_BORDER)
        self.error_text = wx.StaticText(self,-1)
        
        self.gridpanel = CheckGridPanel(self,-1)
        self.order_box2 = wx.StaticBox(self,-1,u'待扫描商品列表')

        self.__set_properties()
        self.__do_layout()
        self.__evt_bind()
    
    
    def __set_properties(self):
        self.SetName('check panel')
        
        self.out_sid_text.SetFocus()
        self.status_bar.SetBackgroundColour('RED')
        
        
    def __do_layout(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        flex_sizer1 = wx.FlexGridSizer(hgap=5,vgap=5)
        flex_sizer1.Add((100,10),0,1)
        flex_sizer1.Add(self.out_sid_label,0,2)
        flex_sizer1.Add(self.out_sid_text,0,3)
        flex_sizer1.Add(self.barcode_label,0,4)
        flex_sizer1.Add(self.barcode_text,0,5)
        
        flex_sizer1.Add((10,10),0,8)
        flex_sizer1.Add(self.cancel_button,0,11)
        flex_sizer1.Add(self.status_bar,0,12,border=10)
        flex_sizer1.Add(self.error_text,0,13)
        
        sbsizer2=wx.StaticBoxSizer(self.order_box2,wx.VERTICAL)
        sbsizer2.Add(self.gridpanel,proportion=1,flag=wx.EXPAND,border=10) 
        
        main_sizer.Add(flex_sizer1,flag=wx.EXPAND)
        main_sizer.Add(sbsizer2,-1,flag=wx.EXPAND)
        self.SetSizer(main_sizer)
        self.Layout()
        
    def __evt_bind(self):
        
        self.Bind(wx.EVT_TEXT_ENTER, self.onOutsidTextChange,self.out_sid_text)
        self.Bind(wx.EVT_TEXT_ENTER, self.onCheckCodeTextChange,self.barcode_text)
        self.Bind(wx.EVT_BUTTON,self.onClickCancelBtn,self.cancel_button)   
    
    def getSid(self):
        sid = self.out_sid_text.GetValue().strip()
        if len(sid) < 20:
            return sid
        return sid[0:13]
    
    @log_exception
    def onOutsidTextChange(self,evt):

        out_sid      = self.getSid()
        if not out_sid:
            return 
        
        try:
            trade = api.getTradeScanCheckInfo(out_sid)
            self.trade = trade
            self.gridpanel.setData(self.trade)
            
            self.barcode_text.SetFocus()
            self.error_text.SetLabel('')
            self.status_bar.SetBackgroundColour('GREEN')
            
        except Exception,exc:
            self.error_text.SetLabel('%s'%exc.message)
            self.out_sid_text.Clear()
            self.out_sid_text.SetFocus()
            self.status_bar.SetBackgroundColour('RED')
            
        evt.Skip()
            
             
    def setBarCode(self):
        
        barcode = self.barcode_text.GetValue().strip()
        
        if barcode == RESET_CODE:
            self.out_sid_text.Clear()
            self.barcode_text.Clear()
            self.out_sid_text.SetFocus()
            self.gridpanel.clearTable()
            self.status_bar.SetBackgroundColour('RED')
            return
            
        if self.trade and barcode:
            checked = self.gridpanel.setBarCode(barcode)
            if barcode == NOTSCAN_CODE or checked:
                if self.gridpanel.isCheckOver():
                   
                    api.completeScanCheck(self.trade['package_no'])
                    
                    self.gridpanel.clearTable()
                    self.out_sid_text.Clear()
                    self.barcode_text.Clear()
                    self.out_sid_text.SetFocus()
                else:
                    self.barcode_text.Clear()
                    self.barcode_text.SetFocus()
            else:
                self.barcode_text.Clear()
                self.barcode_text.SetFocus()
         
         
    def onCheckCodeTextChange(self,evt):

        self.setBarCode()
   
            
    def onClickCancelBtn(self,evt):
        
        self.out_sid_text.Clear()
        self.barcode_text.Clear()
        self.out_sid_text.SetFocus()
    
    
    
        
