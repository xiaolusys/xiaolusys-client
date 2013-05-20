#-*- coding:utf8 -*-
'''
Created on 2012-7-27
  快递揽件单号确认及生成揽件信息报表
@author: user1
'''
import re
import winsound
import weakref
import datetime
import wx,wx.grid
from taobao.common.utils import create_session,MEDIA_ROOT
from taobao.dao.models import MergeTrade,LogisticsCompany,MergeOrder,Product,ProductSku
from taobao.frames.panels.gridpanel import ChargeGridPanel
from taobao.dao.tradedao import get_used_orders,get_return_orders
from taobao.common.utils import getconfig,pydate2wxdate,wxdate2pydate
from taobao.dao import configparams as cfg
    

class ScanChargePanel(wx.Panel):
    
    def __init__(self,parent,id=-1):
        wx.Panel.__init__(self,parent,id)
        self.Session = parent.Session

        self.company_label = wx.StaticText(self,-1,u'快递公司')
        self.company_select = wx.ComboBox(self,-1)
        self.out_sid_label = wx.StaticText(self,-1,u'快递单号')
        self.out_sid_text  = wx.TextCtrl(self,-1,style=wx.TE_PROCESS_ENTER)
        
        self.charge_start_label = wx.StaticText(self,-1,u'揽件日期起')
        self.charge_start_select = wx.DatePickerCtrl(self,
                                style = wx.DP_DROPDOWN| wx.DP_SHOWCENTURY| wx.DP_ALLOWNONE)
        self.charge_end_label = wx.StaticText(self,-1,u'揽件日期止')
        self.charge_end_select =  wx.DatePickerCtrl(self,
                                style = wx.DP_DROPDOWN| wx.DP_SHOWCENTURY| wx.DP_ALLOWNONE)

        self.export_btn   = wx.Button(self,-1,u'导出文件') 
        
        self.gridpanel = ChargeGridPanel(self,-1)
 
        self.logistic_box2 = wx.StaticBox(self,-1,u'物流单信息列表')

        self.__set_properties()
        self.__do_layout()
        self.__evt_bind()
    
    
    def __set_properties(self):
        self.SetName('charge panel')
        
        with create_session(self.Parent) as session: 
            logistics_companies = session.query(LogisticsCompany).filter_by(status=True).order_by('priority desc').all()
        self.company_select.AppendItems([company.name for company in logistics_companies])
        self.company_select.SetFocus()
        
        self.charge_start_select.SetValue(pydate2wxdate(datetime.datetime.now()))
        self.out_sid_text.Enable(False)
    
    def __do_layout(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        flex_sizer1 = wx.FlexGridSizer(hgap=5,vgap=5)
        flex_sizer1.Add(self.company_label,0,0)
        flex_sizer1.Add(self.company_select,0,1)
        flex_sizer1.Add((10,-1))
        flex_sizer1.Add(self.out_sid_label,0,2)
        flex_sizer1.Add(self.out_sid_text,0,3)
        flex_sizer1.Add((10,-1))
        flex_sizer1.Add(self.charge_start_label,0,4)
        flex_sizer1.Add(self.charge_start_select,0,5)
        flex_sizer1.Add(self.charge_end_label,0,6)
        flex_sizer1.Add(self.charge_end_select,0,7)
        flex_sizer1.Add((60,-1))
        flex_sizer1.Add(self.export_btn,0,8)
        
        sbsizer2=wx.StaticBoxSizer(self.logistic_box2,wx.VERTICAL)
        sbsizer2.Add(self.gridpanel,proportion=1,flag=wx.EXPAND,border=10) 
        
        main_sizer.Add(flex_sizer1,flag=wx.EXPAND)
        main_sizer.Add(sbsizer2,-1,flag=wx.EXPAND)
        self.SetSizer(main_sizer)
        self.Layout()
        
    def __evt_bind(self):
        
        self.Bind(wx.EVT_COMBOBOX, self.onComboboxSelect, self.company_select)
        self.Bind(wx.EVT_TEXT_ENTER, self.onOutsidTextChange,self.out_sid_text)
        self.Bind(wx.EVT_DATE_CHANGED, self.onComboboxSelect, self.charge_start_select)
        self.Bind(wx.EVT_DATE_CHANGED, self.onComboboxSelect, self.charge_end_select)
        
        self.Bind(wx.EVT_BUTTON, self.onClickOnLogisticBtn, self.export_btn)

    
    def onComboboxSelect(self,evt):
        
        company_name      = self.company_select.GetValue().strip()
        charge_start_date = self.charge_start_select.GetValue()
        charge_end_date   = self.charge_end_select.GetValue()
        
        dt  = datetime.datetime.now()
        charge_start_date = wxdate2pydate(charge_start_date) or dt.date()
        charge_end_date = wxdate2pydate(charge_end_date)

        self.out_sid_text.Enable(charge_start_date.day==dt.day)
        if (dt.date()-charge_start_date).days>7:    
            dial = wx.MessageDialog(None, u'查询日期须在7日内', u'快递揽件信息确认提示', 
                            wx.OK | wx.ICON_EXCLAMATION)
            dial.ShowModal()
            return 
            
        with create_session(self.Parent) as session:    
            logistics_company = session.query(LogisticsCompany).filter_by(name=company_name).first()
            if not logistics_company:    
                dial = wx.MessageDialog(None, u'未找到快递信息', u'快递揽件信息确认提示', 
                                wx.OK | wx.ICON_EXCLAMATION)
                dial.ShowModal()
                return
            charge_trades = session.query(MergeTrade).filter_by(is_picking_print=True,is_express_print=True,
                        logistics_company_id=logistics_company.id,sys_status=cfg.SYS_STATUS_FINISHED,is_charged=True)
            
            if charge_start_date:
                charge_trades = charge_trades.filter("charge_time >=:start").params(start=charge_start_date)

            if charge_end_date:
                charge_trades = charge_trades.filter("charge_time <=:end").params(end=charge_end_date)
            
        datasource = self.get_datasource_by_trades(charge_trades)    
        self.set_datasource(datasource)
        
        evt.Skip()
        
            
    def onOutsidTextChange(self,evt):
        company_name = self.company_select.GetValue().strip()
        out_sid      = self.out_sid_text.GetValue().strip() 
        trades = None
        with create_session(self.Parent) as session:
            if company_name and out_sid:
                logistics_company = session.query(LogisticsCompany).filter_by(name=company_name).first()
                trades = session.query(MergeTrade).filter_by(out_sid=out_sid,is_picking_print=True,
                        is_express_print=True,logistics_company_id=logistics_company.id,sys_status=cfg.SYS_STATUS_FINISHED)
                 
        count = trades.count() if trades else 0 
        if count>1 :
            dial = wx.MessageDialog(None, u'快递单号有重单，请联系管理员', u'快递揽件信息确认提示', 
                            wx.OK | wx.ICON_EXCLAMATION)
            dial.ShowModal()
        elif count == 1:
            trade = trades.first()
            self.save_charge_to_trade(trade)
            self.out_sid_text.Clear()
            self.out_sid_text.SetFocus()
#            winsound.PlaySound(MEDIA_ROOT+'success.wav',winsound.SND_FILENAME)
        else:
            dial = wx.MessageDialog(None, u'未找到该物流单对应的订单，请查验该单号', u'快递揽件信息确认提示', 
                            wx.OK | wx.ICON_EXCLAMATION)
            dial.ShowModal()
#            winsound.PlaySound(MEDIA_ROOT+'wrong.wav',winsound.SND_FILENAME)
        
        self.out_sid_text.Clear()
        self.out_sid_text.SetFocus()
        evt.Skip()
           
        
    def save_charge_to_trade(self,trade):
        
        with create_session(self.Parent) as session:
            session.query(MergeTrade).filter_by(id=trade.id).update({'is_charged':True,'charge_time':datetime.datetime.now()})

        self.gridpanel.InsertChargeRows(trade)
        
        
    def get_datasource_by_trades(self,trades): 
        
        trade_list = []
        for trade in trades:
            
            t = []
            t.append(trade.out_sid)
            t.append(trade.weight)
            t.append(trade.receiver_state)
            t.append(trade.receiver_city)
            t.append(trade.receiver_district)
            t.append(trade.receiver_zip)
            
            trade_list.append(t)
        return trade_list
                 
    def set_datasource(self,datasource):
        self.gridpanel.setData(datasource)
        
    
    def get_item_list(self,grid):
        
        rows = grid.NumberRows
        cols = grid.NumberCols
        tables = grid.Table
        
        item_list = []
        out_sid_set = set([])
        for i in xrange(0,rows):
            out_sid = tables.GetValue(i,0)
            if out_sid not in out_sid_set:
                item_list.append([tables.GetValue(i,j) for j in range(0,cols)])
                out_sid_set.add(out_sid)

        return item_list
    
    def onClickOnLogisticBtn(self,evt):
        
        wildcard = u"文本文件  (*.txt)|*.txt|csv文档  (*.csv)|*.csv"
        DesktopPath='~'
        
        dt = datetime.datetime.now()
        company_name = self.company_select.GetValue().strip()
        item_list = self.get_item_list(self.gridpanel.grid)
        
        item_len  = len(item_list)

        if item_len == 0:
            evt.Skip()
            return  
        file_name = u'%s-%d.%d-%d'%(company_name,dt.month,dt.day,item_len)

        dlg = wx.FileDialog(
            None, message=u"文件保存为.", defaultDir=DesktopPath, 
            defaultFile=file_name, wildcard=wildcard, style=wx.SAVE
            )
        
        dlg.SetFilterIndex(0)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            with open(path,'w') as f:
                print >> f ,',\t'.join([label.decode('utf8').encode('gbk') for label in self.gridpanel.colLabels])
                for l in item_list:
                    print >> f,',\t'.join( label and label.decode('utf8').encode('gbk') or '-' for label in l)
        
        dlg.Destroy()
        evt.Skip()
        