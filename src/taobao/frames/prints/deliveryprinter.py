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
from taobao.common.utils import create_session,format_datetime
from taobao.common.regedit import updatePageSetupRegedit
from taobao.dao.models import MergeTrade,MergeOrder,Product,ProductSku
from taobao.dao.tradedao import get_used_orders,get_product_locations
from taobao.dao.configparams import SYS_STATUS_PREPARESEND,NO_REFUND,REFUND_CLOSED,SELLER_REFUSE_BUYER,\
    IN_EFFECT,EXPRESS_CELL_COL,PICKLE_CELL_COL,TRADE_ID_CELL_COL,JUHUASUAN_CODE
from taobao.common.utils import IMAGE_ROOT,TEMP_FILE_ROOT

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
 
        self.html = iewin.IEHtmlWindow(self.panel,-1)
        #trade_ids = [200165044022938,165155430754126]
       
        html_text = self.createHtml(trade_ids)
        #self.saveHtml2File(html_text,len(trade_ids))
        self.html.LoadString(html_text)
        
        previewBtn = wx.Button(self.panel,wx.ID_ANY,u'打印预览')
        #printBtn = wx.Button(self.panel,wx.ID_ANY,u'打印')
        cancelBtn = wx.Button(self.panel, wx.ID_ANY, u'关闭窗口')
        
        self.Bind(wx.EVT_BUTTON, self.onPreview, previewBtn)
        #self.Bind(wx.EVT_BUTTON, self.onPrint, printBtn)
        self.Bind(wx.EVT_BUTTON, self.onCancel, cancelBtn)
 
        sizer = wx.BoxSizer(wx.VERTICAL)
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
 
        sizer.Add(self.html, 1, wx.GROW)
        btnSizer.Add(previewBtn, 0, wx.ALL|wx.CENTER, 5)
        #btnSizer.Add(printBtn, 0, wx.ALL|wx.CENTER, 5)
        btnSizer.Add(cancelBtn, 0, wx.ALL|wx.CENTER, 5)
        sizer.Add(btnSizer,0,wx.ALL|wx.CENTER,5)
 
        self.panel.SetSizer(sizer)
        self.panel.SetAutoLayout(True)
 
    #----------------------------------------------------------------------
    def createHtml(self,trade_ids=[]):
        '''
        Creates an html file in the home directory of the application
        that contains the information to display the snapshot
        '''
        with create_session(self.Parent) as session: 
            trade_user_code = session.query(MergeTrade).filter_by(id=trade_ids[0])\
                .one().user.user_code.lower()
        
        trades = self.getTradePickingData(trade_ids)
        try:
            template = get_template('invoice/invoice_%s_template.html'%trade_user_code) 
            html =template.render(trades=trades)
        except:
            return u'<center>模板异常</center>'
        return html

    def getPageSetup(self):
        return {'margin_top':'0.393700',
                'margin_bottom':'0.393700',
                'margin_left':'0.629920',
                'margin_right':'0.393700',
                'footer':'',
                'header':''}
    
    #----------------------------------------------------------------------
    def onPrint(self, event):
        
        with create_session(self.Parent) as session: 
            session.query(MergeTrade).filter(MergeTrade.id.in_(self.trade_ids))\
                .update({'is_picking_print':True},synchronize_session='fetch') 
                
        self.html.Print(True)
        event.Skip() 
 
    #----------------------------------------------------------------------
    def onPreview(self,event):
        """"""
        with create_session(self.Parent) as session: 
            trades = session.query(MergeTrade).filter(MergeTrade.id.in_(self.trade_ids)).filter_by(is_picking_print=True)
            rept_num = trades.count()
            if rept_num > 0:
                dial = wx.MessageDialog(None, u'该批订单有（%d）单已打印发货单，还要继续吗？'%rept_num, u'发货单重打提示', 
                                        wx.OK|wx.CANCEL|wx.ICON_EXCLAMATION)
                result = dial.ShowModal()
                dial.Destroy()
                
                #如果不继续，则退出
                if result != wx.ID_OK:
                    return 
                    
            session.query(MergeTrade).filter(MergeTrade.id.in_(self.trade_ids))\
                .update({'is_picking_print':True},synchronize_session='fetch')
                
        updatePageSetupRegedit(self.getPageSetup())
        
        self.html.PrintPreview()
        #self.Parent.refreshTable() 
        event.Skip()
 
    #----------------------------------------------------------------------
    def onCancel(self, event):
        with create_session(self.Parent) as session:
            grid = self.Parent.grid
            rows = self.Parent.grid.GetNumberRows()
            
            for row in xrange(0,rows):
                trade_id = grid.GetCellValue(row,TRADE_ID_CELL_COL)
                trade = session.query(MergeTrade).filter_by(id=trade_id).first()
                grid.SetCellValue(row,PICKLE_CELL_COL,trade.is_picking_print and '1' or '')
                
        self.Parent.grid.ForceRefresh()
        self.Close()
    
    #----------------------------------------------------------------------
    def saveHtml2File(self,html_text,nums):
        
        dt = datetime.datetime.now()
        file_name = TEMP_FILE_ROOT+'fahuodan(%d)-%s.html'%(nums,format_datetime(dt,format="%Y.%m.%d %H.%M.%S"))
        with open(file_name,'w') as f:
            print >> f,html_text
    

    #----------------------------------------------------------------------
    def getTradePickingData(self ,trade_ids=[]):
        
        with create_session(self.Parent) as session: 
            send_trades  = session.query(MergeTrade).filter(MergeTrade.id.in_(trade_ids)).order_by('out_sid')
            dt         = datetime.datetime.now() 
            picking_data_list = []
            for trade in send_trades:
                trade_data = {}
                
                trade_data['trade_id']     = trade.id
                trade_data['seller_nick']  = trade.seller_nick
                trade_data['post_date']    = dt
                trade_data['pay_time']    = trade.pay_time
                trade_data['buyer_nick']   = trade.buyer_nick
                trade_data['out_sid']      = trade.out_sid
                trade_data['company_name'] = trade.logistics_company and trade.logistics_company.name
                trade_data['order_nums']   = 0
                trade_data['total_fee']    = 0
                trade_data['discount_fee'] = 0
                trade_data['payment']      = 0
                trade_data['buyer_prompt']  = ''
                trade_data['juhuasuan']  = trade.trade_from&JUHUASUAN_CODE == JUHUASUAN_CODE
                
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
                trade_data['buyer_prompt']   = ''
                
                prompt_set = set()
                order_items = {}
                orders = get_used_orders(session,trade.id)  
                for order in orders:
                    
                    trade_data['order_nums']     += order.num
                    trade_data['discount_fee']   += float(order.discount_fee or 0)
                    trade_data['total_fee']      += float(order.total_fee or 0) 
                    trade_data['payment']        += float(order.payment or 0)
                    
                    outer_id = order.outer_id or str(order.num_iid)
                    outer_sku_id = order.outer_sku_id or str(order.sku_id)
                    
                    product  = session.query(Product).filter_by(outer_id=order.outer_id).first()
                    prod_sku = session.query(ProductSku).filter_by(outer_id=order.outer_sku_id,product=product).first()
                    
                    product_id = product.id
                    sku_id     = prod_sku and prod_sku.id
                    
                    promptmsg = (prod_sku and prod_sku.buyer_prompt) or (product and product.buyer_prompt) or ''
                    if promptmsg:
                        prompt_set.add(promptmsg)
                    
                    if order_items.has_key(outer_id):
                        order_items[outer_id]['num'] += order.num
                        skus = order_items[outer_id]['skus']
                        if skus.has_key(outer_sku_id):
                            skus[outer_sku_id]['num'] += order.num
                        else:   
                            prod_sku_name = prod_sku and prod_sku.name or order.sku_properties_name
                            skus[outer_sku_id] = {'sku_name':prod_sku_name,
                                                  'num':order.num,
                                                  'location':get_product_locations(product_id,sku_id,session=session)}
                    else:
                        prod_sku_name = prod_sku and prod_sku.name or order.sku_properties_name
                        order_items[outer_id]={
                                               'num':order.num,
                                               'location':get_product_locations(product_id,opn=True,session=session),
                                               'title': product.name if product else order.title,
                                               'skus':{outer_sku_id:{'sku_name':prod_sku_name,
                                                                     'num':order.num,
                                                                     'location':get_product_locations(product_id,sku_id,session=session)}}
                                               }
                trade_data['buyer_prompt'] = prompt_set and ','.join(list(prompt_set)) or ''   
                order_list = sorted(order_items.items(),key=lambda d:d[1]['location'])
                for trade in order_list:
                    skus = trade[1]['skus']
                    trade[1]['skus'] = sorted(skus.items(),key=lambda d:d[1]['location'])    
                
                trade_data['orders'] = order_list    
                picking_data_list.append(trade_data)
                                           
        return picking_data_list    
