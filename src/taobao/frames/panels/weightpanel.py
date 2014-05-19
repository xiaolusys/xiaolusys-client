#-*- coding:utf8 -*-
'''
Created on 2012-7-27

@author: user1
'''
import re
import winsound
import weakref
import datetime
import wx,wx.grid
from MySQLdb import IntegrityError
from taobao.common.utils import create_session,MEDIA_ROOT
from taobao.dao.models import MergeTrade,LogisticsCompany,MergeOrder,Product,ProductSku
from taobao.frames.panels.gridpanel import WeightGridPanel
from taobao.dao.tradedao import get_used_orders,get_return_orders
from taobao.common.utils import getconfig
from taobao.dao import configparams as cfg

weight_regex=re.compile('[0-9\.]{1,7}$')

class ScanWeightPanel(wx.Panel):
    
    def __init__(self,parent,id=-1):
        wx.Panel.__init__(self,parent,id)
        
        self.Session = parent.Session
        self.trade = None
        self.valid_code = ''
        self.company_label = wx.StaticText(self,-1,u'快递公司')
        self.company_select = wx.ComboBox(self,-1)
        self.out_sid_label = wx.StaticText(self,-1,u'快递单号')
        self.out_sid_text  = wx.TextCtrl(self,-1,size=(200,-1),style=wx.TE_PROCESS_ENTER)
        self.weight_label  = wx.StaticText(self,-1,u'称重重量(g)')
        self.weight_text  = wx.TextCtrl(self,-1,size=(200,-1),style=wx.TE_PROCESS_ENTER)

        self.hand_add_button   = wx.Button(self,-1,u'保存') 
        self.cancel_button   = wx.Button(self,-1,u'取消')
        
        self.error_text = wx.StaticText(self,-1)
        
        self.order_label1  = wx.StaticText(self,-1,u'店铺简称')
        self.order_content1  = wx.TextCtrl(self,-1)
        self.order_label3  = wx.StaticText(self,-1,u'订单类型')
        self.order_content3  = wx.TextCtrl(self,-1)
        self.order_label4  = wx.StaticText(self,-1,u'会员名称')
        self.order_content4  = wx.TextCtrl(self,-1)
        self.order_label5  = wx.StaticText(self,-1,u'快递公司')
        self.order_content5  = wx.TextCtrl(self,-1)     
        self.order_label6  = wx.StaticText(self,-1,u'收货人')
        self.order_content6  = wx.TextCtrl(self,-1,size=(130,-1))
        self.order_label7  = wx.StaticText(self,-1,u'收货地址')
        self.order_content7  = wx.TextCtrl(self,-1,size=(300,-1))
        
        self.order_box1 = wx.StaticBox(self,-1,u'扫描订单详细信息')
        
        self.gridpanel = WeightGridPanel(self,-1)
        
        self.order_box2 = wx.StaticBox(self,-1,u'已称重订单列表')

        self.__set_properties()
        self.__do_layout()
        self.__evt_bind()
    
    
    def __set_properties(self):
        self.SetName('weight panel')
        
        with create_session(self.Parent) as session: 
            logistics_companies = session.query(LogisticsCompany).filter_by(status=True).order_by('priority desc').all()
        self.company_select.AppendItems([company.name for company in logistics_companies])
        
        self.control_array = []
        self.control_array.append(self.order_content1)
        self.control_array.append(self.order_content3)
        self.control_array.append(self.order_content4)
        self.control_array.append(self.order_content5)
        self.control_array.append(self.order_content6)
        self.control_array.append(self.order_content7)

            
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


        flex_sizer1.Add(self.hand_add_button,0,10)
        flex_sizer1.Add(self.cancel_button,0,11)
        flex_sizer1.Add(self.error_text,0,12)
        
        sbsizer1 = wx.StaticBoxSizer(self.order_box1,wx.VERTICAL)
        bag_sizer1 = wx.GridBagSizer(hgap=5,vgap=5)
        bag_sizer1.Add(self.order_label1,pos=(0,0),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_content1,pos=(0,1),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_label3,pos=(0,2),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_content3,pos=(0,3),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_label4,pos=(0,4),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_content4,pos=(0,5),span=(1,1),flag=wx.EXPAND)   
        bag_sizer1.Add(self.order_label5,pos=(0,6),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_content5,pos=(0,7),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_label6,pos=(0,8),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_content6,pos=(0,9),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_label7,pos=(0,10),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_content7,pos=(0,11),span=(1,1),flag=wx.EXPAND)
        
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
        self.Bind(wx.EVT_BUTTON,self.onClickSaveBtn,self.hand_add_button)
        self.Bind(wx.EVT_BUTTON,self.onClickCancelBtn,self.cancel_button)   
    
    def onComboboxSelect(self,evt):
        company_name = self.company_select.GetValue().strip()
        out_sid      = self.out_sid_text.GetValue().strip()
        
        trades = None
        if company_name:
            with create_session(self.Parent) as session:
                logistics_company = session.query(LogisticsCompany).filter_by(name=company_name).first()
                trades = session.query(MergeTrade).filter(MergeTrade.sys_status.in_(self.getPreWeightStatus()))\
                    .filter_by(out_sid=out_sid,logistics_company_id=logistics_company.id,reason_code='')
        count = trades.count() if trades else 0   
        if count>1 :
            self.error_text.SetLabel(u'该快递单号已重复，请联系管理员')
            self.error_text.SetForegroundColour('black')
            self.error_text.SetBackgroundColour('red')
        elif count == 1:
            self.trade = trades.one()
            self.setTradeInfoPanel(self.trade)
            self.weight_text.SetFocus()
            self.error_text.SetLabel('')
        else:
            self.error_text.SetLabel(u'未找到该订单，或订单被拦截')
            self.error_text.SetForegroundColour('black')
            self.error_text.SetBackgroundColour('red')
            winsound.PlaySound(MEDIA_ROOT+'wrong.wav',winsound.SND_FILENAME)
        
    def getSid(self,out_sid):
        
        if len(out_sid) < 20:
            return out_sid
        return out_sid[0:13]
        
    def getYDValidCode(self,out_sid):
        
        if len(out_sid) < 20:
            return ''
        return out_sid[13:17]
    
    def onOutsidTextChange(self,evt):
        company_name = self.company_select.GetValue().strip()
        out_sid      = self.out_sid_text.GetValue().strip() 
        trades          = None
        sid  = self.getSid(out_sid)
        self.valid_code = self.getYDValidCode(out_sid)
        with create_session(self.Parent) as session:
            if company_name and sid:
                logistics_company = session.query(LogisticsCompany).filter_by(name=company_name).first()
                trades = session.query(MergeTrade).filter(MergeTrade.sys_status.in_(self.getPreWeightStatus()))\
                    .filter_by(out_sid=sid,logistics_company_id=logistics_company.id,reason_code='',is_express_print=True)
            elif sid :
                trades = session.query(MergeTrade).filter(MergeTrade.sys_status.in_(self.getPreWeightStatus()))\
                        .filter_by(out_sid=sid,reason_code='',is_express_print=True)
                 
        count = trades.count() if trades else 0
        
        if count>1 :
            self.error_text.SetLabel(u'该快递单号已重复,请选择快递')
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
            self.error_text.SetLabel(u'未找到该订单，或订单被拦截')
            self.error_text.SetForegroundColour('black')
            self.error_text.SetBackgroundColour('red')
            self.clearTradeInfoPanel()
            self.weight_text.Clear()
            self.out_sid_text.Clear()
            self.out_sid_text.SetFocus()
            winsound.PlaySound(MEDIA_ROOT+'wrong.wav',winsound.SND_FILENAME)
        evt.Skip()
        
    def clearTradeInfoPanel(self):
        for i in xrange(1,7):
            try:
                content = eval('self.order_content%s'%str(i))
                content.Clear() 
            except:
                pass 
              
        
    def setTradeInfoPanel(self,trade):
 
        self.order_content1.SetValue(trade.seller_nick)
        self.order_content3.SetValue(cfg.TRADE_TYPE.get(trade.type,u'其他'))
        self.order_content4.SetValue(trade.buyer_nick)
        self.order_content5.SetValue(trade.logistics_company.name)
        self.order_content6.SetValue(trade.receiver_name+'/'+trade.receiver_mobile)        
        self.order_content7.SetValue(' '.join([trade.receiver_state,trade.receiver_city,trade.receiver_district,trade.receiver_address]))
        
        self.Layout()
        
    def onWeightTextChange(self,evt):
        weight = self.weight_text.GetValue().strip()
        if weight_regex.match(weight) and self.trade :
            self.save_weight_to_trade(self.trade,weight)
            self.weight_text.Clear()
            self.out_sid_text.Clear()
            self.out_sid_text.SetFocus()
            winsound.PlaySound(MEDIA_ROOT+'success.wav',winsound.SND_FILENAME)
        else:
            winsound.PlaySound(MEDIA_ROOT+'wrong.wav',winsound.SND_FILENAME)
        
    def save_weight_to_trade(self,trade,weight):
        with create_session(self.Parent) as session: 
            #减库存
            orders = get_used_orders(session,self.trade.id)
            for order in orders:
                outer_id = order.outer_id 
                outer_sku_id = order.outer_sku_id 
                product = session.query(Product).filter_by(outer_id=outer_id).first()
                if product and outer_sku_id:
                    session.query(ProductSku).filter_by(outer_id=outer_sku_id,product=product)\
                        .update({ProductSku.quantity:ProductSku.quantity-order.num})
                        
                    if order.gift_type in (cfg.REAL_ORDER_GIT_TYPE,cfg.COMBOSE_SPLIT_GIT_TYPE):
                        session.query(ProductSku).filter_by(outer_id=outer_sku_id,product=product)\
                        .update({ProductSku.wait_post_num:ProductSku.wait_post_num-order.num})
                
                session.query(Product).filter_by(outer_id=outer_id)\
                    .update({Product.collect_num:Product.collect_num-order.num})
                    
                if order.gift_type in (cfg.REAL_ORDER_GIT_TYPE,cfg.COMBOSE_SPLIT_GIT_TYPE):
                    session.query(Product).filter_by(outer_id=outer_id)\
                    .update({Product.wait_post_num:Product.wait_post_num-order.num})
            
            if trade.type == 'exchange':
                return_orders = get_return_orders(session,self.trade.id)
                for order in return_orders:
                    outer_id = order.outer_id 
                    outer_sku_id = order.outer_sku_id 
                    product = session.query(Product).filter_by(outer_id=outer_id).first()
                    if product and outer_sku_id:
                        session.query(ProductSku).filter_by(outer_id=outer_sku_id,product=product)\
                            .update({ProductSku.quantity:ProductSku.quantity+order.num})
                    
                    session.query(Product).filter_by(outer_id=outer_id)\
                        .update({Product.collect_num:Product.collect_num+order.num})
                    
            #称重后，内部状态变为发货已发货
            session.query(MergeTrade).filter(MergeTrade.sys_status.in_(self.getPreWeightStatus())).filter_by(id=trade.id)\
                    .update({'weight':weight,'sys_status':cfg.SYS_STATUS_FINISHED,
                             'weight_time':datetime.datetime.now(),'reserveh':self.valid_code}
                    ,synchronize_session='fetch')
                    
        self.gridpanel.InsertTradeRows(trade)
        self.trade = None
        self.valid_code = ''
        for control in self.control_array:
            control.SetValue('')
        
    
    def getPreWeightStatus(self):
        conf = getconfig()
        is_need_check = conf.get('custom', 'check_barcode')
        if is_need_check.lower() == 'true':
            return (cfg.SYS_STATUS_WAITSCANWEIGHT,)
        return (cfg.SYS_STATUS_WAITSCANWEIGHT,cfg.SYS_STATUS_WAITSCANCHECK)
        
        
    def onClickSaveBtn(self,evt):
        weight = self.weight_text.GetValue()
        if self.trade and weight:
            self.save_weight_to_trade(self.trade,weight)
            
    
    def onClickCancelBtn(self,evt):
        self.out_sid_text.Clear()
        self.weight_text.Clear()
        for control in self.control_array:
            control.Clear()
        self.out_sid_text.SetFocus()
   
     
                 
