#coding=utf-8
'''
Created on 2012-6-15

@author: user1
'''
import wx
import os
from wx.html import HtmlEasyPrinting 
from taobao.common.environment import get_template
from taobao.dao.models import Trade
from taobao.tasks.tasks import getTradePickingData



FONTSIZE = 10

class HtmlPrinter(HtmlEasyPrinting):
    def __init__(self,*args,**kwargs):
        HtmlEasyPrinting.__init__(self,*args,**kwargs)
        

    def GetHtmlText(self,text):
        "Simple conversion of text.  Use a more powerful version"
        html_text = text
        #html_text = text.replace('', '<BR>')
        return html_text

    def PrintText(self, text, doc_name):
        self.SetHeader(doc_name)
        #self.SetFooter('@PAGENUM@/@PAGESCNT@')
        return HtmlEasyPrinting.PrintText(self,self.GetHtmlText(text),doc_name)

    def PreviewText(self, text, doc_name):
        self.SetHeader(doc_name)
        HtmlEasyPrinting.SetStandardFonts(self,FONTSIZE)
        #self.SetFooter('@PAGENUM@/@PAGESCNT@')
        return HtmlEasyPrinting.PreviewText(self, self.GetHtmlText(text))
    
    
        
    
    
class PrintTradePickingHtml(wx.Frame):
    def __init__(self,parent=None):
        wx.Frame.__init__(self, parent=parent, size=(640, 480),
                          title="Print Framework Sample")
        self.CreateStatusBar()

        # A text widget to display the doc and let it be edited
        self.tc = wx.TextCtrl(self, -1, "",
                              style=wx.TE_MULTILINE|wx.TE_DONTWRAP)
        self.tc.SetFont(wx.Font(FONTSIZE, wx.TELETYPE, wx.NORMAL, wx.NORMAL))
        
        trades = getTradePickingData()
        template = get_template('trade_picking_template.html') 
        self.tc.SetValue(template.render(trades=trades))
        
        self.htmlprinter = HtmlPrinter('打印',self)
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
        self.margins = (wx.Point(3,3), wx.Point(3,3))


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
        #page setup data
        page_setup = self.htmlprinter.PageSetupData      
        page_setup.SetMarginTopLeft(self.margins[0])
        page_setup.SetMarginBottomRight(self.margins[1])
        #print setup data        
        print_data = self.htmlprinter.PrintData
        print_data.Bin = self.pdata.Bin
        print_data.Orientation = self.pdata.Orientation
        print_data.PaperId     = self.pdata.PaperId
        print_data.PaperSize   = self.pdata.PaperSize
        print_data.PrinterName = self.pdata.PrinterName
        print_data.PrivData    = self.pdata.PrivData        
        
        text = self.tc.GetValue()
        self.htmlprinter.PreviewText(text,'')
        
        
    def OnPrint(self, evt):
        #page setup data
        page_setup = self.htmlprinter.PageSetupData      
        page_setup.SetMarginTopLeft(self.margins[0])
        page_setup.SetMarginBottomRight(self.margins[1])
        #print setup data       
        print_data = self.htmlprinter.PrintData
        print_data.Bin = self.pdata.Bin
        print_data.Orientation = self.pdata.Orientation
        print_data.PaperId     = self.pdata.PaperId
        print_data.PaperSize   = self.pdata.PaperSize
        print_data.PrinterName = self.pdata.PrinterName
        print_data.PrivData    = self.pdata.PrivData        

        text = self.tc.GetValue() 
        self.htmlprinter.PrintText(text,'')
        
        
        
#app = wx.PySimpleApp()
#frm = PrintTradePickingHtml()
#frm.Show()
#app.MainLoop()
