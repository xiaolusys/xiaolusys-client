#-*- coding:utf8 -*-
#######################################################################
# logisticsprinter.py
#
# Created: 8/5/2012 by mld
#
# Description: 打印物流单操作窗口
#######################################################################
 
import os,os.path
import wx
import wx.lib.iewin as iewin
import time
import datetime
from wx.html import HtmlEasyPrinting,HtmlWindow 
from taobao.common.environment import get_template
from taobao.dao.dbsession import get_session
from taobao.dao.models import Trade, MergeTrade,Item,Order,SubPurchaseOrder,FenxiaoProduct
from taobao.dao.configparams import SYS_STATUS_PREPARESEND ,TRADE_STATUS_WAIT_SEND_GOODS

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
  
 
class ExpressPrinter(wx.Frame):
 
    #----------------------------------------------------------------------
    def __init__(self,parent=None, title='打印发货单',trade_ids=[]):
        wx.Frame.__init__(self, parent, wx.ID_ANY, title, size=(850,500))
 
        self.panel = wx.Panel(self, wx.ID_ANY)
        self.printer = HtmlPrinter(name='打印', parentWindow=None)
 
        self.html = iewin.IEHtmlWindow(self.panel)
        #trade_ids = [200165044022938,165155430754126]
        html_text = self.createHtml(trade_ids)
        self.html.LoadString(html_text)
 
        mention = wx.StaticText(self.panel,wx.ID_ANY,'(请点击鼠标右键选择打印预览)')
        cancelBtn = wx.Button(self.panel, wx.ID_ANY, '取消打印')
 
        self.Bind(wx.EVT_BUTTON, self.onCancel, cancelBtn)
 
        sizer = wx.BoxSizer(wx.VERTICAL)
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
 
        sizer.Add(self.html, 1, wx.GROW)
        btnSizer.Add(mention, 0, wx.ALL, 5)
        btnSizer.Add(cancelBtn, 0, wx.ALL, 5)
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

        template = get_template('logistics_template.html') 
        html =template.render(trades=trades)

        return html


    #----------------------------------------------------------------------
    def onPrint(self, event):
        self.sendToPrinter()
 
    #----------------------------------------------------------------------
    def sendToPrinter(self):
        """"""
        self.printer.GetPrintData().SetPaperId(wx.PAPER_LETTER)
        self.printer.PrintText(self.html.GetText(True),'发货单')
 
    #----------------------------------------------------------------------
    def onCancel(self, event):
        self.Close()
 
    #----------------------------------------------------------------------
    def getLogisticsData(self ,trade_ids=[]):
        session = get_session()
        send_trades  = session.query(MergeTrade).filter(MergeTrade.tid.in_(trade_ids))
        
        picking_data_list = []
        for trade in send_trades:
            trade_data = {}
            dt         = datetime.datetime.now() 
                    
            trade_data['trade_id']     = trade.tid
            trade_data['seller_nick']  = trade.seller_nick
            trade_data['post_date']    = dt
            trade_data['buyer_nick']        = trade.buyer_nick
            trade_data['out_sid']      = trade.out_sid
            trade_data['company_name'] = trade.logistics_company_name
            trade_data['order_nums']   = 0
            trade_data['total_fee']    = trade.total_fee
            trade_data['discount_fee'] = 0
            trade_data['payment']      = trade.payment
            
            trade_data['receiver_name']     = trade.receiver_name
            trade_data['receiver_phone']    = trade.receiver_phone
            trade_data['receiver_mobile']   = trade.receiver_mobile
            
            trade_data['receiver_state']    = trade.receiver_state
            trade_data['receiver_city']     = trade.receiver_city
            trade_data['receiver_district'] = trade.receiver_district
            trade_data['receiver_address']  = trade.receiver_address
            trade_data['sys_memo']   = trade.sys_memo
            trade_data['orders']       = [] 
                               
        return picking_data_list    
    

