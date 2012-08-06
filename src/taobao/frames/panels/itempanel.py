#-*- coding:utf8 -*-
'''
Created on 2012-7-16

@author: user1
'''
import wx
from taobao.dao.models import MergeTrade,LogisticsCompany
from taobao.dao.configparams import TRADE_TYPE,TRADE_STATUS,SHIPPING_TYPE,SYS_STATUS

class BasicPanel(wx.Panel):
    def __init__(self, parent,id=-1):
        wx.Panel.__init__(self,parent,id)
        
        self.session = parent.session
        self.trade = None
        self.order_label1  = wx.StaticText(self,-1,'店铺简称')
        self.order_content1  = wx.TextCtrl(self,-1)
        self.order_label2  = wx.StaticText(self,-1,'订单类型')
        self.order_content2  = wx.TextCtrl(self,-1)
        self.order_label3  = wx.StaticText(self,-1,'来源单号')
        self.order_content3  = wx.TextCtrl(self,-1)
        self.order_label4  = wx.StaticText(self,-1,'会员名称')
        self.order_content4  = wx.TextCtrl(self,-1)
        self.order_label5  = wx.StaticText(self,-1,'付款时间')
        self.order_content5  = wx.TextCtrl(self,-1)
        self.seller_cod_label = wx.StaticText(self,-1,'卖家货到付款服务费')
        self.seller_cod_text  = wx.TextCtrl(self,-1)
        self.delivery_pick_label = wx.StaticText(self,-1,'已打印发货单')
        self.delivery_pick_check  = wx.CheckBox(self,-1)
           
        self.order_label6  = wx.StaticText(self,-1,'商品数量')
        self.order_content6  = wx.SpinCtrl(self,-1)
        self.order_label7  = wx.StaticText(self,-1,'订单金额')
        self.order_content7  = wx.TextCtrl(self,-1)
        self.order_label8 = wx.StaticText(self,-1,'支付金额')
        self.order_content8  = wx.TextCtrl(self,-1)
        self.order_label9  = wx.StaticText(self,-1,'物流公司代码')
        self.order_content9  = wx.TextCtrl(self,-1)
        self.order_label10  = wx.StaticText(self,-1,'让利金额')
        self.order_content10  = wx.TextCtrl(self,-1)
        self.buyer_cod_label = wx.StaticText(self,-1,'买家货到付款服务费')
        self.buyer_cod_text  = wx.TextCtrl(self,-1)
        self.logistics_pick_label = wx.StaticText(self,-1,'已打印物流单')
        self.logistics_pick_check  = wx.CheckBox(self,-1) 
        
        self.order_label11  = wx.StaticText(self,-1,'物流类型')
        self.order_content11  = wx.TextCtrl(self,-1) 
        self.order_label12  = wx.StaticText(self,-1,'物流费用')
        self.order_content12  = wx.TextCtrl(self,-1,'0')
        self.order_label13  = wx.StaticText(self,-1,'物流公司')
        self.order_content13  = wx.ComboBox(self,-1)
        self.order_label14  = wx.StaticText(self,-1,'物流单号')
        self.order_content14  = wx.TextCtrl(self,-1)
        self.order_label15  = wx.StaticText(self,-1,'发货日期')
        self.order_content15  = wx.TextCtrl(self,-1)
        self.cod_fee_label = wx.StaticText(self,-1,'货到付款服务费')
        self.cod_fee_text  = wx.TextCtrl(self,-1)
        self.send_sms_label = wx.StaticText(self,-1,'已短信提醒')
        self.send_sms_check  = wx.CheckBox(self,-1)
        
        
        self.order_label16  = wx.StaticText(self,-1,'称重重量')
        self.order_content16  = wx.TextCtrl(self,-1)
        self.order_label17  = wx.StaticText(self,-1,'物流成本')
        self.order_content17  = wx.TextCtrl(self,-1)
        self.order_label18  = wx.StaticText(self,-1,'订单状态')
        self.order_content18  = wx.TextCtrl(self,-1)
        self.order_label19  = wx.StaticText(self,-1,'系统状态')
        self.order_content19  = wx.TextCtrl(self,-1)
        self.order_label20  = wx.StaticText(self,-1,'反审核次数')
        self.order_content20  = wx.SpinCtrl(self,-1,'0')
        self.cod_status_label = wx.StaticText(self,-1,'货到付款状态')
        self.cod_status_text  = wx.TextCtrl(self,-1)
        self.has_refund_label = wx.StaticText(self,-1,'有退款')
        self.has_refund_check  = wx.CheckBox(self,-1)
        
        self.order_label21  = wx.StaticText(self,-1,'买家留言')
        self.order_content21  = wx.TextCtrl(self,-1,'',size=(-1,120),style=wx.TE_MULTILINE)
        self.order_label22  = wx.StaticText(self,-1,'卖家留言')
        self.order_content22  = wx.TextCtrl(self,-1,'',size=(-1,120),style=wx.TE_MULTILINE)
        self.order_label23  = wx.StaticText(self,-1,'淘宝备注')
        self.order_content23  = wx.TextCtrl(self,-1,'',size=(-1,120),style=wx.TE_MULTILINE)
        self.order_label24  = wx.StaticText(self,-1,'反审核理由')
        self.order_content24  = wx.TextCtrl(self,-1,'',size=(-1,120),style=wx.TE_MULTILINE)
        self.order_label25  = wx.StaticText(self,-1,'系统订单备注')
        self.order_content25  = wx.TextCtrl(self,-1,'',size=(-1,120),style=wx.TE_MULTILINE)
        
        self.change_btn     = wx.Button(self,-1,'确认修改',size=(-1,40))
        
        self.__set_properties()
        self.__do_layout()
        self.__evt_bind()
        

    def __set_properties(self):
        self.SetName('basic_panel')
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
        self.control_array.append(self.order_content19)
        self.control_array.append(self.order_content20)
        self.control_array.append(self.order_content21)
        self.control_array.append(self.order_content22)
        self.control_array.append(self.order_content23)
        self.control_array.append(self.order_content24)
        self.control_array.append(self.order_content25)
        self.control_array.append(self.seller_cod_text)
        self.control_array.append(self.delivery_pick_check)
        self.control_array.append(self.buyer_cod_text)
        self.control_array.append(self.logistics_pick_check)
        self.control_array.append(self.buyer_cod_text)
        self.control_array.append(self.cod_fee_text)
        self.control_array.append(self.send_sms_check)
        self.control_array.append(self.cod_status_text)
        self.control_array.append(self.has_refund_check)
        
        logistics_companies = self.session.query(LogisticsCompany).order_by('priority desc').all()
        self.order_content13.AppendItems([company.name for company in logistics_companies])
        for control in self.control_array:
            control.Enable(False)
        self.change_btn.Hide()
        
        
            
    def __do_layout(self):
        
        base_order_sizer  = wx.GridBagSizer(hgap=5,vgap=5)
        base_order_sizer.Add(self.order_label1,pos=(0,0),span=(1,1),flag=wx.EXPAND)
        base_order_sizer.Add(self.order_content1,pos=(0,1),span=(1,1),flag=wx.EXPAND)
        base_order_sizer.Add(self.order_label2,pos=(0,2),span=(1,1),flag=wx.EXPAND)
        base_order_sizer.Add(self.order_content2,pos=(0,3),span=(1,1),flag=wx.EXPAND)
        base_order_sizer.Add(self.order_label3,pos=(0,4),span=(1,1),flag=wx.EXPAND)
        base_order_sizer.Add(self.order_content3,pos=(0,5),span=(1,1),flag=wx.EXPAND)
        base_order_sizer.Add(self.order_label4,pos=(0,6),span=(1,1),flag=wx.EXPAND)
        base_order_sizer.Add(self.order_content4,pos=(0,7),span=(1,1),flag=wx.EXPAND)
        base_order_sizer.Add(self.order_label5,pos=(0,8),span=(1,1),flag=wx.EXPAND)
        base_order_sizer.Add(self.order_content5,pos=(0,9),span=(1,1),flag=wx.EXPAND)
        base_order_sizer.Add(self.seller_cod_label,pos=(0,10),span=(1,1),flag=wx.EXPAND)
        base_order_sizer.Add(self.seller_cod_text,pos=(0,11),span=(1,1),flag=wx.EXPAND)
        base_order_sizer.Add(self.delivery_pick_label,pos=(0,12),span=(1,1),flag=wx.EXPAND)
        base_order_sizer.Add(self.delivery_pick_check,pos=(0,13),span=(1,1),flag=wx.EXPAND)
        
        base_order_sizer.Add(self.order_label6,pos=(1,0),span=(1,1),flag=wx.EXPAND)
        base_order_sizer.Add(self.order_content6,pos=(1,1),span=(1,1),flag=wx.EXPAND)
        base_order_sizer.Add(self.order_label7,pos=(1,2),span=(1,1),flag=wx.EXPAND)
        base_order_sizer.Add(self.order_content7,pos=(1,3),span=(1,1),flag=wx.EXPAND)  
        base_order_sizer.Add(self.order_label8,pos=(1,4),span=(1,1),flag=wx.EXPAND)
        base_order_sizer.Add(self.order_content8,pos=(1,5),span=(1,1),flag=wx.EXPAND)
        base_order_sizer.Add(self.order_label9,pos=(1,6),span=(1,1),flag=wx.EXPAND)
        base_order_sizer.Add(self.order_content9,pos=(1,7),span=(1,1),flag=wx.EXPAND)
        base_order_sizer.Add(self.order_label10,pos=(1,8),span=(1,1),flag=wx.EXPAND)
        base_order_sizer.Add(self.order_content10,pos=(1,9),span=(1,1),flag=wx.EXPAND)
        base_order_sizer.Add(self.buyer_cod_label,pos=(1,10),span=(1,1),flag=wx.EXPAND)
        base_order_sizer.Add(self.buyer_cod_text,pos=(1,11),span=(1,1),flag=wx.EXPAND)
        base_order_sizer.Add(self.logistics_pick_label,pos=(1,12),span=(1,1),flag=wx.EXPAND)
        base_order_sizer.Add(self.logistics_pick_check,pos=(1,13),span=(1,1),flag=wx.EXPAND)
        
        base_order_sizer.Add(self.order_label11,pos=(2,0),span=(1,1),flag=wx.EXPAND)
        base_order_sizer.Add(self.order_content11,pos=(2,1),span=(1,1),flag=wx.EXPAND)
        base_order_sizer.Add(self.order_label12,pos=(2,2),span=(1,1),flag=wx.EXPAND)
        base_order_sizer.Add(self.order_content12,pos=(2,3),span=(1,1),flag=wx.EXPAND)   
        base_order_sizer.Add(self.order_label13,pos=(2,4),span=(1,1),flag=wx.EXPAND)
        base_order_sizer.Add(self.order_content13,pos=(2,5),span=(1,1),flag=wx.EXPAND)
        base_order_sizer.Add(self.order_label14,pos=(2,6),span=(1,1),flag=wx.EXPAND)
        base_order_sizer.Add(self.order_content14,pos=(2,7),span=(1,1),flag=wx.EXPAND)
        base_order_sizer.Add(self.order_label15,pos=(2,8),span=(1,1),flag=wx.EXPAND)
        base_order_sizer.Add(self.order_content15,pos=(2,9),span=(1,1),flag=wx.EXPAND)
        base_order_sizer.Add(self.cod_fee_label,pos=(2,10),span=(1,1),flag=wx.EXPAND)
        base_order_sizer.Add(self.cod_fee_text,pos=(2,11),span=(1,1),flag=wx.EXPAND)
        base_order_sizer.Add(self.send_sms_label,pos=(2,12),span=(1,1),flag=wx.EXPAND)
        base_order_sizer.Add(self.send_sms_check,pos=(2,13),span=(1,1),flag=wx.EXPAND)
        
        base_order_sizer.Add(self.order_label16,pos=(3,0),span=(1,1),flag=wx.EXPAND)
        base_order_sizer.Add(self.order_content16,pos=(3,1),span=(1,1),flag=wx.EXPAND)
        base_order_sizer.Add(self.order_label17,pos=(3,2),span=(1,1),flag=wx.EXPAND)
        base_order_sizer.Add(self.order_content17,pos=(3,3),span=(1,1),flag=wx.EXPAND)
        base_order_sizer.Add(self.order_label18,pos=(3,4),span=(1,1),flag=wx.EXPAND)
        base_order_sizer.Add(self.order_content18,pos=(3,5),span=(1,1),flag=wx.EXPAND)
        base_order_sizer.Add(self.order_label19,pos=(3,6),span=(1,1),flag=wx.EXPAND)
        base_order_sizer.Add(self.order_content19,pos=(3,7),span=(1,1),flag=wx.EXPAND)
        base_order_sizer.Add(self.order_label20,pos=(3,8),span=(1,1),flag=wx.EXPAND)
        base_order_sizer.Add(self.order_content20,pos=(3,9),span=(1,1),flag=wx.EXPAND)
        base_order_sizer.Add(self.cod_status_label,pos=(3,10),span=(1,1),flag=wx.EXPAND)
        base_order_sizer.Add(self.cod_status_text,pos=(3,11),span=(1,1),flag=wx.EXPAND)
        base_order_sizer.Add(self.has_refund_label,pos=(3,12),span=(1,1),flag=wx.EXPAND)
        base_order_sizer.Add(self.has_refund_check,pos=(3,13),span=(1,1),flag=wx.EXPAND)
        
        base_order_sizer.Add(self.order_label21,pos=(4,0),span=(1,1),flag=wx.EXPAND)
        base_order_sizer.Add(self.order_content21,pos=(4,1),span=(1,1),flag=wx.EXPAND)
        base_order_sizer.Add(self.order_label22,pos=(4,2),span=(1,1),flag=wx.EXPAND)
        base_order_sizer.Add(self.order_content22,pos=(4,3),span=(1,1),flag=wx.EXPAND)
        base_order_sizer.Add(self.order_label23,pos=(4,4),span=(1,1),flag=wx.EXPAND)
        base_order_sizer.Add(self.order_content23,pos=(4,5),span=(1,1),flag=wx.EXPAND)
        base_order_sizer.Add(self.order_label24,pos=(4,6),span=(1,1),flag=wx.EXPAND)
        base_order_sizer.Add(self.order_content24,pos=(4,7),span=(1,1),flag=wx.EXPAND)
        base_order_sizer.Add(self.order_label25,pos=(4,8),span=(1,1),flag=wx.EXPAND)
        base_order_sizer.Add(self.order_content25,pos=(4,9),span=(1,1),flag=wx.EXPAND)
        
        base_order_sizer.Add(self.change_btn,pos=(4,11))
        base_order_sizer.Layout()
        
        self.SetSizer(base_order_sizer)
    
    def __evt_bind(self):
        self.Bind(wx.EVT_BUTTON,self.onClickChangeBtn,self.change_btn)
        
    def onClickChangeBtn(self,evt):
        company_name = self.order_content13.GetValue()
        company = self.session.query(LogisticsCompany).filter_by(name=company_name).first()
        self.session.query(MergeTrade).filter_by(tid=self.trade.tid).update({
            'is_picking_print':self.delivery_pick_check.IsChecked(),
            'is_express_print':self.logistics_pick_check.IsChecked(),
            'is_send_sms':self.send_sms_check.IsChecked(),
            'has_refund':self.has_refund_check.IsChecked(),
            'logistics_company_name':company_name,
            'out_sid':self.order_content14.GetValue(),
            'sys_memo':self.order_content25.GetValue(),
            'logistics_company_code': company.code if company else ''
            })
        for control in self.control_array:
            control.Enable(False)
        self.Parent.is_changeable = False
        self.change_btn.Hide()
    
    def setData(self,trade): 
        if not trade: 
            return 
        self.trade   = trade
        self.order_content1.SetValue(trade.seller_nick)
        self.order_content2.SetValue(TRADE_TYPE.get(trade.type,'其他'))
        self.order_content3.SetValue(str(trade.tid))
        self.order_content4.SetValue(trade.buyer_nick)
        self.order_content5.SetValue(str(trade.pay_time or '')) 
        
        self.order_content6.SetValue(trade.total_num)
        self.order_content7.SetValue(trade.total_fee)
        self.order_content8.SetValue(trade.payment)
        self.order_content9.SetValue(trade.logistics_company_code)
        self.order_content10.SetValue(trade.discount_fee)
        
        self.order_content11.SetValue(SHIPPING_TYPE.get(trade.shipping_type,'其他'))
        self.order_content12.SetValue(trade.post_fee)
        self.order_content13.SetValue(trade.logistics_company_name)
        self.order_content14.SetValue(trade.out_sid) 
        self.order_content15.SetValue(str(trade.consign_time or '')) 
        
        self.order_content16.SetValue(trade.weight)
        self.order_content17.SetValue(trade.post_cost)
        self.order_content18.SetValue(TRADE_STATUS.get(trade.status,'其他'))
        self.order_content19.SetValue(SYS_STATUS.get(trade.sys_status,'其他'))
        self.order_content20.SetValue(trade.reverse_audit_times)
        
        self.order_content21.SetValue(trade.buyer_memo)
        self.order_content22.SetValue(trade.seller_memo)
        self.order_content23.SetValue(trade.buyer_message)
        self.order_content24.SetValue(trade.reverse_audit_reason)
        self.order_content25.SetValue(trade.sys_memo)
        
        self.seller_cod_text.SetValue(trade.seller_cod_fee)
        self.buyer_cod_text.SetValue(trade.buyer_cod_fee)
        self.cod_fee_text.SetValue(trade.cod_fee)
        self.cod_status_text.SetValue(trade.cod_status)
        
        self.delivery_pick_check.SetValue(trade.is_picking_print)
        self.logistics_pick_check.SetValue(trade.is_express_print)
        self.send_sms_check.SetValue(trade.is_send_sms)
        self.has_refund_check.SetValue(trade.has_refund)
        
        for control in self.control_array:
            control.Enable(False)
        if self.Parent.is_changeable:
            self.delivery_pick_check.Enable(True)
            self.logistics_pick_check.Enable(True)
            self.send_sms_check.Enable(True)
            self.has_refund_check.Enable(True)
            self.order_content13.Enable(True)
            self.order_content14.Enable(True)
            self.order_content25.Enable(True)
            self.change_btn.Show()
        else :
            self.change_btn.Hide()
        self.Layout()
        
        
   
class DetailPanel(wx.Panel):
    
    def __init__(self,parent,id=-1):
        wx.Panel.__init__(self,parent,id)
        self.session = parent.session
        self.trade = None
        from taobao.frames.panels.gridpanel import SimpleOrdersGridPanel
        colLabels = ('商品图片','子订单ID','商品ID','商品名称','商品简称','规格编码','规格','订购数量','实际单价','实付金额',
                     '退款单号','退款费用','退款状态','退款原因','订单状态')
        self.ordergridpanel = SimpleOrdersGridPanel(self,colLabels=colLabels)
        
        self.__set_properties()
        self.__do_layout()
        
    def __set_properties(self):
        self.SetName('detail_panel')    
 
    def __do_layout(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.ordergridpanel,-1,wx.EXPAND)
        self.Layout()
        self.SetSizer(main_sizer)
        
    
    def setData(self,trade):
        if not trade:
            return
        self.trade = trade
        self.ordergridpanel.setData(trade)
        self.ordergridpanel.Layout()
        
        
class ReceiverPanel(wx.Panel):
    
    def __init__(self,parent,id=-1):
        wx.Panel.__init__(self,parent,id)
        
        self.session = parent.session
        self.trade = None
        self.order_label1  = wx.StaticText(self,-1,'收货人')
        self.order_content1  = wx.TextCtrl(self,-1)
        self.order_label2  = wx.StaticText(self,-1,'收货人固定电话')
        self.order_content2  = wx.TextCtrl(self,-1,'')
        self.order_label3  = wx.StaticText(self,-1,'收货人手机')
        self.order_content3  = wx.TextCtrl(self,-1)
        self.order_label4  = wx.StaticText(self,-1,'收货邮编')
        self.order_content4  = wx.TextCtrl(self,-1)
        self.order_label5  = wx.StaticText(self,-1,'所在省')
        self.order_content5  = wx.TextCtrl(self,-1)
        self.order_label6  = wx.StaticText(self,-1,'所在市')
        self.order_content6  = wx.TextCtrl(self,-1)
        self.order_label7  = wx.StaticText(self,-1,'所在地区')
        self.order_content7  = wx.TextCtrl(self,-1)
        self.order_label8  = wx.StaticText(self,-1,'收货人信息')
        self.order_content8 = wx.TextCtrl(self,-1)
        self.order_label9  = wx.StaticText(self,-1,'收货地址')
        self.order_content9  = wx.TextCtrl(self,-1,size=(600,-1))
        
        self.change_btn   = wx.Button(self,-1,'确认修改',size=(-1,-1))
        self.__set_properties()
        self.__do_layout()
        self.__evt_bind()
        
    def __set_properties(self):
        self.SetName('receiver_panel')
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
        self.enable_controls()
 
    def __do_layout(self):
        
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        base_order_sizer  = wx.FlexGridSizer(cols=8,hgap=10,vgap=10)
        base_order_sizer.Add(self.order_label1,0,0)
        base_order_sizer.Add(self.order_content1,0,1)
        base_order_sizer.Add(self.order_label2,0,2)
        base_order_sizer.Add(self.order_content2,0,3)
        base_order_sizer.Add(self.order_label3,0,4)
        base_order_sizer.Add(self.order_content3,0,5)
        base_order_sizer.Add(self.order_label4,0,6)
        base_order_sizer.Add(self.order_content4,0,7)
        base_order_sizer.Add(self.order_label5,1,0)
        base_order_sizer.Add(self.order_content5,1,1)
        base_order_sizer.Add(self.order_label6,1,2)
        base_order_sizer.Add(self.order_content6,1,3)
        base_order_sizer.Add(self.order_label7,1,4)
        base_order_sizer.Add(self.order_content7,1,5)
        base_order_sizer.Add(self.order_label8,1,6)
        base_order_sizer.Add(self.order_content8,1,7)
        
        box_sizer = wx.BoxSizer(wx.HORIZONTAL)
        box_sizer.Add(self.order_label9,0,flag=wx.EXPAND,border=10)
        box_sizer.Add(self.order_content9,0,flag=wx.EXPAND,border=10)
        box_sizer.Add(self.change_btn,0,flag=wx.EXPAND)
        
        main_sizer.Add(base_order_sizer,flag=wx.EXPAND,border=10)
        main_sizer.Add(box_sizer,flag=wx.EXPAND,border=10)
        self.SetSizer(main_sizer)
        
    def __evt_bind(self):
        self.Bind(wx.EVT_BUTTON,self.onClickChangeBtn,self.change_btn)
        
    def onClickChangeBtn(self,evt):
        self.session.query(MergeTrade).filter_by(tid=self.trade.tid).update({
            'receiver_name':self.order_content1.GetValue(),
            'receiver_phone':self.order_content2.GetValue(),
            'receiver_mobile':self.order_content3.GetValue(),
            'receiver_zip':self.order_content4.GetValue(),
            'receiver_state':self.order_content5.GetValue(),
            'receiver_city':self.order_content6.GetValue(),
            'receiver_district':self.order_content7.GetValue(),
            'alipay_no':self.order_content8.GetValue(),
            'receiver_address':self.order_content9.GetValue(),
        })
        self.Parent.is_changeable = False
        self.enable_controls(False)
        
    
    def enable_controls(self,is_enable=False):
        for control in self.control_array:
            control.Enable(is_enable)
        self.change_btn.Show(is_enable)
            
            
    def setData(self,trade):
        if not trade:
            return 
        self.trade = trade
        self.order_content1.SetValue(trade.receiver_name) 
        self.order_content2.SetValue(trade.receiver_phone)  
        self.order_content3.SetValue(trade.receiver_mobile)  
        self.order_content4.SetValue(trade.receiver_zip)  
        self.order_content5.SetValue(trade.receiver_state)
        self.order_content6.SetValue(trade.receiver_city)
        self.order_content7.SetValue(trade.receiver_district) 
        self.order_content8.SetValue(trade.alipay_no)  
        self.order_content9.SetValue(trade.receiver_address)  
        
        self.enable_controls(is_enable=self.Parent.is_changeable)
  
    
        
BASIC_TRADE_ID = wx.NewId()
DETAIL_TRADE_ID = wx.NewId()
RECEIVER_TRADE_ID = wx.NewId()        
class ItemPanel(wx.Panel):
    def __init__(self,parent,id=-1):
        wx.Panel.__init__(self,parent,id)
        
        self.session = parent.session
        self.parent = parent
        self.selected_trade = None
        
        self.is_changeable = False
        self.base_trade_btn = wx.Button(self,BASIC_TRADE_ID,'基本信息')
        self.detail_trade_btn = wx.Button(self,DETAIL_TRADE_ID,'商品明细')
        self.receiver_trade_btn = wx.Button(self,RECEIVER_TRADE_ID,'收货信息')
        
        self.base_trade_panel = BasicPanel(self,-1)
        self.detail_trade_panel = DetailPanel(self,-1)
        self.receiver_trade_panel = ReceiverPanel(self,-1)

        self.__set_properties()
        self.__do_layout()
        self.__evt_bind()
        

    def __set_properties(self):
        self.SetName('item_panel') 
        self.base_trade_btn.Enable(False)
        self.detail_trade_btn.Enable(True)
        self.receiver_trade_btn.Enable(True)
        self.base_trade_panel.Show()
        self.detail_trade_panel.Hide()
        self.receiver_trade_panel.Hide()    
        
    def __do_layout(self):
        trade_btn_sizer = wx.FlexGridSizer(hgap=5,vgap=5)
        box_sizer       = wx.BoxSizer(wx.VERTICAL)
        
        trade_btn_sizer.Add(self.base_trade_btn,0,0)
        trade_btn_sizer.Add(self.detail_trade_btn,0,1)
        trade_btn_sizer.Add(self.receiver_trade_btn,0,2)
        
        box_sizer.Add(trade_btn_sizer,proportion=0,flag=wx.EXPAND|wx.ALL)
        box_sizer.Add(self.base_trade_panel,proportion=0,flag=wx.EXPAND|wx.ALL)
        box_sizer.Add(self.detail_trade_panel,proportion=0,flag=wx.EXPAND|wx.ALL)
        box_sizer.Add(self.receiver_trade_panel,proportion=0,flag=wx.EXPAND|wx.ALL)
        self.SetSizer(box_sizer)
    
    def __evt_bind(self):
        self.Bind(wx.EVT_BUTTON, self.OnChangeContentPane, id=BASIC_TRADE_ID)
        self.Bind(wx.EVT_BUTTON, self.OnChangeContentPane, id=DETAIL_TRADE_ID)
        self.Bind(wx.EVT_BUTTON, self.OnChangeContentPane, id=RECEIVER_TRADE_ID)
    
    def OnChangeContentPane(self,event):
        eventid = event.GetId()
        if eventid == BASIC_TRADE_ID:
            self.base_trade_panel.setData(self.selected_trade)
        elif eventid == DETAIL_TRADE_ID:
            self.detail_trade_panel.setData(self.selected_trade)
        elif eventid == RECEIVER_TRADE_ID:
            self.receiver_trade_panel.setData(self.selected_trade)
        
        self.base_trade_btn.Enable(not eventid==BASIC_TRADE_ID)
        self.detail_trade_btn.Enable(not eventid==DETAIL_TRADE_ID)
        self.receiver_trade_btn.Enable(not eventid==RECEIVER_TRADE_ID)
        
        self.detail_trade_panel.Show(eventid == DETAIL_TRADE_ID)
        self.base_trade_panel.Show(eventid == BASIC_TRADE_ID)
        self.receiver_trade_panel.Show(eventid == RECEIVER_TRADE_ID)
        self.Layout()
        
    def refreshData(self):
        self.is_changeable = True
        self.base_trade_panel.setData(self.selected_trade)
        self.detail_trade_panel.setData(self.selected_trade)
        self.receiver_trade_panel.setData(self.selected_trade)
        self.Layout()
        
    def setData(self,trade_id):
        self.is_changeable = False
        session = self.parent.session
        self.selected_trade = session.query(MergeTrade).filter_by(tid=trade_id).one()
        self.base_trade_panel.setData(self.selected_trade)
        self.detail_trade_panel.setData(self.selected_trade)
        self.receiver_trade_panel.setData(self.selected_trade)
        self.Layout()
        