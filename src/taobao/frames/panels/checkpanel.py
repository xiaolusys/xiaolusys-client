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
from taobao.dao import configparams as cfg 
from taobao.dao.yundao import printYUNDAPDF
from taobao.common.logger import get_sentry_logger,log_exception

logger = get_sentry_logger()
RESET_CODE    = '11110000'   #验货框重置条码
NOTSCAN_CODE  = '00001111'   #不需扫描条码

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
        self.print_qrcode_label    = wx.StaticText(self,-1,u'打印二维码')
        self.print_qrcode_checkbox = wx.CheckBox(self,-1)
        self.hand_add_button   = wx.Button(self,-1,u'确定') 
        self.cancel_button   = wx.Button(self,-1,u'取消')
        
        self.status_bar = wx.Button(self,-1,'', size=(20, 20), style=wx.SUNKEN_BORDER)
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
        self.status_bar.SetBackgroundColour('RED')
        
        
    def __do_layout(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        flex_sizer1 = wx.FlexGridSizer(hgap=5,vgap=5)
        flex_sizer1.Add(self.company_label,0,0)
        flex_sizer1.Add(self.company_select,0,1)
        flex_sizer1.Add(self.out_sid_label,0,2)
        flex_sizer1.Add(self.out_sid_text,0,3)
        flex_sizer1.Add(self.barcode_label,0,4)
        flex_sizer1.Add(self.barcode_text,0,5)
        flex_sizer1.Add(self.print_qrcode_label,0,6)
        flex_sizer1.Add(self.print_qrcode_checkbox,0,7)
        
        flex_sizer1.Add((10,10),0,8)
        flex_sizer1.Add(self.hand_add_button,0,10)
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
                         logistics_company_id=logistics_company.id,sys_status=cfg.SYS_STATUS_WAITSCANCHECK)
        count = trades.count() if trades else 0   
        if count>1 :
            self.error_text.SetLabel(u'该快递单号已重复，请审核后再扫描')
            self.status_bar.SetBackgroundColour('RED')
        elif count == 1:
            self.trade = trades.one()
            self.gridpanel.setData(self.trade)
            self.barcode_text.SetFocus()
            self.error_text.SetLabel('')
            self.status_bar.SetBackgroundColour('GREEN')
        else:
            self.error_text.SetLabel(u'未找到该订单')
            self.out_sid_text.Clear()
            self.out_sid_text.SetFocus()
            self.status_bar.SetBackgroundColour('RED')
        
        self.Layout()  
                
    def onOutsidTextChange(self,evt):
        try:
            company_name = self.company_select.GetValue().strip()
            out_sid      = self.out_sid_text.GetValue().strip() 
            trades = None
            with create_session(self.Parent) as session:
                if company_name and out_sid:
                    logistics_company = session.query(LogisticsCompany).filter_by(name=company_name).first()
                    trades = session.query(MergeTrade).filter_by(out_sid=out_sid,
                           logistics_company_id=logistics_company.id,sys_status=cfg.SYS_STATUS_WAITSCANCHECK)
                elif out_sid :
                    trades = session.query(MergeTrade).filter_by(out_sid=out_sid,sys_status=cfg.SYS_STATUS_WAITSCANCHECK)
            count = trades.count() if trades else 0 
            if count>1 :
                self.error_text.SetLabel(u'该快递单号已重复，请审核后再扫描')
                self.status_bar.SetBackgroundColour('RED')
            elif count == 1:
                self.trade = trades.one()
                self.gridpanel.setData(self.trade)
                self.barcode_text.SetFocus()
                self.error_text.SetLabel('')
                self.status_bar.SetBackgroundColour('GREEN')
            else:
                self.error_text.SetLabel(u'未找到该订单')
                self.out_sid_text.Clear()
                self.out_sid_text.SetFocus()
                self.status_bar.SetBackgroundColour('RED')
            evt.Skip()
            
        except Exception,exc:
            logger.error(exc.message,exc_info=True)
            
             
    def setBarCode(self):
        
        barcode = self.barcode_text.GetValue().strip()
        out_sid = self.out_sid_text.GetValue().strip()
        
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
                    with create_session(self.Parent) as session: 
                        #库存减掉后，修改发货状态
                        session.query(MergeTrade).filter_by(id=self.trade.id,sys_status=cfg.SYS_STATUS_WAITSCANCHECK)\
                            .update({'sys_status':cfg.SYS_STATUS_WAITSCANWEIGHT},synchronize_session='fetch')
                    
                    if self.is_print_qrcode:
                        try:
                            self.directPrintYundaOrder(out_sid)
                        except Exception,exc:
                            dial = wx.MessageDialog(None, u'韵达二维码快递单打印出错:%s'%exc.message,u'快递单打印提示', 
                                                    wx.OK | wx.ICON_EXCLAMATION)
                            dial.ShowModal()
                            
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
   
    def onClickSaveBtn(self,evt):

        self.setBarCode()
            
    def onClickCancelBtn(self,evt):
        
        self.out_sid_text.Clear()
        self.barcode_text.Clear()
        self.out_sid_text.SetFocus()
    
    
    @property
    def is_print_qrcode(self):
        
        return self.print_qrcode_checkbox.IsChecked()
    
    @log_exception
    def directPrintYundaOrder(self,out_sid):
        """ 直接打印韵达二维码面单 """
        
        with create_session(self.Parent) as session:
            trade = session.query(MergeTrade).filter_by(out_sid=out_sid).first()
            yunda_lg = session.query(LogisticsCompany).filter_by(code='YUNDA').first()
            
            if trade.is_qrcode and trade.logistics_company_id == yunda_lg.id:
                #调用韵达打印接口并打印
                printYUNDAPDF([trade.id],direct=True,session=session)
        
