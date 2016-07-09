#-*- coding:utf8 -*-
'''
Created on 2012-7-11

@author: user1
'''
import wx.aui
from taobao.dao.dbsession import get_session
from taobao.common.utils import pinghost,getconfig
from taobao.frames.panels.tradepanel import TradePanel
from taobao.frames.panels.weightpanel import ScanWeightPanel
from taobao.frames.panels.checkpanel import ScanCheckPanel
from taobao.frames.panels.chargepanel import ScanChargePanel
import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )

ID_TradeMainPage   = wx.NewId()
ID_ScanCheck       = wx.NewId()
ID_ScanWeight      = wx.NewId()
ID_ScanCharge      = wx.NewId()
ID_Help            = wx.NewId()
TITLE = u"小鹿特卖仓库客户端V2.3"
class MainFrame(wx.Frame):
    def __init__(self, parent, id=-1, title=TITLE, pos=wx.DefaultPosition,
                 size=(1300,700), style=wx.DEFAULT_FRAME_STYLE |wx.SUNKEN_BORDER |wx.CLIP_CHILDREN):

        wx.Frame.__init__(self, parent, id, title, pos, size, style)
        
        self.Session = get_session()
        # tell FrameManager to manage this frame        
        self._mgr = wx.aui.AuiManager()
        self._mgr.SetManagedWindow(self)
     
        # create menu
        mb = wx.MenuBar()
        view_menu = wx.Menu()
        view_menu.Append(ID_TradeMainPage, u"订单列表",u"订单操作主界面")
        view_menu.Append(ID_ScanCheck, u"扫描验货",u"扫描物流单编号，扫描商品条码")
        view_menu.Append(ID_ScanWeight, u"扫描称重",u"扫描物流单编号，包裹称重")
        #view_menu.Append(ID_ScanCharge, u"揽件确认",u"扫描物流单编号，确认揽件")
        view_menu.Append(wx.ID_EXIT, u"退出")
        view_menu.AppendSeparator()
        
        help_menu = wx.Menu()
        help_menu.Append(ID_Help, u"帮助文档")
        
        mb.Append(view_menu, u"订单操作")
        mb.Append(help_menu, u"帮助")
        
        self.SetMenuBar(mb)
        
        self.statusbar = self.CreateStatusBar(2, wx.ST_SIZEGRIP)
        self.statusbar.SetStatusWidths([-2, -3])
        self.statusbar.SetStatusText("Ready", 0)
        #self.statusbar.SetStatusText("Welcome To wxPython!", 1)
        
        self.SetMinSize(wx.Size(400, 300))
        
        self._mgr.AddPane(self.CreateOrderGrid(), wx.aui.AuiPaneInfo().Name("order_grid_content").
                          CenterPane().Hide())
        
        self._mgr.AddPane(self.CreateCheckView(), wx.aui.AuiPaneInfo().Name("scan_check_content").
                          CenterPane().Hide())

        self._mgr.AddPane(self.CreateDeliveryView(), wx.aui.AuiPaneInfo().Name("scan_weight_content").
                          CenterPane().Hide())
        
#        self._mgr.AddPane(self.CreateChargeView(), wx.aui.AuiPaneInfo().Name("scan_charge_content").
#                          CenterPane().Hide())
        
        all_panes = self._mgr.GetAllPanes()
        for ii in xrange(len(all_panes)):
            all_panes[ii].Hide()
           
        self._mgr.GetPane("order_grid_content").Show()
        self._mgr.Update()
        
        self.Bind(wx.EVT_MENU, self.OnChangeContentPane, id=ID_TradeMainPage)
        self.Bind(wx.EVT_MENU, self.OnChangeContentPane, id=ID_ScanCheck)
        self.Bind(wx.EVT_MENU, self.OnChangeContentPane, id=ID_ScanWeight)
#        self.Bind(wx.EVT_MENU, self.OnChangeContentPane, id=ID_ScanCharge)
        self.Bind(wx.EVT_MENU, self.OnExit, id=wx.ID_EXIT)
        
    
    def OnChangeContentPane(self, event):
        
        self._mgr.GetPane("order_grid_content").Show(event.GetId() == ID_TradeMainPage)
        self._mgr.GetPane("scan_check_content").Show(event.GetId() == ID_ScanCheck)
        self._mgr.GetPane("scan_weight_content").Show(event.GetId() == ID_ScanWeight)
#        self._mgr.GetPane("scan_charge_content").Show(event.GetId() == ID_ScanCharge)
        self._mgr.Update()    
                
    def CreateOrderGrid(self):
        trade_operation_panel = TradePanel(self,-1) 
        return trade_operation_panel
    
    def CreateCheckView(self):    
        check_panel = ScanCheckPanel(self,-1)        
        return check_panel
    
    def CreateDeliveryView(self):    
        delivery_panel = ScanWeightPanel(self,-1)        
        return delivery_panel
    
    def CreateChargeView(self):
        charge_panel = ScanChargePanel(self,-1)        
        return charge_panel
    
    def OnExit(self,event):
        self.Close()
    
    
#sys.setdefaultencoding('utf8') 
app = wx.PySimpleApp()
# try:
config = getconfig()
db_host = config.get('db','db_host')
print db_host
if False and pinghost(db_host):
    dial = wx.MessageDialog(None, u'数据库连接失败(host:%s)'%db_host,
                            u'数据库连接失败提示', wx.OK | wx.ICON_EXCLAMATION)
    dial.ShowModal()
else:
    wx.InitAllImageHandlers()
    frm = MainFrame(None)
    frm.Show()
# except Exception,exc:
#     dial = wx.MessageDialog(None, u'程序错误：%s'%exc.message,
#                              u'错误提示', wx.OK | wx.ICON_EXCLAMATION)
#     dial.ShowModal()
#     raise exc
    
app.MainLoop()    
