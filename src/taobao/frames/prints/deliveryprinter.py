#-*- coding:utf8 -*-
#######################################################################
# deliveryprinter.py
#
# Created: 8/5/2012 by mld
#
# Description: Displays screenshot image using html and then allows
#              the user to print it.
#######################################################################
 
import os,os.path
import wx
import wx.lib.iewin as iewin
import time
import datetime
from wx.html import HtmlEasyPrinting,HtmlWindow 
from taobao.common.environment import get_template
from taobao.common.utils import create_session
from taobao.dao.models import MergeTrade,MergeOrder,Product
from taobao.dao.tradedao import get_used_orders
from taobao.dao.configparams import SYS_STATUS_PREPARESEND,NO_REFUND,REFUND_CLOSED,SELLER_REFUSE_BUYER,IN_EFFECT

from taobao.common.utils import IMAGE_ROOT

FONTSIZE = 10
 
class HtmlPrinter(HtmlEasyPrinting):
    def __init__(self,*args,**kwargs):
        HtmlEasyPrinting.__init__(self,*args,**kwargs)
        

    def GetHtmlText(self,text):
        "Simple conversion of text.  Use a more powerful version"
        return text

    def PrintText(self, text, doc_name):
        self.SetHeader(doc_name)
        self.SetFooter('@PAGENUM@/@PAGESCNT@')
        return HtmlEasyPrinting.PrintText(self,self.GetHtmlText(text),doc_name)

    def PreviewText(self, text, doc_name):
        self.SetHeader(doc_name)
        HtmlEasyPrinting.SetStandardFonts(self,FONTSIZE)
        self.SetFooter('@PAGENUM@/@PAGESCNT@')
        return HtmlEasyPrinting.PreviewText(self, self.GetHtmlText(text))
  
 
class DeliveryPrinter(wx.Frame):
 
    #----------------------------------------------------------------------
    def __init__(self,parent=None, title=u'打印发货单',trade_ids=[]):
        wx.Frame.__init__(self, parent, wx.ID_ANY, title, size=(850,500))
        
        self.trade_ids = trade_ids
        self.panel = wx.Panel(self, wx.ID_ANY)
        self.printer = HtmlPrinter(name=u'打印', parentWindow=None)
 
        self.html = iewin.IEHtmlWindow(self.panel)
        #trade_ids = [200165044022938,165155430754126]
        html_text = self.createHtml(trade_ids)
        self.html.LoadString(html_text)
 
        mention = wx.StaticText(self.panel,wx.ID_ANY,u'(请点击鼠标右键选择打印预览)')
        cancelBtn = wx.Button(self.panel, wx.ID_ANY, u'取消打印')
        deliveryBtn = wx.Button(self.panel, wx.ID_ANY, u'更新已打印发货单状态')
        
        self.Bind(wx.EVT_BUTTON, self.onCancel, cancelBtn)
        self.Bind(wx.EVT_BUTTON, self.onUpdateDeliveryStatus, deliveryBtn)
 
        sizer = wx.BoxSizer(wx.VERTICAL)
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
 
        sizer.Add(self.html, 1, wx.GROW)
        btnSizer.Add(mention, 0, wx.ALL, 5)
        btnSizer.Add(cancelBtn, 0, wx.ALL, 5)
        btnSizer.Add(deliveryBtn, 1, wx.ALL|wx.RIGHT, 5)
        sizer.Add(btnSizer)
 
        self.panel.SetSizer(sizer)
        self.panel.SetAutoLayout(True)
 
    #----------------------------------------------------------------------
    def createHtml(self,trade_ids=[]):
        '''
        Creates an html file in the home directory of the application
        that contains the information to display the snapshot
        '''
 
        trades = self.getTradePickingData(trade_ids)

        template = get_template('trade_picking_template.html') 
        html =template.render(trades=trades)

        return html


    #----------------------------------------------------------------------
    def onPrint(self, event):
        self.sendToPrinter()
 
    #----------------------------------------------------------------------
    def sendToPrinter(self):
        """"""
        self.printer.GetPrintData().SetPaperId(wx.PAPER_LETTER)
        self.printer.PrintText(self.html.GetText(True),u'发货单')
 
    #----------------------------------------------------------------------
    def onCancel(self, event):
        self.Close()
 
    #----------------------------------------------------------------------
    def onUpdateDeliveryStatus(self,event):
        with create_session(self.Parent) as session: 
            session.query(MergeTrade).filter(MergeTrade.id.in_(self.trade_ids))\
                .update({'is_picking_print':True},synchronize_session='fetch')

    #----------------------------------------------------------------------
    def getTradePickingData(self ,trade_ids=[]):
        
        with create_session(self.Parent) as session: 
            send_trades  = session.query(MergeTrade).filter(MergeTrade.id.in_(trade_ids))
        
            picking_data_list = []
            for trade in send_trades:
                trade_data = {}
                dt         = datetime.datetime.now() 
                        
                trade_data['trade_serial'] = int(time.time()*100%10000000)
                trade_data['trade_id']     = trade.id
                trade_data['seller_nick']  = trade.seller_nick
                trade_data['post_date']    = dt
                trade_data['buyer_nick']   = trade.buyer_nick
                trade_data['out_sid']      = trade.out_sid
                trade_data['company_name'] = trade.logistics_company.name
                trade_data['order_nums']   = 0
                trade_data['total_fee']    = 0
                trade_data['discount_fee'] = 0
                trade_data['payment']      = 0
                
                
                trade_data['receiver_name']     = trade.receiver_name
                trade_data['receiver_phone']    = trade.receiver_phone
                trade_data['receiver_mobile']   = trade.receiver_mobile
                
                trade_data['receiver_state']    = trade.receiver_state
                trade_data['receiver_city']     = trade.receiver_city
                trade_data['receiver_district'] = trade.receiver_district
                trade_data['receiver_address']  = trade.receiver_address
                trade_data['buyer_message']   = trade.buyer_message
                trade_data['seller_memo']   = trade.seller_memo
                trade_data['sys_memo']   = trade.sys_memo
                trade_data['orders']       = [] 
                
                orders = get_used_orders(session,trade.id)  
                for order in orders:
                    order_data = {} 
                    product = session.query(Product).filter_by(outer_id=order.outer_id).one()
                    trade_data['order_nums']     += order.num
                    trade_data['discount_fee']   += float(order.discount_fee or 0)
                    trade_data['total_fee']      += float(order.total_fee or 0) 
                    trade_data['payment']      += float(order.payment or 0)
                    order_data['outer_id']  = order.outer_id 
                    order_data['item_name'] = product.name
                    order_data['num']       = order.num
                    order_data['price']     = order.price
                    order_data['discount_fee'] = float(order.discount_fee or 0)
                    order_data['payment']   = order.payment 
                    order_data['properties'] = order.sku_properties_name
                    
                    trade_data['orders'].append(order_data)

                picking_data_list.append(trade_data)
                                           
        return picking_data_list    
