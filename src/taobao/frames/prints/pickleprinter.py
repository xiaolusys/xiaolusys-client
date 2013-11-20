#-*- coding:utf8 -*-
#######################################################################
# logisticsprinter.py
#
# Created: 8/5/2012 by mld
#
# Description: 打印物流单操作窗口
#######################################################################
#-*- coding:utf8 -*- 
import wx
import wx.lib.iewin as iewin
from taobao.common.utils import getconfig

FONTSIZE = 10
  
 
class PicklePrinter(wx.Frame):
 
    #----------------------------------------------------------------------
    def __init__(self,parent=None, title=u'打印配货单'):
        wx.Frame.__init__(self, parent, wx.ID_ANY, title, size=(850,500))
 
        self.panel = wx.Panel(self, wx.ID_ANY)
        #self.printer = HtmlPrinter(name=u'打印', parentWindow=self)
 
        self.html = iewin.IEHtmlWindow(self.panel,-1)
        #trade_ids = [200165044022938,165155430754126]
         
        cfg  = getconfig()
        host_name   = cfg.get('url','web_host')
        client_name = cfg.get('user','username')
        self.html.LoadUrl(cfg.get('url','post_url')%(host_name,client_name))
        
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
    def onPreview(self,event):
        """"""
        self.html.PrintPreview()
         
        event.Skip()
 
    #----------------------------------------------------------------------
    def onCancel(self, event):
        """"""
        self.Parent.refreshTable()
        
        self.Close()
        
    
    

