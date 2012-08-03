#-*- coding:utf8 -*-
'''
Created on 2012-7-19

@author: user1
'''
import datetime
import wx
from taobao.dao.models import Trade,User,LogisticsCompany
from taobao.common.utils import wxdate2pydate
from taobao.dao.configparams import TRADE_TYPE,TRADE_STATUS,SHIPPING_TYPE

class SearchPanel(wx.Panel):
    def __init__(self,parent,id=-1):
        wx.Panel.__init__(self,parent,-1)
        
        self.search_params = {
            'trade_id':None,
            'trade_type':None,
            'trade_status':None,
            'seller_id':None,
            'buyer_nick':None,
            'start_time':None,
            'end_time':None,
            'logistics_id':None,
            'out_sid':None,
            'logistics_company':None,
            'is_picking_print':None,
            'is_express_print':None,
            'is_sms_send':None,
            'has_refund':None
        }
        
        self.session = parent.session
        self.order_label = wx.StaticText(self,-1,'订单号')
        self.order_text = wx.TextCtrl(self,-1)
        self.order_type_label = wx.StaticText(self,-1,'订单类型')
        self.order_type_select = wx.ComboBox(self,-1)
        self.taobao_status_label = wx.StaticText(self,-1,'订单状态')
        self.taobao_status_select = wx.ComboBox(self,-1)
        self.seller_label = wx.StaticText(self,-1,'店铺名称')
        self.seller_select = wx.ComboBox(self,-1) 
        self.buyer_label = wx.StaticText(self,-1,'买家称呼')
        self.buyer_text = wx.TextCtrl(self,-1)
        self.delivery_pick_label = wx.StaticText(self,-1,'已打印发货单')
        self.delivery_pick_check  = wx.CheckBox(self,-1)
        self.send_sms_label = wx.StaticText(self,-1,'已短信提醒')
        self.send_sms_check  = wx.CheckBox(self,-1)
        
        
        self.start_time_label = wx.StaticText(self,-1,'付款时起')
        self.start_time_select = wx.DatePickerCtrl(self, size=(120,-1),
                                style = wx.DP_DROPDOWN| wx.DP_SHOWCENTURY| wx.DP_ALLOWNONE )
        self.end_time_label = wx.StaticText(self,-1,'付款时终')
        self.end_time_select =  wx.DatePickerCtrl(self, size=(120,-1),
                                style = wx.DP_DROPDOWN| wx.DP_SHOWCENTURY| wx.DP_ALLOWNONE )
        self.logistics_label = wx.StaticText(self,-1,'物流单号')
        self.logistics_text = wx.TextCtrl(self,-1)
        self.shipping_type_label = wx.StaticText(self,-1,'物流类型')
        self.shipping_type_select =  wx.ComboBox(self,-1) 
        self.logistics_company_label = wx.StaticText(self,-1,'快递公司')
        self.logistics_company_select = wx.ComboBox(self,-1)
        self.logistics_pick_label = wx.StaticText(self,-1,'已打印物流单')
        self.logistics_pick_check  = wx.CheckBox(self,-1)
        self.has_refund_label = wx.StaticText(self,-1,'有退款')
        self.has_refund_check  = wx.CheckBox(self,-1)
        
        
        
        self.search_btn = wx.Button(self,-1,'搜索')
        
        self.__set_properties()
        self.__do_layout()
        self.__bind_evt()
        
    def __set_properties(self):
        self.SetName('search_panel')
        users = self.session.query(User).all()
        logistics_companies = self.session.query(LogisticsCompany).all()
        self.seller_select.AppendItems([user.nick for user in users])
        self.order_type_select.AppendItems([ v for k,v in TRADE_TYPE.items()])
        self.taobao_status_select.AppendItems([ v for k,v in TRADE_STATUS.items()])
        self.shipping_type_select.AppendItems([v for k,v in SHIPPING_TYPE.items()])
        self.logistics_company_select.AppendItems([company.name for company in logistics_companies])
             
        
    def __do_layout(self):    
        gridbagsizer = wx.GridBagSizer(hgap=5, vgap=5)
        gridbagsizer.Add(self.order_label, pos=(0,0), span=(1,1), flag=wx.EXPAND)
        gridbagsizer.Add(self.order_text, pos=(0,1), span=(1,1), flag=wx.EXPAND)
        gridbagsizer.Add(self.order_type_label, pos=(0,2), span=(1,1), flag=wx.EXPAND)
        gridbagsizer.Add(self.order_type_select, pos=(0,3), span=(1,1), flag=wx.EXPAND)
        gridbagsizer.Add(self.taobao_status_label, pos=(0,4), span=(1,1), flag=wx.EXPAND)
        gridbagsizer.Add(self.taobao_status_select, pos=(0,5), span=(1,1), flag=wx.EXPAND)
        gridbagsizer.Add(self.seller_label, pos=(0,6), span=(1,1), flag=wx.EXPAND)
        gridbagsizer.Add(self.seller_select, pos=(0,7), span=(1,1), flag=wx.EXPAND) 
        gridbagsizer.Add(self.buyer_label, pos=(0,8), span=(1,1), flag=wx.EXPAND)
        gridbagsizer.Add(self.buyer_text, pos=(0,9), span=(1,1), flag=wx.EXPAND)
        gridbagsizer.Add(self.delivery_pick_label, pos=(0,10), span=(1,1), flag=wx.EXPAND)
        gridbagsizer.Add(self.delivery_pick_check, pos=(0,11), span=(1,1), flag=wx.EXPAND)
        gridbagsizer.Add(self.send_sms_label, pos=(0,12), span=(1,1), flag=wx.EXPAND)
        gridbagsizer.Add(self.send_sms_check, pos=(0,13), span=(1,1), flag=wx.EXPAND)
        
        
        gridbagsizer.Add(self.start_time_label, pos=(1,0), span=(1,1), flag=wx.EXPAND)
        gridbagsizer.Add(self.start_time_select, pos=(1,1), span=(1,1), flag=wx.EXPAND)
        gridbagsizer.Add(self.end_time_label, pos=(1,2), span=(1,1), flag=wx.EXPAND)
        gridbagsizer.Add(self.end_time_select, pos=(1,3), span=(1,1), flag=wx.EXPAND)
        gridbagsizer.Add(self.logistics_label, pos=(1,4), span=(1,1), flag=wx.EXPAND)
        gridbagsizer.Add(self.logistics_text, pos=(1,5), span=(1,1), flag=wx.EXPAND)
        gridbagsizer.Add(self.shipping_type_label, pos=(1,6), span=(1,1), flag=wx.EXPAND)
        gridbagsizer.Add(self.shipping_type_select, pos=(1,7), span=(1,1), flag=wx.EXPAND)
        gridbagsizer.Add(self.logistics_company_label, pos=(1,8), span=(1,1), flag=wx.EXPAND)
        gridbagsizer.Add(self.logistics_company_select, pos=(1,9), span=(1,1), flag=wx.EXPAND)
        gridbagsizer.Add(self.logistics_pick_label, pos=(1,10), span=(1,1), flag=wx.EXPAND)
        gridbagsizer.Add(self.logistics_pick_check, pos=(1,11), span=(1,1), flag=wx.EXPAND)
        gridbagsizer.Add(self.has_refund_label, pos=(1,12), span=(1,1), flag=wx.EXPAND)
        gridbagsizer.Add(self.has_refund_check, pos=(1,13), span=(1,1), flag=wx.EXPAND)
        
        gridbagsizer.Add(self.search_btn,pos=(1,14),span=(1,1),flag=wx.EXPAND)
        
        gridbagsizer.Layout()
        
        self.SetSizer(gridbagsizer)
        
    def __bind_evt(self):
#        self.Bind(wx.EVT_DATE_CHANGED, self.OnDateChanged, self.start_time_select)
#        self.Bind(wx.EVT_DATE_CHANGED, self.OnDateChanged, self.end_time_select)
        self.Bind(wx.EVT_BUTTON, self.OnSearch, self.search_btn)
        
    
    def OnSearch(self,evt):
        datasource = self.Parent.grid.datasource
        search_params = self.get_search_data()
        trade_id   = search_params['trade_id']
        trade_type = search_params['trade_type']
        trade_status = search_params['trade_status']
        seller_id = search_params['seller_id']
        buyer_nick = search_params['buyer_nick']
        start_time = search_params['start_time']
        end_time = search_params['end_time']
        logistics_id = search_params['logistics_id']
        shipping_type = search_params['shipping_type']
        logistics_company = search_params['logistics_company']
        is_picking_print = search_params['is_picking_print']
        is_express_print = search_params['is_express_print']
        is_sms_send = search_params['is_sms_send']
        has_refund = search_params['has_refund']
        
        if trade_id:
            datasource = datasource.filter_by(tid=trade_id.decode('utf8'))
        elif logistics_id:
            datasource = datasource.filter('tid = (select tid from shop_logistics_logistic where out_sid =:logistics_id')\
                   .params(logistics_id=logistics_id.decode('utf8')) 
        else:
            if trade_type:
                type_dict = dict([(v,k) for k,v in TRADE_TYPE.items()])
                datasource = datasource.filter_by(type=type_dict.get(trade_type.strip().encode('utf8'),None))
            if trade_status:
                status_dict = dict([(v,k) for k,v in TRADE_STATUS.items()])
                datasource = datasource.filter_by(status=status_dict.get(trade_status.strip().encode('utf8'),None))
            if seller_id:
                datasource = datasource.filter_by(seller_nick=seller_id.strip().decode('utf8'))
            if buyer_nick:
                datasource = datasource.filter_by(buyer_nick=buyer_nick.strip().decode('utf8'))
            if start_time:
                datasource = datasource.filter("pay_time >=:start").params(start=start_time)
            if end_time:
                datasource = datasource.filter("pay_time <=:end").params(end=end_time)
            if shipping_type:
                shipping_dict = dict([(v,k) for k,v in SHIPPING_TYPE.items()])
                datasource = datasource.filter_by(shipping_type=shipping_dict.get(shipping_type.strip().encode('utf8'),None))
            if logistics_company :
                datasource = datasource.filter_by(logistics_company_name=logistics_company.strip().decode('utf8'))
            if is_picking_print:
                datasource = datasource.filter_by(is_picking_print=True)
            if is_express_print:
                datasource = datasource.filter_by(is_express_print=True)
            if is_sms_send:
                datasource = datasource.filter_by(is_send_sms=True)
            if has_refund:
                datasource = datasource.filter_by(has_refund=True)
        
        self.Parent.grid.setSearchData(datasource)
        
        
    def get_search_data(self):
        self.search_params['trade_id']=self.order_text.GetValue()
        self.search_params['trade_type']=self.order_type_select.GetValue()
        self.search_params['trade_status']=self.taobao_status_select.GetValue()
        self.search_params['seller_id']=self.seller_select.GetValue()     
        self.search_params['buyer_nick']=self.buyer_text.GetValue()
        start_time = self.start_time_select.GetValue()
        end_time   = self.end_time_select.GetValue()
        self.search_params['start_time']=wxdate2pydate(start_time)
        self.search_params['end_time']=wxdate2pydate(end_time)
        self.search_params['logistics_id']=self.logistics_text.GetValue()
        self.search_params['shipping_type']=self.shipping_type_select.GetValue()
        self.search_params['logistics_company']=self.logistics_company_select.GetValue()
        self.search_params['is_picking_print']=self.delivery_pick_check.IsChecked()
        self.search_params['is_express_print']=self.delivery_pick_check.IsChecked()
        self.search_params['is_sms_send']=self.send_sms_check.IsChecked()
        self.search_params['has_refund']=self.has_refund_check.IsChecked()
        
        return self.search_params
        
    