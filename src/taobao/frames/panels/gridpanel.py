#-*- coding:utf8 -*-
'''
Created on 2012-7-13

@author: user1
'''
import re
import weakref
import wx, wx.grid as grd
from taobao.dao import configparams as cfg 
from taobao.frames.tables.gridtable import GridTable,SimpleGridTable,WeightGridTable
from taobao.frames.panels.itempanel import ItemPanel
from taobao.frames.tables.gridtable import CheckGridTable
from taobao.common.paginator import Paginator
from taobao.exception.exception import NotImplement
from taobao.common.utils import create_session,getconfig
from taobao.dao.models import MergeOrder,MergeTrade
from taobao.dao.tradedao import get_used_orders
from taobao.frames.prints.deliveryprinter import DeliveryPrinter 
from taobao.frames.prints.expressprinter import ExpressPrinter
from taobao.frames.prints.pickleprinter import PicklePrinter
from taobao.frames.prints.revieworder import OrderReview

TRADE_ID_CELL_COL = 1
LOG_COMPANY_CELL_COL = 11
OUT_SID_CELL_COL = 12
OPERATOR_CELL_COL = 13
OUTER_ID_COL = 5
OUTER_SKU_ID_COL = 6
ORIGIN_NUL_COL = 4
NUM_STATUS_COL = 10

fill_sid_btn_id = wx.NewId()
picking_print_btn_id = wx.NewId()
express_print_btn_id = wx.NewId()
scan_check_btn_id = wx.NewId()
scan_weight_btn_id = wx.NewId()
review_orders_btn_id = wx.NewId()
pickle_print_btn_id  = wx.NewId()
fill_sid_btn2_id = wx.NewId()
fill_sid_btn4_id = wx.NewId()  #核对单号按钮

class GridPanel(wx.Panel):
    def __init__(self, parent, id= -1, colLabels=None, rowLabels=None): 
        wx.Panel.__init__(self, parent, id) 
        
        self.Session = parent.Session
        self.datasource = None
        self.paginator = self.page = None
        self.page_size = 100
        self.rowLabels = rowLabels
        self.colLabels = colLabels
        self.status_type = ''
        self.start_sid   = ''
        self.end_sid     = ''
        self.grid = grd.Grid(self, -1)
        
        self._selectedRows = set()
        self.pag_panel =pag_panel = wx.Panel(self,-1)
        self.select_all_label = wx.StaticText(pag_panel,-1,u'  全  选')
        self.select_all_check = wx.CheckBox(pag_panel,-1)
        self.pt1 = wx.StaticText(pag_panel, -1, u",第")
        self.pt2 = wx.StaticText(pag_panel, -1, u"/")
        self.pt3 = wx.StaticText(pag_panel, -1, u"页(共")
        self.pt5 = wx.StaticText(pag_panel, -1, u"条,已选") 
        self.pt6 = wx.StaticText(pag_panel,-1,u" 条),每页")
        self.lblPageIndex = wx.StaticText(pag_panel, -1, "0")
        self.lblPageCount = wx.StaticText(pag_panel, -1, "0")
        self.lblTotalCount = wx.StaticText(pag_panel, -1, "0")
        self.selected_counts = wx.StaticText(pag_panel,-1,"0")
        self.page_size_select = wx.ComboBox(pag_panel,-1,choices=('50','100','200','500'),value='100')
        self.btnFirst = wx.Button(pag_panel, -1, label=u'首页', style=0)
        self.btnLast = wx.Button(pag_panel, -1, label=u'尾页', style=0)
        self.btnPrev = wx.Button(pag_panel, -1, label=u'上一页', style=0)
        self.btnNext = wx.Button(pag_panel, -1, label=u'下一页', style=0)
   
        self.fill_sid_btn = wx.Button(pag_panel, fill_sid_btn_id, label=u'填物流单号',name=u'打印发货单前，需将物流单号与订单绑定')
        self.picking_print_btn = wx.Button(pag_panel, picking_print_btn_id, label=u'打印发货单',name=u'打印发货单，进行配货')
        self.express_print_btn = wx.Button(pag_panel,express_print_btn_id,label=u'打印物流单',name=u'打印物流单，为打印配货单准备')
        self.post_print_btn = wx.Button(pag_panel,pickle_print_btn_id,label=u'打印配货单',name=u'打印配货单，为扫描验货准备')
        self.review_orders_btn = wx.Button(pag_panel,review_orders_btn_id,label=u'审查订单',name=u'审查指定订单问题并处理')
        self.scan_check_btn = wx.Button(pag_panel,scan_check_btn_id,label=u'扫描验货',name=u'扫描验货,为扫描称重准备')
        self.scan_weight_btn = wx.Button(pag_panel,scan_weight_btn_id,label=u'扫描称重',name=u'扫描称重，订单发货流程结束')
        
        self.button_array = []
        
        self.inner_panel  = wx.Panel(self,-1)
        self.fill_sid_panel   = wx.Panel(self.inner_panel,-1)
        self.fill_sid_label1  = wx.StaticText(self.fill_sid_panel,-1,u'起始物流单号')
        self.fill_sid_text   = wx.TextCtrl(self.fill_sid_panel,-1,size=(200,-1))
        self.fill_sid_label2  = wx.StaticText(self.fill_sid_panel,-1,u'单号自增')
        self.fill_sid_checkbox1   = wx.CheckBox(self.fill_sid_panel,-1)
        self.preview_btn      = wx.Button(self.fill_sid_panel,-1,u'预览')
        self.fill_sid_btn2   = wx.Button(self.fill_sid_panel,fill_sid_btn2_id,u'确定')
        
        self.out_sid_start_label  = wx.StaticText(self.fill_sid_panel,-1,u'连打始单号')
        self.out_sid_start_text   = wx.TextCtrl(self.fill_sid_panel,-1,size=(120,-1))
        self.out_sid_end_label  = wx.StaticText(self.fill_sid_panel,-1,u'连打尾单号')
        self.out_sid_end_text   = wx.TextCtrl(self.fill_sid_panel,-1,size=(120,-1))
        self.fill_sid_btn4   = wx.Button(self.fill_sid_panel,fill_sid_btn4_id,u'核对')
        self.fill_sid_btn3   = wx.Button(self.fill_sid_panel,-1,u'折起')

        self.static_button_down = wx.Button(self,-1,label='^------------^',size=(-1,11))
        self.isSearchPanelShow = 1
        
        self.itempanel = ItemPanel(self, -1)
        
        self.updateTableAndPaginator()
        self.__set_properties()
        self.__do_layout()
        self.__bind_evt()
        
        
        
    def __set_properties(self):
        self.SetName('grid_panel')
        font = wx.Font(10,wx.SWISS,wx.SLANT,wx.BOLD,False)
        self.fill_sid_btn.SetFont(font)
        self.picking_print_btn.SetFont(font)
        self.express_print_btn.SetFont(font)
        self.post_print_btn.SetFont(font)
        self.review_orders_btn.SetFont(font)
        self.scan_check_btn.SetFont(font)
        self.scan_weight_btn.SetFont(font)
        
        self.fill_sid_checkbox1.SetValue(True)
        
        self.button_array.append(self.fill_sid_btn)
        self.button_array.append(self.picking_print_btn)
        self.button_array.append(self.express_print_btn)
        
        self.fill_sid_btn2.Enable(False)
        self.fill_sid_btn4.Enable(False)
        self.review_orders_btn.Enable(False)

        
        
    def __do_layout(self):
        self.main_sizer = main_sizer = wx.BoxSizer(wx.VERTICAL) 
        
        fg = wx.FlexGridSizer(hgap=2, vgap=2)
        fg.Add(self.select_all_label,0,0)
        fg.Add(self.select_all_check,0,0)
        fg.Add(self.pt1, 0, 0)
        fg.Add(self.lblPageIndex, 0, 1)
        fg.Add(self.pt2, 0, 2)
        fg.Add(self.lblPageCount, 0, 3)
        fg.Add(self.pt3, 0, 4)
        fg.Add(self.lblTotalCount, 0, 5)
        fg.Add(self.pt5, 0, 6)
        fg.Add(self.selected_counts,0,7)
        fg.Add(self.pt6,0,8)
        fg.Add(self.page_size_select,0,9)
        fg.Add(self.btnFirst, 0, 10)
        fg.Add(self.btnPrev, 0, 11)
        fg.Add(self.btnNext, 0, 12)
        fg.Add(self.btnLast, 0, 13) 
        fg.Add((10,10),0,14)
  
        
        fg.Add(self.fill_sid_btn, 0, 15)
        fg.Add(self.express_print_btn, 0, 16) 
        fg.Add(self.picking_print_btn, 0, 17)
        fg.Add(self.post_print_btn,0,18)
        fg.Add(self.review_orders_btn,0,19)
        fg.Add(self.scan_check_btn,0,20)
        fg.Add(self.scan_weight_btn, 0,21)
        self.pag_panel.SetSizer(fg)
        
        self.fill_sid_sizer = wx.FlexGridSizer(hgap=15, vgap=15)
        self.fill_sid_sizer.Add(self.fill_sid_label1,0,0)
        self.fill_sid_sizer.Add(self.fill_sid_text,0,1)
        self.fill_sid_sizer.Add(self.fill_sid_label2,0,2)
        self.fill_sid_sizer.Add(self.fill_sid_checkbox1,0,3)
        self.fill_sid_sizer.Add(self.preview_btn,0,4)
        self.fill_sid_sizer.Add(self.fill_sid_btn2,0,5)
        self.fill_sid_sizer.Add(self.out_sid_start_label,0,7)
        self.fill_sid_sizer.Add(self.out_sid_start_text,0,8)
        self.fill_sid_sizer.Add(self.out_sid_end_label,0,9)
        self.fill_sid_sizer.Add(self.out_sid_end_text,0,10)
        self.fill_sid_sizer.Add(self.fill_sid_btn4,0,11)
        self.fill_sid_sizer.Add(self.fill_sid_btn3,0,12)
        self.fill_sid_panel.SetSizer(self.fill_sid_sizer)

        self.inner_box_sizer = wx.BoxSizer(wx.VERTICAL) 
        self.inner_box_sizer.Add(self.fill_sid_panel,proportion=0,flag=wx.EXPAND)
        self.inner_panel.SetSizer(self.inner_box_sizer)
        
        self.__set_sizer(6,4)
        
    def __set_sizer(self,grid_propt=6,item_propt=4):
        self.main_sizer.Clear()
        self.main_sizer.Add(self.grid,grid_propt, wx.EXPAND)
        self.main_sizer.Add(self.pag_panel,flag=wx.RIGHT|wx.EXPAND) 
        self.main_sizer.Add(wx.StaticLine(self,-1),flag=wx.EXPAND)
        self.main_sizer.Add(self.inner_panel,flag=wx.EXPAND)
        self.main_sizer.Add(self.static_button_down,flag=wx.RIGHT|wx.EXPAND)
        self.main_sizer.Add(self.itempanel,item_propt,flag=wx.RIGHT|wx.EXPAND)
        self.SetSizer(self.main_sizer)  
    
    def __bind_evt(self):
        self.Bind(grd.EVT_GRID_CELL_LEFT_CLICK, self.onMouse, self.grid)
        self.Bind(grd.EVT_GRID_SELECT_CELL, self.onCellSelected, self.grid)
        self.Bind(grd.EVT_GRID_EDITOR_CREATED, self.onEditorCreated, self.grid)
        self.Bind(grd.EVT_GRID_CELL_RIGHT_CLICK,self.showPopupMenu,self.grid)
        
        self.Bind(wx.EVT_CHECKBOX,self.onSelectAllCheckbox,self.select_all_check)
        self.Bind(wx.EVT_COMBOBOX,self.onComboBox,self.page_size_select)
        self.Bind(wx.EVT_BUTTON, self.onBtnFirstClick, self.btnFirst)
        self.Bind(wx.EVT_BUTTON, self.onBtnLastClick, self.btnLast)
        self.Bind(wx.EVT_BUTTON, self.onBtnPrevClick, self.btnPrev)
        self.Bind(wx.EVT_BUTTON, self.onBtnNextClick, self.btnNext)
        
        self.Bind(wx.EVT_BUTTON, self.onChangeFlexSizer,self.fill_sid_btn)
        
        self.Bind(wx.EVT_BUTTON, self.onClickHideInnerPanel,self.fill_sid_btn3 )
        self.Bind(wx.EVT_BUTTON,self.onClickStaticButton,self.static_button_down)
        self.Bind(wx.EVT_BUTTON, self.fillOutSidToCell,self.preview_btn)
        
        #分页栏，订单操作事件
        self.Bind(wx.EVT_BUTTON, self.onClickActiveButton,self.fill_sid_btn2)
        self.Bind(wx.EVT_BUTTON, self.onClickActiveButton,self.fill_sid_btn4)
        self.Bind(wx.EVT_BUTTON, self.onClickActiveButton,self.scan_weight_btn)
        self.Bind(wx.EVT_BUTTON, self.onClickActiveButton,self.picking_print_btn)
        self.Bind(wx.EVT_BUTTON, self.onClickActiveButton,self.express_print_btn)
        self.Bind(wx.EVT_BUTTON, self.onClickActiveButton,self.post_print_btn)
        self.Bind(wx.EVT_BUTTON, self.onClickActiveButton,self.review_orders_btn)
        self.Bind(wx.EVT_BUTTON, self.onClickActiveButton,self.scan_check_btn)
        self.Bind(wx.EVT_BUTTON, self.onClickActiveButton,self.scan_weight_btn)

        
    def setDataSource(self, status_type): 
        self.status_type = status_type
        with create_session(self.Parent) as session: 
            datasource     = session.query(MergeTrade).order_by('priority desc','shop_trades_mergetrade.pay_time asc')
            if status_type and status_type != cfg.SYS_STATUS_ALL:
                datasource = datasource.filter_by(sys_status=status_type)
        self.datasource = datasource
        self.paginator = paginator = Paginator(datasource, self.page_size)
        self.page = paginator.page(1)
        
        self.fill_sid_btn.Show(status_type in (cfg.SYS_STATUS_PREPARESEND))
        self.picking_print_btn.Show(status_type in (cfg.SYS_STATUS_PREPARESEND))
        self.express_print_btn.Show(status_type in (cfg.SYS_STATUS_PREPARESEND))
        self.post_print_btn.Show(status_type in (cfg.SYS_STATUS_PREPARESEND))
        self.review_orders_btn.Show(status_type in (cfg.SYS_STATUS_WAITSCANCHECK,cfg.SYS_STATUS_WAITSCANWEIGHT,cfg.SYS_STATUS_FINISHED))
        self.scan_check_btn.Show(status_type in (cfg.SYS_STATUS_WAITSCANCHECK))
        self.scan_weight_btn.Show(status_type in (cfg.SYS_STATUS_WAITSCANWEIGHT))

        self.updateTableAndPaginator()
        self.Layout()
        
    def setSearchData(self, datasource):
        self.paginator = paginator = Paginator(datasource, self.page_size)
        self.page = paginator.page(1)
        self.updateTableAndPaginator()
   

##################checkbox 在grid中的事件绑定 ###################
    def onMouse(self,evt):
        if evt.Col == 0:
            wx.CallLater(100,self.toggleCheckBox)
        evt.Skip()

    def toggleCheckBox(self):
        self.grid.cb.Value = not self.grid.cb.Value
        self.afterCheckBox(self.grid.cb.Value)

    def onCellSelected(self,evt):
        if evt.Col == 0:
            wx.CallAfter(self.grid.EnableCellEditControl)
        evt.Skip()

    def onEditorCreated(self,evt):
        if evt.Col == 0:
            self.grid.cb = evt.Control
            self.grid.cb.WindowStyle |= wx.WANTS_CHARS
            self.grid.cb.Bind(wx.EVT_KEY_DOWN,self.onKeyDown)
            self.grid.cb.Bind(wx.EVT_CHECKBOX,self.onCheckBox)
        evt.Skip()

    def onKeyDown(self,evt):
        if evt.KeyCode == wx.WXK_UP:
            if self.GridCursorRow > 0:
                self.grid.DisableCellEditControl()
                self.grid.MoveCursorUp(False)
        elif evt.KeyCode == wx.WXK_DOWN:
            if self.grid.GridCursorRow < (self.grid.NumberRows-1):
                self.grid.DisableCellEditControl()
                self.grid.MoveCursorDown(False)
        elif evt.KeyCode == wx.WXK_LEFT:
            if self.grid.GridCursorCol > 0:
                self.grid.DisableCellEditControl()
                self.grid.MoveCursorLeft(False)
        elif evt.KeyCode == wx.WXK_RIGHT:
            if self.grid.GridCursorCol < (self.grid.NumberCols-1):
                self.grid.DisableCellEditControl()
                self.grid.MoveCursorRight(False)
        else:
            evt.Skip()

    def onCheckBox(self,evt):
        self.afterCheckBox(evt.IsChecked())

    def afterCheckBox(self,isChecked,singleRecord=False):
        row = 0 if singleRecord else self.grid.GridCursorRow
        if isChecked:
            self._selectedRows.add(row)
            value = self.grid.GetCellValue(row,1)
            self.itempanel.setData(value)
            for btn in self.button_array:
                btn.Enable(True)
        else:
            try:
                self._selectedRows.remove(row)
            except:
                pass
            if len(self._selectedRows) <1:
                for btn in self.button_array:
                    btn.Enable(False)
        self.review_orders_btn.Enable(len(self._selectedRows) == 1)
        self.selected_counts.SetLabel(str(len(self._selectedRows)))
        self.updateSelectAllCheck()
        self.Layout()
        
    #####################check 在grid中事件绑定结束#########################   
    
    
    def showPopupMenu(self,evt):
        if not hasattr(self,"popupID1"):
            self.popupID1 = wx.NewId()
        menu = wx.Menu()
        item = wx.MenuItem(menu,self.popupID1,u'刷新')
        menu.AppendItem(item)
        self.grid.PopupMenu(menu)
        menu.Destroy()
        self.Bind(wx.EVT_MENU,self.onMenuRefreshTable)
        
    
    def onMenuRefreshTable(self,evt):
        eventid = evt.GetId()
        if eventid == self.popupID1:
            self.refreshTable()
    
    def onComboBox(self, evt):
        size = self.page_size_select.GetValue()
        if size.isdigit():
            self.page_size = int(size)
            self.paginator = paginator = Paginator(self.datasource, self.page_size)
            self.page = paginator.page(1)
            self.updateTableAndPaginator()
            
    def onChangeFlexSizer(self,evt):
        eventid= evt.GetId()
        self.inner_panel.Show()
        self.fill_sid_panel.Show(eventid == fill_sid_btn_id)
        self.inner_panel.Layout()
        self.itempanel.Layout()
        self.Layout()
    
    def onClickHideInnerPanel(self,evt):
        self.inner_panel.Hide()
        self.itempanel.Layout()
        self.Layout()
        evt.Skip()
     
    
    def onSelectAllCheckbox(self,evt):
        rows = self.grid.NumberRows
        if evt.IsChecked():
            for i in xrange(0,rows):
                self.grid.SetCellValue(i,0,'1')
                self._selectedRows.add(i)
            for btn in self.button_array:
                btn.Enable(True)
        else: 
            for i in xrange(0,rows):
                self.grid.SetCellValue(i,0,'')
            self._selectedRows.clear()
            for btn in self.button_array:
                btn.Enable(False)

        self.grid.ForceRefresh()
        self.selected_counts.SetLabel(str(len(self._selectedRows))) 

    
    def onClickStaticButton(self,evt):
        if self.isSearchPanelShow == 0:
            self.__set_sizer(6,4)
            self.itempanel.Show()
            self.isSearchPanelShow = 1
            self.static_button_down.SetLabel('^------------^')
        elif self.isSearchPanelShow == 1:
            self.__set_sizer(1,9)
            self.isSearchPanelShow = 2
            self.static_button_down.SetLabel('v------------v')
        else:
            self.__set_sizer(8,2)
            self.isSearchPanelShow = 0
            self.static_button_down.SetLabel('^------------^')
            self.itempanel.Hide()
        self.Layout()    
            
    def fillOutSidToCell(self,evt):
        self.refreshTable()
        start_out_sid = self.fill_sid_text.GetValue()
        is_auto_fill  = self.fill_sid_checkbox1.IsChecked()
        with create_session(self.Parent) as session:
            if start_out_sid.isdigit() and is_auto_fill:
                self.start_sid = start_out_sid
                start_out_sid = int(start_out_sid)
                for row in self._selectedRows:
                    trade_id = self.grid.GetCellValue(row,TRADE_ID_CELL_COL)
                    trade = session.query(MergeTrade).filter_by(id=trade_id).first()
                    company_regex = trade.logistics_company.reg_mail_no
                    id_compile = re.compile(company_regex)
                    is_out_sid_match = id_compile.match(str(start_out_sid))
                    if is_out_sid_match and trade.sys_status == cfg.SYS_STATUS_PREPARESEND:
                        self.grid.SetCellValue(row,OUT_SID_CELL_COL,str(start_out_sid))  
                        start_out_sid += 1
                    elif not is_out_sid_match:
                        dial = wx.MessageDialog(None, u'物流单号快递不符', '快递单号预览错误', 
                            wx.OK | wx.ICON_EXCLAMATION)
                        dial.ShowModal()
                        self.fill_sid_text.Clear()
                        self.refreshTable()
                        return
                self.end_sid = str(start_out_sid -1) 
            elif start_out_sid:
                min_row_num = min(self._selectedRows)
                trade_id = self.grid.GetCellValue(min_row_num,TRADE_ID_CELL_COL)
                trade = session.query(MergeTrade).filter_by(id=trade_id).first()
                company_regex = trade.logistics_company.reg_mail_no
                id_compile = re.compile(company_regex)
                if id_compile.match(str(start_out_sid)):
                    self.grid.SetCellValue(min_row_num ,OUT_SID_CELL_COL,start_out_sid)
                else:
                    self.refreshTable()
                    evt.Skip()
                    return 
        self.preview_btn.Enable(False)
        self.fill_sid_btn2.Enable(True)
        self.fill_sid_text.Clear()
        self.grid.ForceRefresh()
        evt.Skip()
    
    def disablePicklePrintBtn(self):
        """ 将打印配货单按钮设无效 """
        self.post_print_btn.Enable(False)
        
    def enablePicklePrintBtn(self):
        """ 将打印配货单按钮设有效 """
        self.post_print_btn.Enable(True)
    
    def onClickActiveButton(self,evt):
        eventid = evt.GetId()
        cf = getconfig()
        operator = cf.get('user','username') 
        with create_session(self.Parent) as session: 
            if eventid == fill_sid_btn2_id:
                for row in self._selectedRows:
                    try:
                        trade_id = self.grid.GetCellValue(row,TRADE_ID_CELL_COL)
                        out_sid = self.grid.GetCellValue(row,OUT_SID_CELL_COL)
                        trade = session.query(MergeTrade).filter_by(id=trade_id).first()
                        company_regex = trade.logistics_company.reg_mail_no if trade else None
                        is_match_pass = True
                        if company_regex:
                            id_compile = re.compile(company_regex)
                            is_match_pass = id_compile.match(out_sid)
                        if is_match_pass:
                            session.query(MergeTrade).filter_by(id=trade_id)\
                                .update({'out_sid':out_sid,'operator':operator},synchronize_session='fetch')
                            self.grid.SetCellValue(row,OUT_SID_CELL_COL,out_sid)
                            self.grid.SetCellValue(row,OPERATOR_CELL_COL,operator)
                        else:
                            break    
                    except:
                        break
                if len(self._selectedRows)>2:
                    self.disablePicklePrintBtn() 
                    self.fill_sid_btn2.Enable(False)
                    self.fill_sid_btn4.Enable(True) 
                else:      
                    self.fill_sid_btn2.Enable(False)
                    self.preview_btn.Enable(True)
                
            elif eventid == fill_sid_btn4_id:
                start_out_sid = self.out_sid_start_text.GetValue()
                end_out_sid   = self.out_sid_end_text.GetValue()

                if self.start_sid == start_out_sid and self.end_sid == end_out_sid:
                    self.enablePicklePrintBtn()
                    self.out_sid_start_text.Clear()
                    self.out_sid_end_text.Clear()
                    self.fill_sid_btn4.Enable(False)
                    self.preview_btn.Enable(True)
                    
            elif eventid == picking_print_btn_id:
                trade_ids = []
                for row in self._selectedRows:
                    out_sid = self.grid.GetCellValue(row,OUT_SID_CELL_COL)
                    operator = self.grid.GetCellValue(row,OPERATOR_CELL_COL)
                    if out_sid and operator:
                        trade_ids.append(self.grid.GetCellValue(row,TRADE_ID_CELL_COL))
                if trade_ids:
                    DeliveryPrinter(parent=self,trade_ids=trade_ids).ShowFullScreen(True,style=wx.FULLSCREEN_NOBORDER)
            
            elif eventid == express_print_btn_id:
                trade_ids = []
                pre_company_id = ''
                for row in self._selectedRows:
                    trade_id = self.grid.GetCellValue(row,TRADE_ID_CELL_COL)
                    trade = session.query(MergeTrade).filter_by(id=trade_id).first()
                    if pre_company_id and pre_company_id != trade.logistics_company_id:
                        dial = wx.MessageDialog(None, u'请确保批打订单快递相同', '快递单打印错误', 
                            wx.OK | wx.ICON_EXCLAMATION)
                        dial.ShowModal()
                        return
                    pre_company_id = trade.logistics_company_id
                    out_sid = trade.out_sid
                    operator = trade.operator
                    if out_sid and operator:
                        trade_ids.append(trade_id)
                if trade_ids:
                    ExpressPrinter(parent=self,trade_ids=trade_ids).ShowFullScreen(True,style=wx.FULLSCREEN_NOBORDER)
                    
            elif eventid == pickle_print_btn_id:
                PicklePrinter(parent=self).ShowFullScreen(True,style=wx.FULLSCREEN_ALL)#.Show()
            
            elif eventid == review_orders_btn_id:
                if len(self._selectedRows)==1:
                    trade_id = self.grid.GetCellValue(self._selectedRows.pop(),TRADE_ID_CELL_COL)
                    OrderReview(parent=self,trade_id=trade_id).ShowFullScreen(True,style=wx.FULLSCREEN_ALL)#.Show()

            elif eventid == scan_check_btn_id:
                self.Parent.Parent._mgr.GetPane("scan_check_content").Show()
                self.Parent.Parent._mgr.Update()
            
            elif eventid == scan_weight_btn_id:
                self.Parent.Parent._mgr.GetPane("scan_weight_content").Show()
                self.Parent.Parent._mgr.Update()          
        evt.Skip()

    def setupPager(self):
        self.lblPageIndex.SetLabel(str(self.page.number) if self.page else '0')
        self.lblPageCount.SetLabel(str(self.page.paginator.num_pages) if self.page else '0') 
        self.lblTotalCount.SetLabel(str(self.page.paginator.count) if self.page else '0')
        self.selected_counts.SetLabel(str(len(self._selectedRows)))
        self.btnFirst.Enable(self.page.paginator.num_pages >= 1 if self.page else False)
        self.btnPrev.Enable(self.page.has_previous() if self.page else False)
        self.btnNext.Enable(self.page.has_next() if self.page else False)
        self.btnLast.Enable(self.page.paginator.num_pages > 1 if self.page else False)
    
    def refreshTable(self):
        #修改状态后 ，刷新当前表单  
        trade_ids = self.getSelectTradeIds(self._selectedRows)
        tail_nums = self.Parent.getAllTailNums()
        if self.page:
            self.page = self.paginator.page(self.page.number)
            object_list = self.parseObjectToList(self.page.object_list,tail_nums)
        else:
            object_list = ()
        gridtable = weakref.ref(GridTable(object_list, self.rowLabels, self.colLabels, self.Parent.selectedRowColour))
        self.grid.SetTable(gridtable())
        self.grid.SetColSize(0, 20)
        self.grid.SetRowLabelSize(40)  
        self.updateCellBySelectedTradeIds(trade_ids)
        self.updateSelectAllCheck()
#        self.grid.ForceRefresh() 
    
    def updateCellBySelectedTradeIds(self,trade_ids):
        self._selectedRows.clear()
        rows  = self.grid.GetNumberRows()
        for row in xrange(0,rows):
            trade_id = self.grid.GetCellValue(row,TRADE_ID_CELL_COL)
            if trade_id in trade_ids:
                self._selectedRows.add(row)
                self.grid.SetCellValue(row,0,'1')
            
    def getSelectTradeIds(self,selectRows):
        trade_ids = []
        for row in selectRows:
            trade_id = self.grid.GetCellValue(int(row),TRADE_ID_CELL_COL)
            trade_ids.append(trade_id)
        return trade_ids
    
    def updateSelectAllCheck(self):
        row = self.grid.GetNumberRows()
        if row>0 and row==len(self._selectedRows):
            self.select_all_check.SetValue(True)
        else:
            self.select_all_check.SetValue(False)
    
    def updateTableAndPaginator(self):
        self._selectedRows.clear()
        tail_nums = self.Parent.getAllTailNums()
        if self.page:
            object_list = self.parseObjectToList(self.page.object_list,tail_nums)
        else:
            object_list = ()
           
        gridtable = weakref.ref(GridTable(object_list, self.rowLabels, self.colLabels,self.Parent.selectedRowColour))
        self.grid.SetTable(gridtable())
        self.grid.SetColSize(0, 20)
        self.grid.SetRowLabelSize(40)
        self.setupPager()
        for btn in self.button_array:
            btn.Enable(False)
        
        if len(object_list) == 1:
            self.grid.SetCellValue(0,0,'1')
            self.afterCheckBox(True,singleRecord=True)
            
        self.updateSelectAllCheck()
        
        self.inner_panel.Hide()
        self.inner_panel.Layout()
        self.Layout()
        self.grid.ForceRefresh()
    
     
    def parseObjectToList(self, object_list):
        raise NotImplement(u"parseObjectToList-该方法没有实现") 
        
    
    def onBtnFirstClick(self, evt):
        self.page = self.paginator.page(1)
        self.updateTableAndPaginator()
        
        
    def onBtnLastClick(self, evt):
        self.page = self.paginator.page(self.paginator.num_pages)
        self.updateTableAndPaginator()
    
    def onBtnPrevClick(self, evt):
        self.page = self.paginator.page(self.page.previous_page_number())
        self.updateTableAndPaginator()
    
    def onBtnNextClick(self, evt):
        self.page = self.paginator.page(self.page.next_page_number())
        self.updateTableAndPaginator()


class ListArrayGridPanel(GridPanel):
    
    def parseObjectToList(self, object_list):
        return object_list
    
   
class QueryObjectGridPanel(GridPanel):
     
    def parseObjectToList(self, object_list, tailnums=set()):
        assert isinstance(object_list,(list,tuple))
        assert isinstance(object_list,(set,list,tuple))
        parallel_num = self.Parent.client_num
        array_object = []
        for order in object_list:
            if not tailnums or order.id%parallel_num in tailnums:
                object_array = []
                object_array.append(order.id)
                object_array.append(order.seller_nick)
                object_array.append(order.buyer_nick)
                object_array.append(cfg.TRADE_TYPE.get(order.type,u'其他'))
                object_array.append(cfg.TRADE_STATUS.get(order.status,u'其他'))
                object_array.append(cfg.SYS_STATUS.get(order.sys_status,u'其他'))
                object_array.append(order.receiver_state+'-'+order.receiver_city)
                object_array.append(order.is_picking_print)
                object_array.append(order.is_express_print)
                object_array.append(order.can_review)
                object_array.append(order.logistics_company and order.logistics_company.name or '')
                object_array.append(order.out_sid)
                object_array.append(order.operator)
                object_array.append(str(order.total_num))
                object_array.append(order.payment)
                object_array.append(order.total_fee)
                object_array.append(order.pay_time)
                object_array.append(order.consign_time or '')
                object_array.append(order.weight_time or '')
                array_object.append(object_array)
        return array_object
    
    
    
class SimpleGridPanel(wx.Panel):
    def __init__(self, parent, id= -1, colLabels=None, rowLabels=None): 
        wx.Panel.__init__(self, parent, id) 
        
        self.Session = parent.Session
        self.rowLabels = rowLabels
        self.colLabels = colLabels
        self.grid =  grd.Grid(self, -1)
        self.setData(None)
        self.__set_properties()
        self.__do_layout()

        
    def __set_properties(self):
        self.SetName('simple_grid_panel')
    
    def __do_layout(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.grid,-1,flag=wx.EXPAND)
        self.SetSizer(main_sizer)
        self.Layout()

    def setData(self,trade,grid_table_type=SimpleGridTable):
        object_list = self.parseObjectToList(trade)
        gridtable = weakref.ref(grid_table_type(object_list, self.rowLabels, self.colLabels))
        self.grid.SetTable(gridtable(),True)
        self.grid.AutoSize()
        self.grid.SetColSize(0,50)
        for i in range(0,len(object_list)):
            self.grid.SetRowSize(i,50)
        self.grid.ForceRefresh()
        self.Layout()
    
    def parseObjectToList(self,trade):
        raise NotImplement(u"parseObjectToList-该方法没有实现")
        
 
class SimpleOrdersGridPanel(SimpleGridPanel):
     
    def parseObjectToList(self, trade):
        array_object = []
        if not trade :
            return array_object
        
        with create_session(self.Parent) as session:
            orders = session.query(MergeOrder).filter_by(merge_trade_id=trade.id,sys_status=cfg.IN_EFFECT)
            array_object = [] 
            for order in orders:
                object_array = []
                object_array.append(order.pic_path)
                object_array.append(order.id)
                object_array.append(order.outer_id or order.num_iid)
                object_array.append(order.title)
                object_array.append(order.outer_sku_id)
                object_array.append(order.sku_properties_name)
                object_array.append(order.num)
                object_array.append(order.price)
                object_array.append(order.payment)
                object_array.append(order.refund_id)
                object_array.append(cfg.REFUND_STATUS.get(order.refund_status,''))
                object_array.append(cfg.ORDER_TYPE.get(order.gift_type,u'其他'))
                object_array.append(cfg.TRADE_STATUS.get(order.status,'其他'))
                object_array.append(cfg.SYS_ORDERS_STATUS.get(order.sys_status,'其他'))
                array_object.append(object_array)
        return array_object
      
            
class WeightGridPanel(wx.Panel):
    def __init__(self, parent, id=-1): 
        wx.Panel.__init__(self, parent, id) 
        
        self.grid = grd.Grid(self,-1)
        colLabels = (u'内部单号',u'店铺简称',u'订单类型',u'会员名称',u'订单状态',u'系统状态',u'物流类型',u'称重重量',u'物流成本',u'实付邮费',
                     u'收货人',u'收货人固定电话',u'收货人手机',u'收货邮编',u'所在省',u'所在市',u'所在地区',u'收货地址')
        gridtable = weakref.ref(WeightGridTable(colLabels=colLabels))
        self.grid.SetTable(gridtable(),True)  
        self.grid.SetRowLabelSize(40)
        
        box_sizer = wx.BoxSizer(wx.HORIZONTAL)
        box_sizer.Add(self.grid,flag=wx.EXPAND)
        
        self.grid.SetMinSize((1300,500))
        self.SetSizer(box_sizer)
        self.Layout()
        
    def InsertTradeRows(self,trade):
        
        items = self.getTradeItems(trade)
        for index,item in enumerate(items):
            self.grid.SetCellValue(0,index,item)
            
        self.grid.InsertRows(0,1,True)
        self.grid.ProcessTableMessage(grd.GridTableMessage(
                                    self.grid.Table,grd.GRIDTABLE_NOTIFY_ROWS_INSERTED,0,1))
            
        self.grid.ForceRefresh()

    def getTradeItems(self,trade):
        items = []
        items.append(str(trade.id))
        items.append(trade.seller_nick)
        items.append(cfg.TRADE_TYPE.get(trade.type,u'其它'))
        items.append(trade.buyer_nick)
        items.append(cfg.TRADE_STATUS.get(trade.status,u'其它'))
        items.append(cfg.SYS_STATUS.get(trade.sys_status,u'其它'))
        items.append(cfg.SHIPPING_TYPE.get(trade.shipping_type,u'其它'))
        items.append(trade.weight)
        items.append(trade.post_cost)
        
        items.append(trade.post_fee)
        items.append(trade.receiver_name)
        items.append(trade.receiver_phone)
        items.append(trade.receiver_mobile)
        items.append(trade.receiver_zip)
        items.append(trade.receiver_state)
        items.append(trade.receiver_city)
        items.append(trade.receiver_district)
        items.append(trade.receiver_address)
        
        return items
      
      
class CheckOrdersGridPanel(SimpleGridPanel):
    #商品检验部分的panel 
    def parseObjectToList(self, trade):
        array_object = []
        if not trade :
            return array_object
        
        with create_session(self.Parent) as session:
            orders = get_used_orders(session,trade.id)
            from taobao.dao.models import Product
            array_object = [] 
            for order in orders:
                object_array = []     
                product = session.query(Product).filter_by(outer_id=order.outer_id).first()
                object_array.append(order.pic_path or product.pic_path)
                object_array.append(str(order.id))
                object_array.append(order.num_iid or order.outer_id)
                
                object_array.append(product.name if product else order.title)
                object_array.append(order.num)
                object_array.append(order.outer_id)
                object_array.append(order.outer_sku_id)
                object_array.append(order.sku_properties_name)
                object_array.append(cfg.TRADE_STATUS.get(order.status,'其他'))
                object_array.append(cfg.SYS_ORDERS_STATUS.get(order.sys_status,'其他'))
                object_array.append(0)
                
                array_object.append(object_array)
        return array_object
      

class CheckGridPanel(wx.Panel):
    
    def __init__(self,parent,id=-1):
        wx.Panel.__init__(self,parent,id)

        self.Session = parent.Session
        self.trade = None
        self.code_num_dict = {}
       
        colLabels = (u'商品图片',u'子订单ID',u'商品ID',u'商品简称',u'订购数量',u'商品外部编码',u'规格外部编码',u'规格属性',u'订单状态',u'系统状态',u'扫描次数')
        self.ordergridpanel = CheckOrdersGridPanel(self,colLabels=colLabels)
        
        self.__set_properties()
        self.__do_layout()
        
    def __set_properties(self):
        self.SetName('detail_panel')    
 
    def __do_layout(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.ordergridpanel,-1,wx.EXPAND)
        self.Layout()
        self.SetSizer(main_sizer)
      
    def getOrderCodeMapNumDict(self,trade):
        with create_session(self.Parent) as session:
            orders = get_used_orders(session,trade.id)
            code_num_dict = {}    
            for order in orders:
                barcode = order.outer_id+order.outer_sku_id
                if code_num_dict.has_key(barcode):
                    code_num_dict[barcode]['rnums'] += order.num
                else:
                    code_num_dict[barcode] = {'rnums':order.num,'cnums':0}
        return  code_num_dict
    
    def isCheckOver(self):
        for key,value in self.code_num_dict.items():
            if value['rnums'] != value['cnums']:
                return False
        return True
            
    
    def setBarCode(self,barcode):
        if barcode.lower() == 'pass':
            for key,value in self.code_num_dict.items():
                value['cnums'] = value['rnums']
            return True
        if self.code_num_dict.has_key(barcode):
            grid = self.ordergridpanel.grid
            self.code_num_dict[barcode]['cnums'] += 1
            for row in xrange(0,grid.NumberRows):
                outer_id     = grid.GetCellValue(row,OUTER_ID_COL)
                outer_sku_id = grid.GetCellValue(row,OUTER_SKU_ID_COL)
                code = outer_id+outer_sku_id
                if barcode == code:
                    grid.SetCellValue(row,NUM_STATUS_COL,str(self.code_num_dict[barcode]['cnums']))
                    return True
            grid.ForceRefresh()
        return False
        
        
    def setData(self,trade,grid_table_type=CheckGridTable):
        if not trade:
            return
        self.trade = trade
        self.ordergridpanel.setData(trade,grid_table_type=CheckGridTable)
        self.code_num_dict = self.getOrderCodeMapNumDict(trade)
        self.ordergridpanel.Layout()
        
                
