#-*- coding:utf8 -*-
#######################################################################
# logisticsprinter.py
#
# Created: 8/5/2012 by meixqhi
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
from taobao.common.utils import create_session,format_datetime
from taobao.common.regedit import updatePageSetupRegedit
from taobao.dao.models import MergeTrade,Item,MergeOrder,ClassifyZone
from taobao.dao.configparams import (SYS_STATUS_PREPARESEND ,
                                     TRADE_STATUS_WAIT_SEND_GOODS,
                                     EXPRESS_CELL_COL,
                                     PICKLE_CELL_COL,
                                     TRADE_ID_CELL_COL,
                                     YUNDA_CODE)
from taobao.dao.yundao import get_classify_zone,get_zone_by_code
from taobao.common.utils import TEMP_FILE_ROOT


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
    def __init__(self,parent=None, title=u'打印快递单',trade_ids=[]):
        wx.Frame.__init__(self, parent, wx.ID_ANY, title, size=(850,500))
        
        self.trade_ids = trade_ids
        self.panel = wx.Panel(self, wx.ID_ANY)
        self.printed = False
        #self.printer = HtmlPrinter(name=u'打印', parentWindow=self)
 
        self.html = iewin.IEHtmlWindow(self.panel,-1)
        #trade_ids = [200165044022938,165155430754126]
        
        html_text = self.createHtml(trade_ids)
        #self.saveHtml2File(html_text,len(trade_ids))
        #self.printer.PreviewText(html_text, u'物流单')
        self.html.LoadString(html_text)
        
        previewBtn = wx.Button(self.panel,wx.ID_ANY,u'打印预览')
        cancelBtn = wx.Button(self.panel, wx.ID_ANY, u'关闭窗口')
        
        self.Bind(wx.EVT_BUTTON, self.onPreview, previewBtn)
        self.Bind(wx.EVT_BUTTON, self.onCancel, cancelBtn)

        #监听打印预览菜单项
        #self.panel.Bind(wx.EVT_MENU, self.onSelectMenu)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
 
        sizer.Add(self.html, 1, wx.GROW)
        
        btnSizer.Add(previewBtn, 0, wx.ALL|wx.CENTER, 5)
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
        trades = self.getLogisticsData(trade_ids)
        try:
            template_name = 'logistic/logistics_%s_template.html'%trades[0]['company_code'].lower()
            template = get_template(template_name) 
            html = template.render(trades=trades)
        except:
            html = u'<html><head></head><body style="text-align:center;">对不起，你还没有添加%s的物流单模板。</body></html>'%trades[0]['company_name']
        return html
    
    
    def getPageSetup(self):
        return {'margin_top':'0.393700',
                'margin_bottom':'0.629920',
                'margin_left':'0.393700',
                'margin_right':'0.393700',
                'footer':'',
                'header':''}
    
    #----------------------------------------------------------------------
    def onPrint(self, event):
        
        with create_session(self.Parent) as session: 
            session.query(MergeTrade).filter(MergeTrade.id.in_(self.trade_ids))\
                .update({'is_express_print':True},synchronize_session='fetch')
                
        self.html.Print(True)
        event.Skip() 
 
    #----------------------------------------------------------------------
    def onPreview(self,event):
        """"""
        with create_session(self.Parent) as session: 
            trades = session.query(MergeTrade).filter(MergeTrade.id.in_(self.trade_ids)).filter_by(is_express_print=True)
            rept_num = trades.count()
            if rept_num > 0:
                dial = wx.MessageDialog(None, u'该批订单有（%d）单已打印快递单，还要继续吗？'%rept_num, u'快递单重打提示', 
                                        wx.OK|wx.CANCEL|wx.ICON_EXCLAMATION)
                result = dial.ShowModal()
                dial.Destroy()
                
                #如果不继续，则退出
                if result != wx.ID_OK:
                    return 
        
            session.query(MergeTrade).filter(MergeTrade.id.in_(self.trade_ids))\
                .update({'is_express_print':True},synchronize_session='fetch')
            
            self.printed = True
            
        updatePageSetupRegedit(self.getPageSetup())
        
        self.html.PrintPreview()
        #self.Parent.refreshTable()  
        event.Skip()
    
    #----------------------------------------------------------------------
    def saveHtml2File(self,html_text,nums):
        
        dt = datetime.datetime.now()
        file_name = TEMP_FILE_ROOT+'kuaididan(%d)-%s.html'%(nums,format_datetime(dt,format="%Y.%m.%d %H.%M.%S"))
        with open(file_name,'w') as f:
            print >> f,html_text.encode('gbk')
    
    #----------------------------------------------------------------------
    def onCancel(self, event):
        """ onCancel """
        grid = self.Parent.grid
        rows = self.Parent.grid.GetNumberRows()
        
        for row in xrange(0,rows):
            grid.SetCellValue(row,EXPRESS_CELL_COL,self.printed and '1' or '')
                    
        self.Parent.grid.ForceRefresh()
        self.Close()
 
    
    #----------------------------------------------------------------------
    def getLogisticsData(self ,trade_ids=[]):
        
        with create_session(self.Parent) as session: 
            send_trades  = session.query(MergeTrade).filter(MergeTrade.id.in_(trade_ids)).order_by('out_sid')
        
            express_data_list = []
            for trade in send_trades:
                trade_data = {}
                dt         = datetime.datetime.now() 
                        
                trade_data['trade_id']     = trade.id
                trade_data['seller_nick']  = trade.user.nick
                trade_data['seller_contacter']  = trade.user.contacter
                trade_data['seller_phone']      = trade.user.phone
                trade_data['seller_mobile']     = trade.user.mobile
                trade_data['seller_area_code']  = trade.user.area_code
                trade_data['seller_location']   = trade.user.location
                
                trade_data['post_date']    = dt
                trade_data['buyer_nick']   = trade.buyer_nick
                trade_data['out_sid']      = trade.out_sid
                trade_data['company_name'] = (trade.logistics_company and 
                                              trade.logistics_company.name or 'NULL')
                trade_data['company_code'] = (trade.logistics_company and 
                                              trade.logistics_company.code or 'NULL')
                
                trade_data['receiver_name']     = trade.receiver_name
                trade_data['receiver_phone']    = trade.receiver_phone
                trade_data['receiver_mobile']   = trade.receiver_mobile
                trade_data['receiver_zip']      = trade.receiver_zip
                
                trade_data['receiver_state']    = trade.receiver_state
                trade_data['receiver_city']     = trade.receiver_city
                trade_data['receiver_district'] = trade.receiver_district
                trade_data['receiver_address']  = trade.receiver_address
                
                trade_data['zone'] = ''
                if trade_data['company_code'].upper() in YUNDA_CODE:
                    zone = None

                    #if trade.is_qrcode and trade.reserveo:
                    #    zone = get_zone_by_code(trade.reserveo,session=session)
                    
                    if not zone:    
                        zone = get_classify_zone(trade.receiver_state,trade.receiver_city,trade.receiver_district
                                                 ,address=trade.receiver_address,session=session)
                    
                    trade_data['zone'] = zone and zone.COMBO_CODE or trade.reservet
                
                express_data_list.append(trade_data)
                               
        return express_data_list    
    

