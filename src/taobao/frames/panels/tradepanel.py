#-*- coding:utf8 -*-
'''
Created on 2012-7-14

@author: user1
'''
import wx
from taobao.frames.panels.searchpanel import SearchPanel
from taobao.frames.panels.gridpanel import QueryObjectGridPanel
from taobao.dao import configparams as cfg
from taobao.dao.tradedao import is_normal_print_limit


all_trade_id = wx.NewId()
prapare_send_id  = wx.NewId()
check_barcode_id  = wx.NewId()
scan_weight_id = wx.NewId()
wait_delivery_id = wx.NewId()
sync_status_id = wx.NewId()
has_send_id   = wx.NewId()
audit_fail_id = wx.NewId()
invalid_id   = wx.NewId()
merge_rule_id = wx.NewId()
regular_remain_id = wx.NewId()
expand_id = wx.NewId()
fold_id = wx.NewId()
class TradePanel(wx.Panel):
    
    def __init__(self,parent,id=-1):
        wx.Panel.__init__(self,parent,id)
        
        self.Session = parent.Session
        self.selectedRowColour = (0, 128, 0, 255)
        self.search_panel = SearchPanel(self,-1)
        self.buttons = [] 
        
        for button in self.buttons_tuple:
            self.buttons.append(wx.Button(self,button[0],button[1]))
            
        self.normalradio = wx.RadioButton(self, -1, u'单打模式', pos=(20, 50),style=wx.RB_GROUP)
        self.dividradio  = wx.RadioButton(self, -1, u'分打模式', pos=(20, 50))  
  
        colLabels = (u'订单号',u'卖家昵称',u'买家昵称',u'订单类型',u'订单状态',u'系统状态',u'省-市-区',u'锁定',u'物流单',u'发货单',u'复审',
                     u'物流公司',u'物流单号',u'打单员',u'热敏打印信息',u'品类数',u'实付',u'总金额',u'扫描员',u'付款时间',u'发货时间',u'称重时间')
        self.grid = QueryObjectGridPanel(self,-1,rowLabels=None,colLabels=colLabels)
        self.grid.setDataSource(cfg.SYS_STATUS_PREPARESEND)
        
        self.static_button_up = wx.Button(self,-1,label='^------------^',size=(-1,11))
        self.isSearchPanelShow = False
        
        self.refresh_btn = wx.Button(self,-1,u'刷新',size=(35,23))
        self.colorpicker = wx.ColourPickerCtrl(self,-1) 
        
        self.__set_properties()
        self.__do_layout()   
        self.__evt_bind()
     
    @property 
    def buttons_tuple(self):
        return ((all_trade_id,u'全部',1),#1表示显示，0表示在隐藏域
                (prapare_send_id,u'待发货准备',1),
                (check_barcode_id,u'待扫描验货',1),
                (scan_weight_id,u'待扫描称重',1),
                (expand_id,'>>',2),
                (merge_rule_id,u'合并规则区',0),
                (regular_remain_id,u'定时处理区',0),
                (audit_fail_id,u'问题单',0),
                (has_send_id,u'已完成',0),
                (invalid_id,u'已作废',0),
                (fold_id,'<<',2),
                )
           
        
    def __set_properties(self):
        self.SetName('trade_panel') 
        self.FindWindowById(prapare_send_id).Enable(False)  
        self.refresh_btn.SetToolTip(wx.ToolTip(u'刷新当前表单'))
        self.colorpicker.SetToolTip(wx.ToolTip(u'设置选中行颜色'))
        
        self.search_panel.Hide()
        for button in self.buttons_tuple:
            if button[2] == 0:
                self.FindWindowById(button[0]).Hide()
        self.FindWindowById(fold_id).Hide()
    
    def __do_layout(self):  
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.search_panel,flag=wx.EXPAND)
         
        main_sizer.Add(self.static_button_up,flag=wx.EXPAND)
        self.trade_naming_sizer =trade_naming_sizer = wx.FlexGridSizer(hgap=2,vgap=2)
        
        for index,button in enumerate(self.buttons_tuple):
            trade_naming_sizer.Add(self.FindWindowById(button[0]),0,index)
        
        trade_naming_sizer.Add((250,-1))
  
        trade_naming_sizer.Add(self.normalradio,0,index+1)
        trade_naming_sizer.Add(self.dividradio,0,index+2)
        trade_naming_sizer.Add((10,-1))
        trade_naming_sizer.Add(self.refresh_btn,0,index+4)
        trade_naming_sizer.Add(self.colorpicker,0,index+5)
        
        main_sizer.Add(trade_naming_sizer,flag=wx.EXPAND)
        main_sizer.Add(self.grid,1,flag=wx.EXPAND)
        main_sizer.Layout()
        self.search_panel.Layout()
        self.SetSizer(main_sizer)
        
        
    def __evt_bind(self):
        for button in self.buttons_tuple:
            if button[2] in (0,1):
                self.Bind(wx.EVT_BUTTON,self.onClickGridBtn,self.FindWindowById(button[0])) 
            elif button[2] == 2:
                self.Bind(wx.EVT_BUTTON,self.onClickExpandFoldBtn,self.FindWindowById(button[0]))   
                
        self.Bind(wx.EVT_BUTTON,self.onClickStaticButton,self.static_button_up)
        self.Bind(wx.EVT_BUTTON, self.onClickRefreshBtn,self.refresh_btn)
        self.Bind(wx.EVT_COLOURPICKER_CHANGED, self.onClickColorPickerChange,self.colorpicker)
        
        self.Bind(wx.EVT_RADIOBUTTON, self.onSelectRadioBtn, self.normalradio)
        self.Bind(wx.EVT_RADIOBUTTON, self.onSelectRadioBtn, self.dividradio)
            
    def onClickExpandFoldBtn(self,evt):
        eventid = evt.GetId()
        if eventid == expand_id:
            for button in self.buttons_tuple:
                if button[2] == 0:
                    self.FindWindowById(button[0]).Show()
            self.FindWindowById(expand_id).Hide() 
            self.FindWindowById(fold_id).Show()     
        elif eventid == fold_id:
            for button in self.buttons_tuple:
                if button[2] == 0:
                    self.FindWindowById(button[0]).Hide() 
            self.FindWindowById(fold_id).Hide()
            self.FindWindowById(expand_id).Show()
        self.Layout()

            
    def onClickGridBtn(self,evt):
        eventid = evt.GetId()
        if eventid == all_trade_id:
            trades_status_type = cfg.SYS_STATUS_ALL
        elif eventid == prapare_send_id:
            trades_status_type = cfg.SYS_STATUS_PREPARESEND 
        elif eventid == check_barcode_id:
            trades_status_type = cfg.SYS_STATUS_WAITSCANCHECK      
        elif eventid == scan_weight_id:
            trades_status_type = cfg.SYS_STATUS_WAITSCANWEIGHT  
        elif eventid == has_send_id:
            trades_status_type = cfg.SYS_STATUS_FINISHED 
        elif eventid == audit_fail_id:
            trades_status_type = cfg.SYS_STATUS_WAITAUDIT  
        elif eventid == invalid_id:
            trades_status_type = cfg.SYS_STATUS_INVALID
        elif eventid == merge_rule_id:
            trades_status_type = cfg.SYS_STATUS_ON_THE_FLY
        elif eventid == regular_remain_id:
            trades_status_type = cfg.SYS_STATUS_REGULAR_REMAIN 
            
        for button in self.buttons:
            button.Enable(not eventid==button.GetId())
        self.grid.setDataSource(trades_status_type)
        self.Layout()
    
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
    
    def onClickColorPickerChange(self,evt):
        self.selectedRowColour = evt.GetColour()
        self.grid.refreshTable()
    
    def onClickRefreshBtn(self,evt):
        self.grid.refreshTable()   
    
    def onSelectRadioBtn(self,evt):
        print_mode = self.getPrintMode()
        normal_print_limit = is_normal_print_limit(session=self.Session)
        is_auto_incr = normal_print_limit or (print_mode == cfg.DIVIDE_MODE) 
        self.grid.enableAutoIncrSidBtn(is_auto_incr)
        self.grid.setDataSource(self.grid.status_type)
        
    def getPrintMode(self):
        if self.normalradio.GetValue():
            return cfg.NORMAL_MODE
        else:
            return cfg.DIVIDE_MODE

        
    
