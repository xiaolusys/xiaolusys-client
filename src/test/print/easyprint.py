'''
Created on 2012-6-4

@author: user1
'''
import wx
import os
from wx.html import HtmlEasyPrinting

FONTSIZE = 10

class HtmlPrinter(HtmlEasyPrinting):
    def __init__(self):
        HtmlEasyPrinting.__init__(self)

    def GetHtmlText(self,text):
        "Simple conversion of text.  Use a more powerful version"
        html_text = text.replace('\n\n','<P>')
        html_text = text.replace('\n', '<BR>')
        return html_text

    def Print(self, text, doc_name):
        self.SetHeader(doc_name)
        self.PrintText(self.GetHtmlText(text),doc_name)

    def PreviewText(self, text, doc_name):
        self.SetHeader(doc_name)
        return HtmlEasyPrinting.PreviewText(self, self.GetHtmlText(text))
        


content = open('../sample-text.txt','r')
printer = HtmlPrinter()
printer.Print(content.decode('gbk'),'my first page')


