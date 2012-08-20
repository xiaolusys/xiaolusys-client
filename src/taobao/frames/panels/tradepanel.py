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
        
        self.Session = parent.Session
        self.selectedRowColour = (0, 128, 0, 255)
        self.selecttailnums  = set()
        self.search_panel = SearchPanel(self,-1)
             
        self.buttons = [] 
        
        for button in self.buttons_tuple:
            self.buttons.append(wx.Button(self,button[0],button[1]))
 
        colLabels = ('订单号','卖家昵称','买家昵称','订单类型','订单状态','系统状态','物流类型','有退款','打印发货单','打印物流单','短信提醒','物流公司','物流单号',
                     '实付','邮费','总金额','商品数量','优惠金额','调整金额','付款时间','发货时间','反审核次数')
        self.grid = QueryObjectGridPanel(self,rowLabels=None,colLabels=colLabels)
        self.grid.setDataSource(SYS_STATUS_UNAUDIT)
        
        self.static_button_up = wx.Button(self,-1,label='^------------^',size=(-1,11))
        self.isSearchPanelShow = True
        self.istailnumshow = False
        
        self.filter_number_btn = wx.Button(self,-1,'>',size=(23,23)) 
        self.colorpicker = wx.ColourPickerCtrl(self,-1)
   
        self.__set_properties()
        self.__do_layout()   
        self.__evt_bind()
     
    @property 
    def buttons_tuple(self):
        return ((all_trade_id,'全部'),
                (wait_audit_id,'待审核'),
                (prapare_send_id,'待发货准备'),
                (scan_weight_id,'待扫描称重'),
                (wait_delivery_id,'待确认发货'),
                (has_send_id,'已发货'),
                (audit_fail_id,'问题单'),
                (invalid_id,'已作废'),
                )
           
        
    def __set_properties(self):
        self.SetName('trade_panel') 
        self.FindWindowById(wait_audit_id).Enable(False)  
        self.colorpicker.SetToolTip(wx.ToolTip('设置选中行颜色'))
        self.filter_number_btn.SetToolTip(wx.ToolTip('选择显示的订单尾号'))  
        
    def __do_layout(self):  
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.search_panel,flag=wx.EXPAND)
         
        main_sizer.Add(self.static_button_up,flag=wx.EXPAND)
        self.trade_naming_sizer =trade_naming_sizer = wx.FlexGridSizer(hgap=2,vgap=2)
        
        for index,button in enumerate(self.buttons_tuple):
            trade_naming_sizer.Add(self.FindWindowById(button[0]),0,index)
        
        trade_naming_sizer.Add((150,-1))
        
        self.checksizer = wx.FlexGridSizer(hgap=2,vgap=10)
        self.checkbox_list = []
        for i in xrange(0,10):
            check = wx.CheckBox(self,-1,str(i))
            self.checkbox_list.append(check)
            self.checksizer.Add(check,0,i)
        trade_naming_sizer.Add(self.colorpicker,0,index+1)
        trade_naming_sizer.Add(self.filter_number_btn,0,index+2)
        trade_naming_sizer.Add(self.checksizer,0,index+3)
        trade_naming_sizer.Hide(self.checksizer)
        
        main_sizer.Add(trade_naming_sizer,flag=wx.EXPAND)
        main_sizer.Add(self.grid,1,flag=wx.EXPAND)
        main_sizer.Layout()
        self.search_panel.Layout()
        self.SetSizer(main_sizer)
        
        
    def __evt_bind(self):
        for button in self.buttons_tuple:
            self.Bind(wx.EVT_BUTTON,self.onClickGridBtn,self.FindWindowById(button[0]))    
        self.Bind(wx.EVT_BUTTON,self.onClickStaticButton,self.static_button_up)
        
        self.Bind(wx.EVT_COLOURPICKER_CHANGED, self.onClickColorPickerChange,self.colorpicker)
        self.Bind(wx.EVT_BUTTON, self.onClickTailNumBtn,self.filter_number_btn)
        for checkbox in self.checkbox_list:
            self.Bind(wx.EVT_CHECKBOX, self.onCheckTailNum,checkbox)
            
        
         
    def onClickGridBtn(self,evt):
        eventid = evt.GetId()
        if eventid == all_trade_id:
            trades_status_type = SYS_STATUS_ALL
        elif eventid == wait_audit_id:
            trades_status_type = SYS_STATUS_UNAUDIT 
        elif eventid == prapare_send_id:
            trades_status_type = SYS_STATUS_PREPARESEND       
        elif eventid == scan_weight_id:
            trades_status_type = SYS_STATUS_SCANWEIGHT  
        elif eventid == wait_delivery_id:
            trades_status_type = SYS_STATUS_CONFIRMSEND  
        elif eventid == sync_status_id: 
            trades_status_type = SYS_STATUS_SYSTEMSEND
        elif eventid == has_send_id:
            trades_status_type = SYS_STATUS_FINISHED 
        elif eventid == audit_fail_id:
            trades_status_type = SYS_STATUS_AUDITFAIL  
        elif eventid == invalid_id:
            trades_status_type = SYS_STATUS_INVALID 
            
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
        
    def onCheckTailNum(self,evt):
        source = evt.GetEventObject()
        if evt.IsChecked():
            self.selecttailnums.add(int(source.GetLabelText()))
        else :
            try:
                self.selecttailnums.remove(int(source.GetLabelText()))
            except:
                pass
        self.grid.updateTableAndPaginator()

        
    def onClickTailNumBtn(self,evt):
        if self.istailnumshow:
            self.trade_naming_sizer.Hide(self.checksizer)
            self.istailnumshow = False
        else:
            self.trade_naming_sizer.Show(self.checksizer)
            self.istailnumshow = True
        self.Layout()
        
