#coding=utf-8
'''
Created on 2012-6-5

@author: user1
'''
import wx
import os
from wx.html import HtmlEasyPrinting 
from taobao.common.environment import get_template
from taobao.dao.models import Trade
from taobao.dao.dbsession import get_session



FONTSIZE = 8

class HtmlPrinter(HtmlEasyPrinting):
    def __init__(self,*args,**kwargs):
        HtmlEasyPrinting.__init__(self,*args,**kwargs)
        

    def GetHtmlText(self,text):
        "Simple conversion of text.  Use a more powerful version"
        html_text = text.replace('\n\n','<P>')
        html_text = text.replace('\n', '<BR>')
        return html_text

    def PrintText(self, text, doc_name,prompt=True):
        self.SetHeader(doc_name)
        self.SetFooter('@PAGENUM@/@PAGESCNT@')
        return HtmlEasyPrinting.PrintText(self,self.GetHtmlText(text),doc_name)

    def PreviewText(self, text, doc_name):
        self.SetHeader(doc_name)
        HtmlEasyPrinting.SetStandardFonts(self,FONTSIZE)
        self.SetFooter('@PAGENUM@/@PAGESCNT@')
        return HtmlEasyPrinting.PreviewText(self, self.GetHtmlText(text))
    
    
        
    
    
class PrintTradePickingHtml(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, size=(640, 480),
                          title="Print Framework Sample")
        self.CreateStatusBar()

        # A text widget to display the doc and let it be edited
        self.tc = wx.TextCtrl(self, -1, "",
                              style=wx.TE_MULTILINE|wx.TE_DONTWRAP)
        self.tc.SetFont(wx.Font(FONTSIZE, wx.TELETYPE, wx.NORMAL, wx.NORMAL))
        session = get_session()
        trades = session.query(Trade).filter_by(status='WAIT_SELLER_SEND_GOODS')
        template = get_template('trade_picking_template.html')
        self.tc.SetValue(template.render(trades=trades))
        
        self.htmlprinter = HtmlPrinter('Printing',self)
        self.tc.Bind(wx.EVT_SET_FOCUS, self.OnClearSelection)
        wx.CallAfter(self.tc.SetInsertionPoint, 0)

        # Create the menu and menubar
        menu = wx.Menu('config')
        item = menu.Append(-1, "Page Setup...\tF5",
                           "Set up page margins and etc.")
        self.Bind(wx.EVT_MENU, self.OnPageSetup, item)
        item = menu.Append(-1, "Print Setup...\tF6",
                           "Set up the printer options, etc.")
        self.Bind(wx.EVT_MENU, self.OnPrintSetup, item)
        item = menu.Append(-1, "Print Preview...\tF7",
                           "View the printout on-screen")
        self.Bind(wx.EVT_MENU, self.OnPrintPreview, item)
        item = menu.Append(-1, "Print...\tF8", "Print the document")
        self.Bind(wx.EVT_MENU, self.OnPrint, item)
        menu.AppendSeparator()
        item = menu.Append(-1, "E ", "Close this application")
        self.Bind(wx.EVT_MENU, self.OnExit, item)

        menubar = wx.MenuBar()
        menubar.Append(menu, "setup")
        self.SetMenuBar(menubar)

        # initialize the print data and set some default values
        self.pdata = wx.PrintData()
        self.pdata.SetPaperId(wx.PAPER_LETTER)
        self.pdata.SetOrientation(wx.PORTRAIT)
        self.margins = (wx.Point(1,1), wx.Point(1,1))


    def OnExit(self, evt):
        self.Close()


    def OnClearSelection(self, evt):
        evt.Skip()
        wx.CallAfter(self.tc.SetInsertionPoint,
                     self.tc.GetInsertionPoint())


    def OnPageSetup(self, evt):
        data = wx.PageSetupDialogData()
        data.SetPrintData(self.pdata)

        data.SetDefaultMinMargins(True)
        data.SetMarginTopLeft(self.margins[0])
        data.SetMarginBottomRight(self.margins[1])
        dlg = wx.PageSetupDialog(self, data)
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetPageSetupData()
            self.pdata = wx.PrintData(data.GetPrintData()) # force a copy
            self.pdata.SetPaperId(data.GetPaperId())
            self.margins = (data.GetMarginTopLeft(),
                            data.GetMarginBottomRight())
        dlg.Destroy()


    def OnPrintSetup(self, evt):
        data = wx.PrintDialogData(self.pdata)
        dlg = wx.PrintDialog(self, data)
        #dlg.GetPrintDialogData().SetSetupDialog(True)
        dlg.ShowModal();
        data = dlg.GetPrintDialogData()
        self.pdata = wx.PrintData(data.GetPrintData()) # force a copy
        dlg.Destroy()


    def OnPrintPreview(self, evt):
        page_setup = self.htmlprinter.PageSetupData
        #print_data = self.htmlprinter.PrintData
        
        page_setup.SetMarginTopLeft(self.margins[0])
        page_setup.SetMarginBottomRight(self.margins[1])
        
        text = self.tc.GetValue()
        self.htmlprinter.PreviewText(text,u'\u53d1\u8d27\u5355')
        
    def OnPrint(self, evt):
        #printer = wx.Printer(data)
        text = self.tc.GetValue()
        self.htmlprinter.PrintText(text,u'\u53d1\u8d27\u5355')
        
app = wx.PySimpleApp()
frm = PrintTradePickingHtml()
frm.Show()
app.MainLoop()
