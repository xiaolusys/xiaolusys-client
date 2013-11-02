#-*- coding:utf8 -*-
'''
Created on 2012-7-19

@author: user1
'''
import datetime
import wx
from   sqlalchemy import or_
from taobao.dao.models import MergeTrade,MergeOrder,User,LogisticsCompany
from taobao.common.utils import wxdate2pydate,create_session
from taobao.dao import configparams as cfg

CHECKBOX_THIRD_VALUE = 2

class SearchPanel(wx.Panel):
    def __init__(self,parent,id=-1):
        wx.Panel.__init__(self,parent,-1)
        
        self.Session = parent.Session
        self.order_label = wx.StaticText(self,-1,u'订单号')
        self.order_text = wx.TextCtrl(self,-1,style=wx.TE_PROCESS_ENTER)
        self.order_receiver_name_label = wx.StaticText(self,-1,u'收货人')
        self.order_receiver_name = wx.TextCtrl(self,-1,style=wx.TE_PROCESS_ENTER)
        self.taobao_status_label = wx.StaticText(self,-1,u'订单状态')
        self.taobao_status_select = wx.ComboBox(self,-1,size=(90,-1))
        self.seller_label = wx.StaticText(self,-1,u'店铺名称')
        self.seller_select = wx.ComboBox(self,-1,size=(90,-1)) 
        self.buyer_label = wx.StaticText(self,-1,u'买家称呼')
        self.buyer_text = wx.TextCtrl(self,-1,style=wx.TE_PROCESS_ENTER,size=(90,-1))
        self.outer_id_label = wx.StaticText(self,-1,u'商品编码')
        self.outer_id_text =  wx.TextCtrl(self,-1,style=wx.TE_PROCESS_ENTER) 
        self.sku_outer_id_label = wx.StaticText(self,-1,u'规格编码')
        self.sku_outer_id_text =  wx.TextCtrl(self,-1,style=wx.TE_PROCESS_ENTER) 
        self.delivery_pick_label = wx.StaticText(self,-1,u'发货单')
        self.delivery_pick_check  = wx.CheckBox(self,-1,style=wx.CHK_3STATE|wx.CHK_ALLOW_3RD_STATE_FOR_USER)
        self.logistics_pick_label = wx.StaticText(self,-1,u'物流单')
        self.logistics_pick_check  = wx.CheckBox(self,-1,style=wx.CHK_3STATE|wx.CHK_ALLOW_3RD_STATE_FOR_USER)
        self.single_prod_label  = wx.StaticText(self,-1,u'单品')
        self.single_prod_check  = wx.CheckBox(self,-1,style=wx.CHK_2STATE)
        
        self.start_time_label = wx.StaticText(self,-1,u'付款时起')
        self.start_time_select = wx.DatePickerCtrl(self,
                                style = wx.DP_DROPDOWN| wx.DP_SHOWCENTURY| wx.DP_ALLOWNONE)
        self.end_time_label = wx.StaticText(self,-1,u'付款时终')
        self.end_time_select =  wx.DatePickerCtrl(self,
                                style = wx.DP_DROPDOWN| wx.DP_SHOWCENTURY| wx.DP_ALLOWNONE)
        self.logistics_label = wx.StaticText(self,-1,u'物流单号')
        self.logistics_text = wx.TextCtrl(self,-1,style=wx.TE_PROCESS_ENTER,size=(90,-1))
        self.trade_type_label = wx.StaticText(self,-1,u'订单类型')
        self.trade_type_select =  wx.ComboBox(self,-1,size=(90,-1)) 
        self.logistics_company_label = wx.StaticText(self,-1,u'快递公司')
        self.logistics_company_select = wx.ComboBox(self,-1,size=(90,-1))
        self.weight_start_label = wx.StaticText(self,-1,u'称重日期起')
        self.weight_start_select = wx.DatePickerCtrl(self,
                                style = wx.DP_DROPDOWN| wx.DP_SHOWCENTURY| wx.DP_ALLOWNONE)
        self.weight_end_label = wx.StaticText(self,-1,u'称重日期止')
        self.weight_end_select =  wx.DatePickerCtrl(self,
                                style = wx.DP_DROPDOWN| wx.DP_SHOWCENTURY| wx.DP_ALLOWNONE)
        self.urggent_doc_label = wx.StaticText(self,-1,u'紧急件')
        self.urggent_doc_check  = wx.CheckBox(self,-1,style=wx.CHK_2STATE)
        self.is_locked_label = wx.StaticText(self,-1,u'已锁定')
        self.is_locked_check  = wx.CheckBox(self,-1,style=wx.CHK_3STATE|wx.CHK_ALLOW_3RD_STATE_FOR_USER)
        self.juhuasuan_label = wx.StaticText(self,-1,u'聚划算')
        self.juhuasuan_check  = wx.CheckBox(self,-1,style=wx.CHK_3STATE|wx.CHK_ALLOW_3RD_STATE_FOR_USER)
        
        self.__set_properties()
        self.__do_layout()
        self.__bind_evt()
        
    def __set_properties(self):
        self.SetName('search_panel')
        with create_session(self.Parent) as session: 
            users = session.query(User).all()
            logistics_companies = session.query(LogisticsCompany).filter_by(status=True).order_by('priority desc').all()
        self.seller_select.AppendItems([user.nick for user in users])
        self.logistics_company_select.AppendItems([company.name for company in logistics_companies])
        
        self.taobao_status_select.AppendItems([ v for k,v in cfg.TRADE_STATUS.items()])
        self.trade_type_select.AppendItems([v for k,v in cfg.TRADE_TYPE.items()])   
 
        
    def __do_layout(self):    
        gridbagsizer = wx.GridBagSizer(hgap=5, vgap=5)
        gridbagsizer.Add(self.order_label, pos=(0,0), span=(1,1), flag=wx.EXPAND)
        gridbagsizer.Add(self.order_text, pos=(0,1), span=(1,1), flag=wx.EXPAND)
        gridbagsizer.Add(self.order_receiver_name_label, pos=(0,2), span=(1,1), flag=wx.EXPAND)
        gridbagsizer.Add(self.order_receiver_name, pos=(0,3), span=(1,1), flag=wx.EXPAND)
        gridbagsizer.Add(self.taobao_status_label, pos=(0,4), span=(1,1), flag=wx.EXPAND)
        gridbagsizer.Add(self.taobao_status_select, pos=(0,5), span=(1,1), flag=wx.EXPAND)
        gridbagsizer.Add(self.seller_label, pos=(0,6), span=(1,1), flag=wx.EXPAND)
        gridbagsizer.Add(self.seller_select, pos=(0,7), span=(1,1), flag=wx.EXPAND) 
        gridbagsizer.Add(self.buyer_label, pos=(0,8), span=(1,1), flag=wx.EXPAND)
        gridbagsizer.Add(self.buyer_text, pos=(0,9), span=(1,1), flag=wx.EXPAND)
        gridbagsizer.Add(self.outer_id_label, pos=(0,10), span=(1,1), flag=wx.EXPAND)
        gridbagsizer.Add(self.outer_id_text, pos=(0,11), span=(1,1), flag=wx.EXPAND)
        gridbagsizer.Add(self.sku_outer_id_label, pos=(0,12), span=(1,1), flag=wx.EXPAND)
        gridbagsizer.Add(self.sku_outer_id_text, pos=(0,13), span=(1,1), flag=wx.EXPAND)
        gridbagsizer.Add(self.logistics_pick_label, pos=(0,14), span=(1,1), flag=wx.EXPAND)
        gridbagsizer.Add(self.logistics_pick_check, pos=(0,15), span=(1,1), flag=wx.EXPAND)
        gridbagsizer.Add(self.delivery_pick_label, pos=(0,16), span=(1,1), flag=wx.EXPAND)
        gridbagsizer.Add(self.delivery_pick_check, pos=(0,17), span=(1,1), flag=wx.EXPAND)
        gridbagsizer.Add(self.single_prod_label, pos=(0,18), span=(1,1), flag=wx.EXPAND)
        gridbagsizer.Add(self.single_prod_check, pos=(0,19), span=(1,1), flag=wx.EXPAND)
        
        gridbagsizer.Add(self.start_time_label, pos=(1,0), span=(1,1), flag=wx.EXPAND)
        gridbagsizer.Add(self.start_time_select, pos=(1,1), span=(1,1), flag=wx.EXPAND)
        gridbagsizer.Add(self.end_time_label, pos=(1,2), span=(1,1), flag=wx.EXPAND)
        gridbagsizer.Add(self.end_time_select, pos=(1,3), span=(1,1), flag=wx.EXPAND)
        gridbagsizer.Add(self.logistics_label, pos=(1,4), span=(1,1), flag=wx.EXPAND)
        gridbagsizer.Add(self.logistics_text, pos=(1,5), span=(1,1), flag=wx.EXPAND)
        gridbagsizer.Add(self.trade_type_label, pos=(1,6), span=(1,1), flag=wx.EXPAND)
        gridbagsizer.Add(self.trade_type_select, pos=(1,7), span=(1,1), flag=wx.EXPAND)
        gridbagsizer.Add(self.logistics_company_label, pos=(1,8), span=(1,1), flag=wx.EXPAND)
        gridbagsizer.Add(self.logistics_company_select, pos=(1,9), span=(1,1), flag=wx.EXPAND)
        gridbagsizer.Add(self.weight_start_label, pos=(1,10), span=(1,1), flag=wx.EXPAND)
        gridbagsizer.Add(self.weight_start_select, pos=(1,11), span=(1,1), flag=wx.EXPAND)
        gridbagsizer.Add(self.weight_end_label, pos=(1,12), span=(1,1), flag=wx.EXPAND)
        gridbagsizer.Add(self.weight_end_select, pos=(1,13), span=(1,1), flag=wx.EXPAND)
        gridbagsizer.Add(self.is_locked_label, pos=(1,14), span=(1,1), flag=wx.EXPAND)
        gridbagsizer.Add(self.is_locked_check, pos=(1,15), span=(1,1), flag=wx.EXPAND)
        gridbagsizer.Add(self.urggent_doc_label, pos=(1,16), span=(1,1), flag=wx.EXPAND)
        gridbagsizer.Add(self.urggent_doc_check, pos=(1,17), span=(1,1), flag=wx.EXPAND)
        gridbagsizer.Add(self.juhuasuan_label, pos=(1,18), span=(1,1), flag=wx.EXPAND)
        gridbagsizer.Add(self.juhuasuan_check, pos=(1,19), span=(1,1), flag=wx.EXPAND)

        gridbagsizer.Layout()
        
        self.SetSizer(gridbagsizer)
        
    def __bind_evt(self):
        
        self.Bind(wx.EVT_TEXT_ENTER, self.OnSearch, self.order_text)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnSearch, self.order_receiver_name)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnSearch, self.buyer_text)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnSearch, self.outer_id_text)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnSearch, self.logistics_text)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnSearch, self.sku_outer_id_text)
        
        self.Bind(wx.EVT_COMBOBOX, self.OnSearch, self.taobao_status_select)
        self.Bind(wx.EVT_COMBOBOX, self.OnSearch, self.seller_select)
        self.Bind(wx.EVT_COMBOBOX, self.OnSearch, self.trade_type_select)
        self.Bind(wx.EVT_COMBOBOX, self.OnSearch, self.logistics_company_select)
        
        self.Bind(wx.EVT_DATE_CHANGED, self.OnSearch, self.start_time_select)
        self.Bind(wx.EVT_DATE_CHANGED, self.OnSearch, self.end_time_select)
        
        self.Bind(wx.EVT_DATE_CHANGED, self.OnSearch, self.weight_start_select)
        self.Bind(wx.EVT_DATE_CHANGED, self.OnSearch, self.weight_end_select)
        
        self.Bind(wx.EVT_CHECKBOX, self.OnSearch, self.delivery_pick_check)
        self.Bind(wx.EVT_CHECKBOX, self.OnSearch, self.logistics_pick_check)
        
        self.Bind(wx.EVT_CHECKBOX, self.OnSearch, self.urggent_doc_check)
        self.Bind(wx.EVT_CHECKBOX, self.OnSearch, self.single_prod_check)
        self.Bind(wx.EVT_CHECKBOX, self.OnSearch, self.is_locked_check)
        self.Bind(wx.EVT_CHECKBOX, self.OnSearch, self.juhuasuan_check)
        
    def clearSearchPanel(self,evt):
        
        self.order_text.Clear()
        self.order_receiver_name.Clear()
        self.taobao_status_select.SetValue('')
        self.seller_select.SetValue('')
        self.buyer_text.Clear()
        
        self.start_time_select.SetValue(wx.DefaultDateTime)
        self.end_time_select.SetValue(wx.DefaultDateTime)

        self.logistics_text.Clear()
        self.trade_type_select.SetValue('')
        self.logistics_company_select.SetValue('')
        self.delivery_pick_check.SetValue(False)
        self.logistics_pick_check.SetValue(False)
        self.outer_id_text.Clear()
        self.sku_outer_id_text.Clear()
        self.urggent_doc_check.SetValue(False)
        self.is_locked_check.SetValue(False)
        self.single_prod_check.SetValue(False)
        self.juhuasuan_check.SetValue(False)
        
        self.weight_start_select.SetValue(wx.DefaultDateTime)
        self.weight_end_select.SetValue(wx.DefaultDateTime)
        
        self.OnSearch(None)

    
    def OnSearch(self,evt):
        ds = self.Parent.grid.datasource
        counter    = self.Parent.grid.counter
        
        trade_id   = self.order_text.GetValue()
        receiver_name = self.order_receiver_name.GetValue()
        trade_status = self.taobao_status_select.GetValue()
        seller_id = self.seller_select.GetValue()
        buyer_nick = self.buyer_text.GetValue()
        
        start_time = self.start_time_select.GetValue()
        end_time   = self.end_time_select.GetValue()
        start_time = wxdate2pydate(start_time)
        end_time = wxdate2pydate(end_time)
        logistics_id = self.logistics_text.GetValue()
        trade_type = self.trade_type_select.GetValue()
        logistics_company = self.logistics_company_select.GetValue()
        pick_print_state  = self.delivery_pick_check.Get3StateValue()
        express_print_state = self.logistics_pick_check.Get3StateValue()
        outer_id      = self.outer_id_text.GetValue()
        sku_outer_id  = self.sku_outer_id_text.GetValue()
        urgent_doc_state = self.urggent_doc_check.GetValue()
        locke_state     = self.is_locked_check.Get3StateValue() 
        single_prod     = self.single_prod_check.GetValue()
        juhuasuan    = self.juhuasuan_check.Get3StateValue() 
        
        weight_start_time = self.weight_start_select.GetValue()
        weight_end_time   = self.weight_end_select.GetValue()
        weight_start_time = wxdate2pydate(weight_start_time)
        weight_end_time = wxdate2pydate(weight_end_time)

        
        def appendFilter(datasource):
            if trade_id:
                datasource = datasource.filter(or_(MergeTrade.tid==trade_id,MergeTrade.id==trade_id))
            elif logistics_id:
                datasource = datasource.filter_by(out_sid=logistics_id)
            else:
                if receiver_name:
                    datasource = datasource.filter_by(receiver_name=receiver_name)
                if trade_status:
                    status_dict = dict([(v,k) for k,v in cfg.TRADE_STATUS.items()])
                    datasource = datasource.filter_by(status=status_dict.get(trade_status.strip(),None))
                if seller_id:
                    datasource = datasource.filter_by(seller_nick=seller_id.strip())
                if buyer_nick:
                    datasource = datasource.filter_by(buyer_nick=buyer_nick.strip())
                if start_time:
                    datasource = datasource.filter("pay_time >=:start").params(start=start_time)
                if end_time:
                    datasource = datasource.filter("pay_time <=:end").params(end=end_time)
                if weight_start_time:
                    datasource = datasource.filter("weight_time >=:start").params(start=weight_start_time)
                if weight_end_time:
                    datasource = datasource.filter("weight_time <=:end").params(end=weight_end_time)
                if trade_type:
                    trade_type_dict = dict([(v,k) for k,v in cfg.TRADE_TYPE.items()])
                    datasource = datasource.filter_by(type=trade_type_dict.get(trade_type.strip(),None))
                if logistics_company :
                    with create_session(self.Parent) as session:
                        log_company = session.query(LogisticsCompany).filter_by(name=logistics_company.strip()).one()
                    datasource = datasource.filter_by(logistics_company_id=log_company.id)
                if urgent_doc_state:
                    datasource = datasource.filter_by(priority=1)
                if single_prod:
                    datasource = datasource.filter(MergeTrade.prod_num==1)
                if pick_print_state:
                    datasource = datasource.filter_by(is_picking_print=pick_print_state == 1 and True or False)
                if express_print_state:
                    datasource = datasource.filter_by(is_express_print=express_print_state == 1 and True or False)
                if juhuasuan:
                    if juhuasuan == 1:
                        datasource = datasource.filter(MergeTrade.trade_from.op('&')(cfg.JUHUASUAN_CODE) == cfg.JUHUASUAN_CODE)
                    else:
                        datasource = datasource.filter(MergeTrade.trade_from.op('&')(cfg.JUHUASUAN_CODE) != cfg.JUHUASUAN_CODE)
                if outer_id:
                    trade_ids = [t.id for t in datasource]
                    with create_session(self.Parent) as session:
                        
                        merge_orders = session.query(MergeOrder).filter(MergeOrder.merge_trade_id.in_(trade_ids))
                        if outer_id and sku_outer_id:
                            merge_orders = merge_orders.filter(MergeOrder.outer_id==outer_id,MergeOrder.outer_sku_id==sku_outer_id)
                        else :
                            merge_orders = merge_orders.filter(MergeOrder.outer_id==outer_id)
                        
                        trade_ids = set([o.merge_trade_id for o in merge_orders])
                        datasource = session.query(MergeTrade).filter(MergeTrade.id.in_(trade_ids))
                        
                if locke_state:
                    datasource = datasource.filter_by(is_locked=locke_state == 1 and True or False)
                    
            return datasource
        
        if outer_id:
            counter = None
        else:
            counter = appendFilter(counter)
                
        self.Parent.grid.setSearchData(appendFilter(ds),counter=counter)

        

    
