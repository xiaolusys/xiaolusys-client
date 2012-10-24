#-*- coding:utf8 -*-
'''
Created on 2012-7-27

@author: user1
'''
import re
import weakref
import wx,wx.grid
from taobao.common.utils import create_session
from taobao.dao.models import MergeTrade,LogisticsCompany
from taobao.frames.panels.gridpanel import WeightGridPanel
from taobao.dao.configparams import TRADE_TYPE,TRADE_STATUS,SHIPPING_TYPE,SYS_STATUS,SYS_STATUS_FINISHED,\
    SYS_STATUS_INVALID,TRADE_STATUS_WAIT_SEND_GOODS,SYS_STATUS_WAITSCANWEIGHT

weight_regex=re.compile('[0-9\.]{1,7}$')

class ScanWeightPanel(wx.Panel):
    
    def __init__(self,parent,id=-1):
        wx.Panel.__init__(self,parent,id)
        
        self.Session = parent.Session
        self.is_auto_save = False
        self.trade = None
        self.company_label = wx.StaticText(self,-1,'快递公司')
        self.company_select = wx.ComboBox(self,-1)
        self.out_sid_label = wx.StaticText(self,-1,'快递单号')
        self.out_sid_text  = wx.TextCtrl(self,-1,style=wx.TE_PROCESS_ENTER)
        self.weight_label  = wx.StaticText(self,-1,'称重重量(g)')
        self.weight_text  = wx.TextCtrl(self,-1,style=wx.TE_PROCESS_ENTER)
        self.auto_add_label  = wx.StaticText(self,-1,'自动保存') 
        self.auto_add_checkbox = wx.CheckBox(self,-1)
        self.hand_add_button   = wx.Button(self,-1,'保存') 
        self.cancel_button   = wx.Button(self,-1,'取消')
        
        self.error_text = wx.StaticText(self,-1)
        
        self.order_label1  = wx.StaticText(self,-1,'店铺简称')
        self.order_content1  = wx.TextCtrl(self,-1)
        self.order_label2  = wx.StaticText(self,-1,'来源单号')
        self.order_content2  = wx.TextCtrl(self,-1)
        self.order_label3  = wx.StaticText(self,-1,'订单类型')
        self.order_content3  = wx.TextCtrl(self,-1)
        self.order_label4  = wx.StaticText(self,-1,'会员名称')
        self.order_content4  = wx.TextCtrl(self,-1)
        self.order_label5  = wx.StaticText(self,-1,'快递公司')
        self.order_content5  = wx.TextCtrl(self,-1)     
        self.order_label6  = wx.StaticText(self,-1,'快递单号')
        self.order_content6  = wx.TextCtrl(self,-1) 

        
        self.order_label7  = wx.StaticText(self,-1,'订单状态')
        self.order_content7  = wx.TextCtrl(self,-1)
        self.order_label8  = wx.StaticText(self,-1,'系统状态')
        self.order_content8  = wx.TextCtrl(self,-1)
        self.order_label9  = wx.StaticText(self,-1,'收货人')
        self.order_content9  = wx.TextCtrl(self,-1)
        self.order_label10  = wx.StaticText(self,-1,'物流类型')
        self.order_content10  = wx.TextCtrl(self,-1)
        self.order_label11  = wx.StaticText(self,-1,'实付邮费')
        self.order_content11  = wx.TextCtrl(self,-1)
        self.order_label12  = wx.StaticText(self,-1,'收货人固定电话')
        self.order_content12  = wx.TextCtrl(self,-1,'') 
        
        self.order_label13  = wx.StaticText(self,-1,'收货人手机')
        self.order_content13  = wx.TextCtrl(self,-1) 
        self.order_label14  = wx.StaticText(self,-1,'收货邮编')
        self.order_content14  = wx.TextCtrl(self,-1)
        self.order_label15  = wx.StaticText(self,-1,'所在省')
        self.order_content15  = wx.TextCtrl(self,-1)
        self.order_label16  = wx.StaticText(self,-1,'所在市')
        self.order_content16  = wx.TextCtrl(self,-1)
        self.order_label17  = wx.StaticText(self,-1,'所在地区')
        self.order_content17  = wx.TextCtrl(self,-1)
        self.order_label18  = wx.StaticText(self,-1,'收货地址')
        self.order_content18  = wx.TextCtrl(self,-1,size=(150,-1))
        
        self.order_box1 = wx.StaticBox(self,-1,'扫描订单详细信息')
        
        self.gridpanel = WeightGridPanel(self,-1)
        
        self.order_box2 = wx.StaticBox(self,-1,'已称重订单列表')

        self.__set_properties()
        self.__do_layout()
        self.__evt_bind()
    
    
    def __set_properties(self):
        self.SetName('weight panel')
        
        with create_session(self.Parent) as session: 
            logistics_companies = session.query(LogisticsCompany).order_by('priority desc').all()
        self.company_select.AppendItems([company.name for company in logistics_companies])
        self.out_sid_text.SetFocus()
        
        self.control_array = []
        self.control_array.append(self.order_content1)
        self.control_array.append(self.order_content2)
        self.control_array.append(self.order_content3)
        self.control_array.append(self.order_content4)
        self.control_array.append(self.order_content5)
        self.control_array.append(self.order_content6)
        
        self.control_array.append(self.order_content7)
        self.control_array.append(self.order_content8)
        self.control_array.append(self.order_content9)
        self.control_array.append(self.order_content10)
        self.control_array.append(self.order_content11)
        self.control_array.append(self.order_content12)
        
        self.control_array.append(self.order_content13)
        self.control_array.append(self.order_content14)
        self.control_array.append(self.order_content15)
        self.control_array.append(self.order_content16)
        self.control_array.append(self.order_content17)
        self.control_array.append(self.order_content18)
        
        for control in self.control_array:
            control.Enable(False)
            
        self.out_sid_text.SetFocus()
    
    def __do_layout(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        flex_sizer1 = wx.FlexGridSizer(hgap=5,vgap=5)
        flex_sizer1.Add(self.company_label,0,0)
        flex_sizer1.Add(self.company_select,0,1)
        flex_sizer1.Add(self.out_sid_label,0,2)
        flex_sizer1.Add(self.out_sid_text,0,3)
        flex_sizer1.Add(self.weight_label,0,4)
        flex_sizer1.Add(self.weight_text,0,5)

        flex_sizer1.Add(self.auto_add_label,0,8)
        flex_sizer1.Add(self.auto_add_checkbox,0,9)
        flex_sizer1.Add(self.hand_add_button,0,10)
        flex_sizer1.Add(self.cancel_button,0,11)
        flex_sizer1.Add(self.error_text,0,12)
        
        sbsizer1 = wx.StaticBoxSizer(self.order_box1,wx.VERTICAL)
        bag_sizer1 = wx.GridBagSizer(hgap=5,vgap=5)
        bag_sizer1.Add(self.order_label1,pos=(0,0),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_content1,pos=(0,1),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_label2,pos=(0,2),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_content2,pos=(0,3),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_label3,pos=(0,4),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_content3,pos=(0,5),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_label4,pos=(0,6),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_content4,pos=(0,7),span=(1,1),flag=wx.EXPAND)   
        bag_sizer1.Add(self.order_label5,pos=(0,8),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_content5,pos=(0,9),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_label6,pos=(0,10),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_content6,pos=(0,11),span=(1,1),flag=wx.EXPAND)
        
        bag_sizer1.Add(self.order_label7,pos=(1,0),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_content7,pos=(1,1),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_label8,pos=(1,2),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_content8,pos=(1,3),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_label9,pos=(1,4),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_content9,pos=(1,5),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_label10,pos=(1,6),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_content10,pos=(1,7),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_label11,pos=(1,8),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_content11,pos=(1,9),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_label12,pos=(1,10),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_content12,pos=(1,11),span=(1,1),flag=wx.EXPAND)
        
        bag_sizer1.Add(self.order_label13,pos=(2,0),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_content13,pos=(2,1),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_label14,pos=(2,2),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_content14,pos=(2,3),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_label15,pos=(2,4),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_content15,pos=(2,5),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_label16,pos=(2,6),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_content16,pos=(2,7),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_label17,pos=(2,8),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_content17,pos=(2,9),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_label18,pos=(2,10),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_content18,pos=(2,11),span=(1,1),flag=wx.EXPAND)
        
        sbsizer1.Add(bag_sizer1,proportion=0,flag=wx.EXPAND,border=10)
        
        sbsizer2=wx.StaticBoxSizer(self.order_box2,wx.VERTICAL)
        sbsizer2.Add(self.gridpanel,proportion=1,flag=wx.EXPAND,border=10) 
        
        main_sizer.Add(flex_sizer1,flag=wx.EXPAND)
        main_sizer.Add(sbsizer1,flag=wx.EXPAND)
        main_sizer.Add(sbsizer2,-1,flag=wx.EXPAND)
        self.SetSizer(main_sizer)
        self.Layout()
        
    def __evt_bind(self):
        
        self.Bind(wx.EVT_COMBOBOX, self.onComboboxSelect, self.company_select)
        self.Bind(wx.EVT_TEXT_ENTER, self.onOutsidTextChange,self.out_sid_text)
        self.Bind(wx.EVT_TEXT_ENTER, self.onWeightTextChange,self.weight_text)
        self.Bind(wx.EVT_CHECKBOX, self.onClickCheckBox, self.auto_add_checkbox)
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
                         logistics_company_id=logistics_company.id,status=TRADE_STATUS_WAIT_SEND_GOODS)
        count = trades.count() if trades else 0   
        if count>1 :
            self.error_text.SetLabel('该快递单号已重复，请反审核后修改')
            self.error_text.SetForegroundColour('black')
            self.error_text.SetBackgroundColour('red')
        elif count == 1:
            self.trade = trades.one()
            self.setTradeInfoPanel(self.trade)
            self.weight_text.SetFocus()
            self.error_text.SetLabel('')
        else:
            self.error_text.SetLabel('未找到该订单')
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
                       logistics_company_id=logistics_company.id,status=TRADE_STATUS_WAIT_SEND_GOODS)
            elif out_sid :
                trades = session.query(MergeTrade).filter_by(out_sid=out_sid,status=TRADE_STATUS_WAIT_SEND_GOODS)
                 
        count = trades.count() if trades else 0 
        if count>1 :
            self.error_text.SetLabel('该快递单号已重复，请反审核后修改')
            self.error_text.SetForegroundColour('black')
            self.error_text.SetBackgroundColour('red')
            self.clearTradeInfoPanel()
        elif count == 1:
            self.trade = trades.one()
            self.setTradeInfoPanel(self.trade)
            self.weight_text.SetFocus()
            self.error_text.SetLabel('')
            self.error_text.SetForegroundColour('white')
            self.error_text.SetBackgroundColour('black')
        else:
            self.error_text.SetLabel('未找到该订单')
            self.error_text.SetForegroundColour('black')
            self.error_text.SetBackgroundColour('red')
            self.clearTradeInfoPanel()
        evt.Skip()
        
    def clearTradeInfoPanel(self):
        for i in xrange(1,19):
            content = eval('self.order_content%s'%str(i))
            content.Clear()    
        
    def setTradeInfoPanel(self,trade):
 
        self.order_content1.SetValue(trade.seller_nick)
        self.order_content2.SetValue(str(trade.tid))
        self.order_content3.SetValue(TRADE_TYPE.get(trade.type,'其他'))
        self.order_content4.SetValue(trade.buyer_nick)
        self.order_content5.SetValue(trade.logistics_company.name)
        self.order_content6.SetValue(trade.out_sid)
        
        self.order_content7.SetValue(TRADE_STATUS.get(trade.status,'其他'))
        self.order_content8.SetValue(SYS_STATUS.get(trade.sys_status,'其他'))
        self.order_content9.SetValue(trade.receiver_name)
        self.order_content10.SetValue(SHIPPING_TYPE.get(trade.shipping_type,'其他'))
        self.order_content11.SetValue(trade.post_fee)
        self.order_content12.SetValue(trade.receiver_phone)
        
        self.order_content13.SetValue(trade.receiver_mobile)
        self.order_content14.SetValue(trade.receiver_zip)
        self.order_content15.SetValue(trade.receiver_state)
        self.order_content16.SetValue(trade.receiver_city)
        self.order_content17.SetValue(trade.receiver_district)
        self.order_content18.SetValue(trade.receiver_address)
        
        self.Layout()
        
    def onWeightTextChange(self,evt):
        weight = self.weight_text.GetValue().strip()
        if weight_regex.match(weight) and self.trade and self.is_auto_save:
            self.save_weight_to_trade(self.trade,weight)
            self.weight_text.Clear()
            self.out_sid_text.Clear()
            self.out_sid_text.SetFocus()
        
    def save_weight_to_trade(self,trade,weight):
        with create_session(self.Parent) as session: 
            session.query(MergeTrade).filter_by(id=trade.id,sys_status=SYS_STATUS_WAITSCANWEIGHT)\
                    .update({'weight':weight,'sys_status':SYS_STATUS_FINISHED},synchronize_session='fetch')
        self.gridpanel.InsertTradeRows(trade)
    
        
    def onClickCheckBox(self,evt):
        self.is_auto_save = evt.IsChecked()
        
        
    def onClickSaveBtn(self,evt):
        weight = self.weight_text.GetValue()
        if self.trade and weight:
            self.save_weight_to_trade(self.trade,weight)
            
    
    def onClickCancelBtn(self,evt):
        self.out_sid_text.Clear()
        self.weight_text.Clear()
        for control in self.control_array:
            control.Clear()
   
     
                 