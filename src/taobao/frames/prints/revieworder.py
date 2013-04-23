#-*- coding:utf8 -*-
#######################################################################
# revieworder.py
#
# Created: 8/5/2012 by mld
#
# Description: 复审订单
#######################################################################
#-*- coding:utf8 -*- 
import datetime
import wx
import wx.lib.iewin as iewin
from taobao.common.utils import getconfig
from taobao.common.utils import create_session
from taobao.common.environment import get_template
from taobao.dao.models import MergeTrade,MergeOrder,Product,ProductSku
from taobao.dao.tradedao import get_used_orders

FONTSIZE = 10
  
 
class OrderReview(wx.Frame):
 
    #----------------------------------------------------------------------
    def __init__(self,parent=None, title=u'订单复审', trade_id=None):
        wx.Frame.__init__(self, parent, wx.ID_ANY, title, size=(850,500))
 
        self.panel    = wx.Panel(self, wx.ID_ANY)
        #self.printer = HtmlPrinter(name=u'打印', parentWindow=self)
        self.trade_id = trade_id
        self.html = iewin.IEHtmlWindow(self.panel,-1)
        #trade_ids = [200165044022938,165155430754126]
         
        cfg  = getconfig()
        self.html.LoadUrl(cfg.get('url','review_url')%trade_id)
        
        previewExpressBtn = wx.Button(self.panel,wx.ID_ANY,u'物流单打印预览')
        previewDeliveryBtn = wx.Button(self.panel,wx.ID_ANY,u'发货单打印预览')
        cancelBtn = wx.Button(self.panel, wx.ID_ANY, u'关闭窗口')
        
        self.Bind(wx.EVT_BUTTON, self.onExpressPreview, previewExpressBtn)
        self.Bind(wx.EVT_BUTTON, self.onDeliveryPreview, previewDeliveryBtn)
        self.Bind(wx.EVT_BUTTON, self.onCancel, cancelBtn)

        #监听打印预览菜单项
        #self.panel.Bind(wx.EVT_MENU, self.onSelectMenu)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
 
        sizer.Add(self.html, 1, wx.GROW)
        
        btnSizer.Add(previewExpressBtn, 0, wx.ALL|wx.CENTER, 5)
        btnSizer.Add(previewDeliveryBtn, 0, wx.ALL|wx.CENTER, 5)
        btnSizer.Add(cancelBtn, 0, wx.ALL|wx.CENTER, 5)
        sizer.Add(btnSizer,0,wx.ALL|wx.CENTER,5)
 
        self.panel.SetSizer(sizer)
        self.panel.SetAutoLayout(True)
    
 
    #----------------------------------------------------------------------
    def onExpressPreview(self,event):
        """"""
        html_text = self.createExpressHtml([self.trade_id])
        self.html.LoadString(html_text)
        self.html.PrintPreview()
        with create_session(self.Parent) as session:
            session.query(MergeTrade).filter_by(id=self.trade_id).update({MergeTrade.is_express_print:True})
        event.Skip()
        
    #----------------------------------------------------------------------
    def onDeliveryPreview(self,event):
        """"""
        html_text = self.createPickingHtml([self.trade_id])
        self.html.LoadString(html_text)
        self.html.PrintPreview()
        with create_session(self.Parent) as session:
            session.query(MergeTrade).filter_by(id=self.trade_id).update({MergeTrade.is_picking_print:True})
        event.Skip()
 
    #----------------------------------------------------------------------
    def onCancel(self, event):
        self.Close()
 
    #----------------------------------------------------------------------
    def createExpressHtml(self,trade_ids=[]):
        '''
        Creates an html file in the home directory of the application
        that contains the information to display the snapshot
        '''
        try:
            trades = self.getLogisticsData(trade_ids)
            template_name = 'logistics_%s_template.html'%trades[0]['company_code'].lower()
            template = get_template(template_name) 
            html = template.render(trades=trades)
        except:
            html = u'<html><head></head><body style="text-align:center;">对不起，你还没有添加%s的物流单模板。</body></html>'%trades[0]['company_name']
        return html
 
    #----------------------------------------------------------------------
    def createPickingHtml(self,trade_ids=[]):
        '''
        Creates an html file in the home directory of the application
        that contains the information to display the snapshot
        '''
 
        trades = self.getTradePickingData(trade_ids)
        template = get_template('trade_picking_template.html') 
        html =template.render(trades=trades)

        return html
    
    #----------------------------------------------------------------------
    def getTradePickingData(self ,trade_ids=[]):
        
        with create_session(self.Parent) as session: 
            send_trades  = session.query(MergeTrade).filter(MergeTrade.id.in_(trade_ids)).order_by('out_sid')
        
            picking_data_list = []
            for trade in send_trades[0:1]:
                trade_data = {}
                dt         = datetime.datetime.now() 
                        
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
                
                order_items = {}
                orders = get_used_orders(session,trade.id)  
                for order in orders:
                    
                    trade_data['order_nums']     += order.num
                    trade_data['discount_fee']   += float(order.discount_fee or 0)
                    trade_data['total_fee']      += float(order.total_fee or 0) 
                    trade_data['payment']      += float(order.payment or 0)
                    
                    outer_id = order.outer_id or str(order.num_iid)
                    outer_sku_id = order.outer_sku_id or str(order.sku_id)
                    
                    if order_items.has_key(outer_id):
                        order_items[outer_id]['num'] += order.num
                        skus = order_items[outer_id]['skus']
                        if skus.has_key(outer_sku_id):
                            skus[outer_sku_id]['num'] += order.num
                        else:
                            product  = session.query(Product).filter_by(outer_id=order.outer_id).first()
                            prod_sku = session.query(ProductSku).filter_by(outer_id=order.outer_sku_id,product=product).first()
                            prod_sku_name = (prod_sku.properties_alias or prod_sku.properties_name ) if prod_sku else order.sku_properties_name
                            skus[outer_sku_id] = {'sku_name':prod_sku_name,'num':order.num}
                    else:
                        product  = session.query(Product).filter_by(outer_id=order.outer_id).first()
                        prod_sku = session.query(ProductSku).filter_by(outer_id=order.outer_sku_id,product=product).first()
                        prod_sku_name =prod_sku.properties_name if prod_sku else order.sku_properties_name
                        
                        order_items[outer_id]={
                                               'num':order.num,
                                               'title': product.name if product else order.title,
                                               'skus':{outer_sku_id:{'sku_name':prod_sku_name,'num':order.num}}
                                               }
                    
                order_list = sorted(order_items.items(),key=lambda d:d[1]['num'],reverse=True)
                for trade in order_list:
                    skus = trade[1]['skus']
                    trade[1]['skus'] = sorted(skus.items(),key=lambda d:d[1]['num'],reverse=True)    
                
                trade_data['orders'] = order_list    
                picking_data_list.append(trade_data)
                                           
        return picking_data_list
    
    
    #----------------------------------------------------------------------
    def getLogisticsData(self ,trade_ids=[]):
        with create_session(self.Parent) as session: 
            send_trades  = session.query(MergeTrade).filter(MergeTrade.id.in_(trade_ids)).order_by('out_sid')
        
        express_data_list = []
        for trade in send_trades:
            trade_data = {}
            dt         = datetime.datetime.now() 
                    
            trade_data['trade_id']     = trade.id
            trade_data['seller_nick']  = trade.seller_nick
            trade_data['seller_contacter']  = trade.user.contacter
            trade_data['seller_phone']  = trade.user.phone
            trade_data['seller_mobile']  = trade.user.mobile
            trade_data['seller_area_code']  = trade.user.area_code
            trade_data['seller_location']  = trade.user.location
            
            trade_data['post_date']    = dt
            trade_data['buyer_nick']        = trade.buyer_nick
            trade_data['out_sid']      = trade.out_sid
            trade_data['company_name'] = trade.logistics_company.name
            trade_data['company_code'] = trade.logistics_company.code
            
            trade_data['receiver_name']     = trade.receiver_name
            trade_data['receiver_phone']    = trade.receiver_phone
            trade_data['receiver_mobile']   = trade.receiver_mobile
            trade_data['receiver_zip']      = trade.receiver_zip
            
            trade_data['receiver_state']    = trade.receiver_state
            trade_data['receiver_city']     = trade.receiver_city
            trade_data['receiver_district'] = trade.receiver_district
            trade_data['receiver_address']  = trade.receiver_address
            
            express_data_list.append(trade_data)
                               
        return express_data_list
    
    

