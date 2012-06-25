#coding=utf-8
'''
Created on 2012-6-15

@author: user1
'''
import wx
import os
from wx.html import HtmlEasyPrinting 
from taobao.dao.models import Trade
from taobao.dao.dbsession import get_session
from taobao.tasks import tasks,timer
from taobao.picking.pickingframe import PrintTradePickingHtml


class MainFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, size=(800, 600),style =wx.DEFAULT_FRAME_STYLE&~(wx.RESIZE_BORDER|wx.RESIZE_BOX|wx.MAXIMIZE_BOX),
                          title="用户操作客户端")
   
        self.CreateStatusBar()
        panel = wx.Panel(self)
        
        menu = wx.Menu('选择操作')
        item = menu.Append(-1, "手动打印发货单\tF5",
                           "可以设置打印属性，并选择打印发货单。")
        self.Bind(wx.EVT_MENU, self.OpenPrintPickingFrame, item)
        
        menubar = wx.MenuBar()
        menubar.Append(menu, "操作菜单")
        self.SetMenuBar(menubar)
       
        pick_button = wx.Button(panel,label='手动打印发货单',pos=(530, 10),size=(100,40))
        self.Bind(wx.EVT_BUTTON,self.OpenPrintPickingFrame,pick_button)
        
        sms_button = wx.Button(panel,label='启动短信备注提示\n（每半小时）',pos=(650, 10),size=(120,40))
        self.Bind(wx.EVT_BUTTON,self.OnSmsButtonClick,sms_button)
        
        self.sms_button_flag = 1
        self.sms_schedule_thread = None
        
        self.auto_picking_flag = 1
        self.auto_picking_thread = None
        
    def OnSmsButtonClick(self,evt):
        button = evt.EventObject
        if self.sms_button_flag == 1:
            if not self.sms_schedule_thread:
                self.sms_schedule_thread = \
                    timer.Timer(tasks.sendSmsToUnmemoBuyerTask,args=(1,),sleep=30*60)
            self.sms_schedule_thread.start()
            button.SetLabel('关闭短信备注提示\n（每半小时）')
            
            self.sms_button_flag = 0
        else :
            if self.sms_schedule_thread:
                self.sms_schedule_thread.stop()
            button.SetLabel('启动短信备注提示\n（每半小时）')
            self.sms_button_flag = 1
            self.sms_schedule_thread = None
    
    
#    def OnAutoPickButtonClick(self,evt):
#        button = evt.EventObject
#        if self.auto_picking_flag == 1:
#            if not self.auto_picking_thread:
#                self.auto_picking_thread = \
#                    timer.Timer(tasks.printTradePickingTask,args=(),sleep=30*60)
#            self.auto_picking_thread.start()
#            button.SetLabel('启动自动打印发货单\n（每半小时）') 
#            self.auto_picking_flag = 0
#        else :
#            if self.auto_picking_thread:
#                self.auto_picking_thread.stop()
#            button.SetLabel('停止自动打印发货单\n（每半小时）')
#            self.auto_picking_flag = 1
#            self.auto_picking_thread = None        
      
    def OpenPrintPickingFrame(self,evt):
        ptph = PrintTradePickingHtml(parent=self)
        ptph.Show() 
    
      
    def OnResult(self, event):
        """Show Result status."""
        if event.data is None:
            # Thread aborted (using our convention of None return)
            print event
        else:
            # Process results here
            print event.data
        # In either event, the worker is done
        self.sms_schedule_thread = None
      
            
        
app = wx.PySimpleApp()
frm = MainFrame()
frm.Show()
app.MainLoop()
