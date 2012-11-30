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
from taobao.dao.tradedao import get_used_orders
from taobao.dao.configparams import TRADE_TYPE,TRADE_STATUS,SHIPPING_TYPE,SYS_STATUS,SYS_STATUS_FINISHED,\
    SYS_STATUS_WAITSCANWEIGHT,SYS_STATUS_WAITSCANCHECK



class ScanCheckPanel(wx.Panel):
    
    def __init__(self,parent,id=-1):
        wx.Panel.__init__(self,parent,id)
        self.Session = parent.Session
        self.is_auto_save = False
        self.trade = None

        self.company_label = wx.StaticText(self,-1,u'快递公司')
        self.company_select = wx.ComboBox(self,-1)
        self.out_sid_label = wx.StaticText(self,-1,u'快递单号')
        self.out_sid_text  = wx.TextCtrl(self,-1,style=wx.TE_PROCESS_ENTER)
        self.barcode_label = wx.StaticText(self,-1,u'商品条码')
        self.barcode_text  = wx.TextCtrl(self,-1,style=wx.TE_PROCESS_ENTER)
        self.hand_add_button   = wx.Button(self,-1,u'确定') 
        self.cancel_button   = wx.Button(self,-1,u'取消')
        
        self.error_text = wx.StaticText(self,-1)
        self.gridpanel = CheckGridPanel(self,-1)
        self.order_box2 = wx.StaticBox(self,-1,u'待扫描商品列表')

        self.__set_properties()
        self.__do_layout()
        self.__evt_bind()
    
    
    def __set_properties(self):
        self.SetName('check panel')
        
        with create_session(self.Parent) as session: 
            logistics_companies = session.query(LogisticsCompany).filter_by(status=True).order_by('priority desc').all()
        self.company_select.AppendItems([company.name for company in logistics_companies])
        self.out_sid_text.SetFocus()

    
    def __do_layout(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        flex_sizer1 = wx.FlexGridSizer(hgap=5,vgap=5)
        flex_sizer1.Add(self.company_label,0,0)
        flex_sizer1.Add(self.company_select,0,1)
        flex_sizer1.Add(self.out_sid_label,0,2)
        flex_sizer1.Add(self.out_sid_text,0,3)
        flex_sizer1.Add(self.barcode_label,0,4)
        flex_sizer1.Add(self.barcode_text,0,5)
        
        flex_sizer1.Add(self.hand_add_button,0,10)
        flex_sizer1.Add(self.cancel_button,0,11)
        flex_sizer1.Add(self.error_text,0,12)
        
        sbsizer2=wx.StaticBoxSizer(self.order_box2,wx.VERTICAL)
        sbsizer2.Add(self.gridpanel,proportion=1,flag=wx.EXPAND,border=10) 
        
        main_sizer.Add(flex_sizer1,flag=wx.EXPAND)
        main_sizer.Add(sbsizer2,-1,flag=wx.EXPAND)
        self.SetSizer(main_sizer)
        self.Layout()
        
    def __evt_bind(self):
        
        self.Bind(wx.EVT_COMBOBOX, self.onComboboxSelect, self.company_select)
        self.Bind(wx.EVT_TEXT_ENTER, self.onOutsidTextChange,self.out_sid_text)
        self.Bind(wx.EVT_TEXT_ENTER, self.onCheckCodeTextChange,self.barcode_text)
        self.Bind(wx.EVT_BUTTON,self.onClickSaveBtn,self.hand_add_button)
        self.Bind(wx.EVT_BUTTON,self.onClickCancelBtn,self.cancel_button)   
    
    def onComboboxSelect(self,evt):
        company_name = self.company_select.GetValue().strip()
        out_sid      = self.out_sid_text.GetValue().strip()
        trades = None
        if company_name:
            with create_session(self.Parent) as session:
                logistics_company = session.query(LogisticsCompany).filter_by(name=company_name).first()
                trades = session.query(MergeTrade).filter_by(out_sid=out_sid,
                         logistics_company_id=logistics_company.id,sys_status=SYS_STATUS_WAITSCANCHECK)
        count = trades.count() if trades else 0   
        if count>1 :
            self.error_text.SetLabel(u'该快递单号已重复，请反审核后修改')
            self.error_text.SetForegroundColour('black')
            self.error_text.SetBackgroundColour('red')
        elif count == 1:
            self.trade = trades.one()
            self.gridpanel.setData(self.trade)
            self.barcode_text.SetFocus()
            self.error_text.SetLabel('')
        else:
            self.error_text.SetLabel(u'未找到该订单')
            self.error_text.SetForegroundColour('black')
            self.error_text.SetBackgroundColour('red')
        
          
                
    def onOutsidTextChange(self,evt):
        company_name = self.company_select.GetValue().strip()
        out_sid      = self.out_sid_text.GetValue().strip() 
        trades = None
        with create_session(self.Parent) as session:
            if company_name and out_sid:
                logistics_company = session.query(LogisticsCompany).filter_by(name=company_name).first()
                trades = session.query(MergeTrade).filter_by(out_sid=out_sid,
                       logistics_company_id=logistics_company.id,sys_status=SYS_STATUS_WAITSCANCHECK)
            elif out_sid :
                trades = session.query(MergeTrade).filter_by(out_sid=out_sid,sys_status=SYS_STATUS_WAITSCANCHECK)
                 
        count = trades.count() if trades else 0 
        if count>1 :
            self.error_text.SetLabel(u'该快递单号已重复，请反审核后修改')
            self.error_text.SetForegroundColour('black')
            self.error_text.SetBackgroundColour('red')
            self.clearTradeInfoPanel()
        elif count == 1:
            self.trade = trades.one()
            self.gridpanel.setData(self.trade)
            self.barcode_text.SetFocus()
            self.error_text.SetLabel('')
            self.error_text.SetForegroundColour('white')
            self.error_text.SetBackgroundColour('black')
        else:
            self.error_text.SetLabel(u'未找到该订单')
            self.error_text.SetForegroundColour('black')
            self.error_text.SetBackgroundColour('red')
            self.clearTradeInfoPanel()
        evt.Skip()
         
    def setBarCode(self):
        barcode = self.barcode_text.GetValue().strip()
        if self.trade and barcode:
            checked = self.gridpanel.setBarCode(barcode)
            if checked:
                if self.gridpanel.isCheckOver():
                    with create_session(self.Parent) as session: 
                        #库存减掉后，修改发货状态
                        session.query(MergeTrade).filter_by(id=self.trade.id,sys_status=SYS_STATUS_WAITSCANCHECK)\
                            .update({'sys_status':SYS_STATUS_WAITSCANWEIGHT},synchronize_session='fetch')
                            
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
   
    def onClickSaveBtn(self,evt):

        self.setBarCode()
            
    def onClickCancelBtn(self,evt):
        self.out_sid_text.Clear()
        self.barcode_text.Clear()

           
     
