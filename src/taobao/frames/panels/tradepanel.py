#-*- coding:utf8 -*-
'''
Created on 2012-7-14

@author: user1
'''
import wx
from taobao.dao.models import MergeTrade
from taobao.frames.panels.searchpanel import SearchPanel
from taobao.frames.panels.gridpanel import QueryObjectGridPanel
from taobao.dao.configparams import SYS_STATUS_ALL,SYS_STATUS_UNAUDIT,SYS_STATUS_AUDITFAIL,SYS_STATUS_PREPARESEND,\
    SYS_STATUS_SCANWEIGHT,SYS_STATUS_CONFIRMSEND,SYS_STATUS_FINISHED,SYS_STATUS_INVALID,SYS_STATUS_SYSTEMSEND


all_trade_id = wx.NewId()
wait_audit_id = wx.NewId()
prapare_send_id  = wx.NewId()
scan_weight_id = wx.NewId()
wait_delivery_id = wx.NewId()
sync_status_id = wx.NewId()
has_send_id   = wx.NewId()
audit_fail_id = wx.NewId()
invalid_id   = wx.NewId()
class TradePanel(wx.Panel):
    
    def __init__(self,parent,id=-1):
        wx.Panel.__init__(self,parent,id)
        
        self.session = session = parent.session
        self.search_panel = SearchPanel(self,-1)
        
        self.all_trade_btn = wx.Button(self,all_trade_id,'全部')
        self.wait_audit_btn = wx.Button(self,wait_audit_id,'待审核',)
        self.prapare_send_btn = wx.Button(self,prapare_send_id,'待发货准备',)
        self.scan_weight_btn = wx.Button(self,scan_weight_id,'待扫描称重')
        self.wait_delivery_btn = wx.Button(self,wait_delivery_id,'待确认发货')
        self.sync_status_btn = wx.Button(self,sync_status_id,'待更新发货状态')
        self.has_send_btn = wx.Button(self,has_send_id,'已发货')
        self.audit_fail_btn = wx.Button(self,audit_fail_id,'审核未通过')
        self.invalid_btn = wx.Button(self,invalid_id,'已作废')

        self.datasource = session.query(MergeTrade)
        trades  = self.datasource.filter_by(sys_status=SYS_STATUS_UNAUDIT)   
        colLabels = ('订单号','卖家昵称','买家昵称','订单类型','订单状态','系统状态','物流类型','有退款','打印发货单','打印物流单','短信提醒','物流公司','物流单号',
                     '实付','邮费','总金额','商品数量','优惠金额','调整金额','付款时间','发货时间','反审核次数')
        self.grid = QueryObjectGridPanel(self,rowLabels=None,colLabels=colLabels)
        trades.status_type = SYS_STATUS_UNAUDIT
        self.grid.setDataSource(trades)
        
        self.static_button_up = wx.Button(self,-1,label='^------------^',size=(-1,11))
        self.isSearchPanelShow = True
        
        self.__set_properties()
        self.__do_layout()   
        self.__evt_bind()
        
        
    def __set_properties(self):
        self.SetName('trade_panel') 
        self.wait_audit_btn.Enable(False)    
        
    def __do_layout(self):  
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.search_panel,flag=wx.EXPAND)
         
        main_sizer.Add(self.static_button_up,flag=wx.EXPAND)
        trade_naming_sizer = wx.FlexGridSizer(hgap=2,vgap=2)
        trade_naming_sizer.Add(self.all_trade_btn,0,0)
        trade_naming_sizer.Add(self.wait_audit_btn,0,1)
        trade_naming_sizer.Add(self.prapare_send_btn,0,2)
        trade_naming_sizer.Add(self.scan_weight_btn,0,3)
        trade_naming_sizer.Add(self.wait_delivery_btn,0,4)
        trade_naming_sizer.Add(self.sync_status_btn,0,6)
        trade_naming_sizer.Add(self.has_send_btn,0,6)
        trade_naming_sizer.Add(self.audit_fail_btn,0,7)
        trade_naming_sizer.Add(self.invalid_btn,0,8)
        main_sizer.Add(trade_naming_sizer,flag=wx.EXPAND)
        main_sizer.Add(self.grid,1,flag=wx.EXPAND)
        main_sizer.Layout()
        self.search_panel.Layout()
        self.SetSizer(main_sizer)
        
        
    def __evt_bind(self):
        self.Bind(wx.EVT_BUTTON,self.onClickGridBtn,self.all_trade_btn)
        self.Bind(wx.EVT_BUTTON,self.onClickGridBtn,self.wait_audit_btn)
        self.Bind(wx.EVT_BUTTON,self.onClickGridBtn,self.prapare_send_btn)
        self.Bind(wx.EVT_BUTTON,self.onClickGridBtn,self.scan_weight_btn)
        self.Bind(wx.EVT_BUTTON,self.onClickGridBtn,self.wait_delivery_btn)
        self.Bind(wx.EVT_BUTTON,self.onClickGridBtn,self.sync_status_btn)
        self.Bind(wx.EVT_BUTTON,self.onClickGridBtn,self.has_send_btn)
        self.Bind(wx.EVT_BUTTON,self.onClickGridBtn,self.audit_fail_btn)
        self.Bind(wx.EVT_BUTTON,self.onClickGridBtn,self.invalid_btn)
        
        self.Bind(wx.EVT_BUTTON,self.onClickStaticButton,self.static_button_up)
     
        
    def onClickGridBtn(self,evt):
        eventid = evt.GetId()
        if eventid == all_trade_id:
            trades = self.datasource
            trades.status_type = SYS_STATUS_ALL
        elif eventid == wait_audit_id:
            trades = self.datasource.filter_by(sys_status=SYS_STATUS_UNAUDIT)
            trades.status_type = SYS_STATUS_UNAUDIT 
        elif eventid == prapare_send_id:
            trades = self.datasource.filter_by(sys_status=SYS_STATUS_PREPARESEND)
            trades.status_type = SYS_STATUS_PREPARESEND       
        elif eventid == scan_weight_id:
            trades = self.datasource.filter_by(sys_status=SYS_STATUS_SCANWEIGHT)
            trades.status_type = SYS_STATUS_SCANWEIGHT  
        elif eventid == wait_delivery_id:
            trades = self.datasource.filter_by(sys_status=SYS_STATUS_CONFIRMSEND)
            trades.status_type = SYS_STATUS_CONFIRMSEND  
        elif eventid == sync_status_id:
            trades = self.datasource.filter_by(sys_status=SYS_STATUS_SYSTEMSEND) 
            trades.status_type = SYS_STATUS_SYSTEMSEND
        elif eventid == has_send_id:
            trades = self.datasource.filter_by(sys_status=SYS_STATUS_FINISHED) 
            trades.status_type = SYS_STATUS_FINISHED 
        elif eventid == audit_fail_id:
            trades = self.datasource.filter_by(sys_status=SYS_STATUS_AUDITFAIL)
            trades.status_type = SYS_STATUS_AUDITFAIL  
        elif eventid == invalid_id:
            trades = self.datasource.filter_by(sys_status=SYS_STATUS_INVALID) 
            trades.status_type = SYS_STATUS_INVALID 

        self.all_trade_btn.Enable(not eventid==all_trade_id)
        self.wait_audit_btn.Enable(not eventid==wait_audit_id)
        self.prapare_send_btn.Enable(not eventid==prapare_send_id)
        self.scan_weight_btn.Enable(not eventid==scan_weight_id)
        self.wait_delivery_btn.Enable(not eventid==wait_delivery_id)
        self.sync_status_btn.Enable(not eventid==sync_status_id)
        self.has_send_btn.Enable(not eventid==has_send_id)
        self.audit_fail_btn.Enable(not eventid==audit_fail_id)
        self.invalid_btn.Enable(not eventid==invalid_id)
              
        self.grid.setDataSource(trades)
    
    def onClickStaticButton(self,evt):
        if self.isSearchPanelShow:
            self.search_panel.Hide()
            self.static_button_up.SetLabel('v------------v')
            self.isSearchPanelShow = False
        else:
            self.search_panel.Show()
            self.static_button_up.SetLabel('^------------^')
            self.isSearchPanelShow = True
        self.Layout() 
        

        
