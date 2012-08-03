#-*- coding:utf8 -*-
'''
Created on 2012-7-11

@author: user1
'''
import wx
import wx.grid
import wx.html
import wx.aui
import cStringIO
from taobao.dao.dbsession import get_session
from taobao.frames.panels.tradepanel import TradePanel
from taobao.frames.panels.deliverypanel import DeliveryPanel


ID_ConnectDb       = wx.NewId()
ID_CreatePicking   = wx.NewId()
ID_CreateLogistics = wx.NewId()
ID_ScanWeight      = wx.NewId()
ID_Delivery        = wx.NewId()
ID_Help            = wx.NewId() 

overview = """\
<html><body>
<h3>wx.aui, the Advanced User Interface module</h3>

<br/><b>Overview</b><br/>

<p>wx.aui is an Advanced User Interface library for the wxWidgets toolkit 
that allows developers to create high-quality, cross-platform user 
interfaces quickly and easily.</p>

<p><b>Features</b></p>

<p>With wx.aui developers can create application frameworks with:</p>

<ul>
<li>Native, dockable floating frames</li>
<li>Perspective saving and loading</li>
<li>Native toolbars incorporating real-time, &quot;spring-loaded&quot; dragging</li>
<li>Customizable floating/docking behavior</li>
<li>Completely customizable look-and-feel</li>
<li>Optional transparent window effects (while dragging or docking)</li>
</ul>

</body></html>
"""

class MainFrame(wx.Frame):
    def __init__(self, parent, id=-1, title="ERP客户端", pos=wx.DefaultPosition,
                 size=(1300,700), style=wx.DEFAULT_FRAME_STYLE |wx.SUNKEN_BORDER |wx.CLIP_CHILDREN):

        wx.Frame.__init__(self, parent, id, title, pos, size, style)
        
        self.session = get_session()
        # tell FrameManager to manage this frame        
        self._mgr = wx.aui.AuiManager()
        self._mgr.SetManagedWindow(self)
        
        self.n = 0
        self.x = 0
        
        # create menu
        mb = wx.MenuBar()

        file_menu = wx.Menu()
        file_menu.Append(ID_ConnectDb, "设置连接数据库")
        file_menu.Append(wx.ID_EXIT, "退出")

        view_menu = wx.Menu()
        view_menu.Append(ID_CreatePicking, "订单列表","订单主界面")
        view_menu.Append(ID_CreateLogistics, "发货准备","打印发货单，打印物流单")
        view_menu.Append(ID_ScanWeight, "扫描称重","扫描物流单编号，包裹称重")
        view_menu.Append(ID_Delivery, "发货确认","确认发货，同步到淘宝后台")
        view_menu.AppendSeparator()
        
        help_menu = wx.Menu()
        help_menu.Append(ID_Help, "帮助文档")
        
        mb.Append(file_menu, "数据库")
        mb.Append(view_menu, "订单操作")
        mb.Append(help_menu, "帮助")
        
        self.SetMenuBar(mb)
        
        self.statusbar = self.CreateStatusBar(2, wx.ST_SIZEGRIP)
        self.statusbar.SetStatusWidths([-2, -3])
        self.statusbar.SetStatusText("Ready", 0)
        #self.statusbar.SetStatusText("Welcome To wxPython!", 1)
        
        self.SetMinSize(wx.Size(400, 300))
        
        self._mgr.AddPane(self.CreateOrderGrid(), wx.aui.AuiPaneInfo().Name("order_grid_content").
                          CenterPane().Hide())

        self._mgr.AddPane(self.CreateDeliveryView(), wx.aui.AuiPaneInfo().Name("delivery_view_content").
                          CenterPane().Hide())
    
        all_panes = self._mgr.GetAllPanes()
        for ii in xrange(len(all_panes)):
            all_panes[ii].Hide()
           
        self._mgr.GetPane("order_grid_content").Show()
        self._mgr.Update()
        
        self.Bind(wx.EVT_MENU, self.OnChangeContentPane, id=ID_CreatePicking)
        self.Bind(wx.EVT_MENU, self.OnChangeContentPane, id=ID_CreateLogistics)
        
    
    def OnChangeContentPane(self, event):

        self._mgr.GetPane("order_grid_content").Show(event.GetId() == ID_CreatePicking)
        self._mgr.GetPane("delivery_view_content").Show(event.GetId() == ID_CreateLogistics)
        self._mgr.Update()    
    
                      
    def CreateOrderGrid(self):
        trade_operation_panel = TradePanel(self,-1) 
        return trade_operation_panel
    
    def CreateDeliveryView(self):    
        delivery_panel = TradePanel(self,-1)        
        return delivery_panel
    
    def GetIntroText(self):
        return overview
    
       
app = wx.PySimpleApp()
frm = MainFrame(None)
frm.Show()
app.MainLoop()    
