#-*- coding:utf8 -*-
'''
Created on 2012-7-13

@author: user1
'''
import re
import weakref
import time
import wx, wx.grid as grd
from taobao.frames.tables.gridtable import GridTable,SimpleGridTable,WeightGridTable
from taobao.frames.panels.itempanel import ItemPanel
from taobao.frames.tables.gridtable import CheckGridTable
from taobao.common.paginator import Paginator
from taobao.exception.exception import NotImplement
from taobao.common.utils import create_session,getconfig
from taobao.dao.models import MergeOrder,MergeTrade
from taobao.dao.configparams import TRADE_TYPE,SHIPPING_TYPE,SYS_STATUS,TRADE_STATUS,REFUND_STATUS
from taobao.dao.configparams import SYS_STATUS_ALL,SYS_STATUS_WAITAUDIT,SYS_STATUS_PREPARESEND,SYS_STATUS_WAITSCANCHECK,\
    SYS_STATUS_WAITSCANWEIGHT,SYS_STATUS_FINISHED,SYS_STATUS_INVALID,NO_REFUND,REFUND_CLOSED,SELLER_REFUSE_BUYER
from taobao.frames.prints.deliveryprinter import DeliveryPrinter 
from taobao.frames.prints.expressprinter import ExpressPrinter

TRADE_ID_CELL_COL = 1
LOG_COMPANY_CELL_COL = 11
OUT_SID_CELL_COL = 12
OUTER_ID_COL = 5
OUTER_SKU_ID_COL = 6
NUM_STATUS_COL = 9

fill_sid_btn_id = wx.NewId()
picking_print_btn_id = wx.NewId()
express_print_btn_id = wx.NewId()
scan_check_btn_id = wx.NewId()
scan_weight_btn_id = wx.NewId()

fill_sid_btn2_id = wx.NewId()

class GridPanel(wx.Panel):
    def __init__(self, parent, id= -1, colLabels=None, rowLabels=None): 
        wx.Panel.__init__(self, parent, id) 
        
        self.Session = parent.Session
        self.datasource = None
        self.paginator = self.page = None
        self.page_size = 50
        self.rowLabels = rowLabels
        self.colLabels = colLabels
        self.grid = grd.Grid(self, -1)
        
        self._selectedRows = set()
        self.select_all_label = wx.StaticText(self,-1,u'  全  选')
        self.select_all_check = wx.CheckBox(self,-1)
        self.pt1 = wx.StaticText(self, -1, u",第")
        self.pt2 = wx.StaticText(self, -1, u"/")
        self.pt3 = wx.StaticText(self, -1, u"页(共")
        self.pt5 = wx.StaticText(self, -1, u"条记录,已选中 ") 
        self.pt6 = wx.StaticText(self,-1,u" 条),每页")
        self.lblPageIndex = wx.StaticText(self, -1, "0")
        self.lblPageCount = wx.StaticText(self, -1, "0")
        self.lblTotalCount = wx.StaticText(self, -1, "0")
        self.selected_counts = wx.StaticText(self,-1,'0')
        self.page_size_select = wx.ComboBox(self,-1,choices=('20','50','100','200','500','1000','5000'),value='50')
        self.btnFirst = wx.Button(self, -1, label=u'首页', style=0)
        self.btnLast = wx.Button(self, -1, label=u'尾页', style=0)
        self.btnPrev = wx.Button(self, -1, label=u'上一页', style=0)
        self.btnNext = wx.Button(self, -1, label=u'下一页', style=0)
   
        self.fill_sid_btn = wx.Button(self, fill_sid_btn_id, label=u'填物流单号',name=u'打印发货单前，需将物流单号与订单绑定')
        self.picking_print_btn = wx.Button(self, picking_print_btn_id, label=u'打印发货单',name=u'打印发货单，进行配货')
        self.express_print_btn = wx.Button(self,express_print_btn_id,label=u'打印物流单',name=u'打印物流单，为扫描称重准备')
        self.scan_check_btn = wx.Button(self,scan_check_btn_id,label=u'扫描验货',name=u'对发货包裹进行检验，确认是否缺货')
        self.scan_weight_btn = wx.Button(self,scan_weight_btn_id,label=u'扫描称重',name=u'对发货包裹进行称重，物流结算')
        
        self.button_array = []
        
        self.inner_panel  = wx.Panel(self,-1)
        self.fill_sid_panel   = wx.Panel(self.inner_panel,-1)
        self.fill_sid_label1  = wx.StaticText(self.fill_sid_panel,-1,u'起始物流单号')
        self.fill_sid_text   = wx.TextCtrl(self.fill_sid_panel,-1,size=(200,-1))
        self.fill_sid_label2  = wx.StaticText(self.fill_sid_panel,-1,u'自增物流单号')
        self.fill_sid_checkbox1   = wx.CheckBox(self.fill_sid_panel,-1)
        self.preview_btn      = wx.Button(self.fill_sid_panel,-1,u'预览')
        self.fill_sid_btn2   = wx.Button(self.fill_sid_panel,fill_sid_btn2_id,u'确定')
        self.fill_sid_btn3   = wx.Button(self.fill_sid_panel,-1,u'取消')

        self.static_button_down = wx.Button(self,-1,label='v------------v',size=(-1,11))
        self.isSearchPanelShow = True
        
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
        self.scan_check_btn.SetFont(font)
        self.scan_weight_btn.SetFont(font)
        
        self.fill_sid_checkbox1.SetValue(True)
        
        self.button_array.append(self.fill_sid_btn)
        self.button_array.append(self.picking_print_btn)
        self.button_array.append(self.express_print_btn)
        
        self.fill_sid_btn2.Enable(False)


        
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
        fg.Add((20,20),0,14)
  
        fg.Add(self.scan_check_btn,0,17)
        fg.Add(self.fill_sid_btn, 0, 18)
        fg.Add(self.picking_print_btn, 0, 19) 
        fg.Add(self.express_print_btn, 0, 20)
        fg.Add(self.scan_weight_btn, 0, 22)
        
        self.fill_sid_sizer = wx.FlexGridSizer(hgap=15, vgap=15)
        self.fill_sid_sizer.Add(self.fill_sid_label1,0,0)
        self.fill_sid_sizer.Add(self.fill_sid_text,0,1)
        self.fill_sid_sizer.Add(self.fill_sid_label2,0,2)
        self.fill_sid_sizer.Add(self.fill_sid_checkbox1,0,3)
        self.fill_sid_sizer.Add(self.preview_btn,0,4)
        self.fill_sid_sizer.Add(self.fill_sid_btn2,0,5)
        self.fill_sid_sizer.Add(self.fill_sid_btn3,0,6)
        self.fill_sid_panel.SetSizer(self.fill_sid_sizer)

        self.inner_box_sizer = wx.BoxSizer(wx.VERTICAL) 
        self.inner_box_sizer.Add(self.fill_sid_panel,proportion=0,flag=wx.EXPAND)
        self.inner_panel.SetSizer(self.inner_box_sizer)
        
        main_sizer.Add(self.grid, 5, wx.EXPAND)
        main_sizer.Add(fg, flag=wx.RIGHT|wx.EXPAND) 
        main_sizer.Add(wx.StaticLine(self,-1),flag=wx.EXPAND)
        main_sizer.Add(self.inner_panel,flag=wx.EXPAND)
        main_sizer.Add(self.static_button_down,flag=wx.RIGHT|wx.EXPAND)
        main_sizer.Add(self.itempanel,3,flag=wx.RIGHT|wx.EXPAND)
        
        self.SetSizer(main_sizer)
    
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
        self.Bind(wx.EVT_BUTTON, self.onClickActiveButton,self.picking_print_btn)
        self.Bind(wx.EVT_BUTTON, self.onClickActiveButton,self.express_print_btn)
        self.Bind(wx.EVT_BUTTON, self.onClickActiveButton,self.scan_check_btn)
        self.Bind(wx.EVT_BUTTON, self.onClickActiveButton,self.scan_weight_btn)

        
    def setDataSource(self, status_type): 
        with create_session(self.Parent) as session: 
            datasource     = session.query(MergeTrade)
            if status_type and status_type != SYS_STATUS_ALL:
                datasource = datasource.filter_by(sys_status=status_type)
        self.datasource = datasource
        self.paginator = paginator = Paginator(datasource, self.page_size)
        self.page = paginator.page(1)
        
        self.fill_sid_btn.Show(status_type in (SYS_STATUS_PREPARESEND))
        self.picking_print_btn.Show(status_type in (SYS_STATUS_PREPARESEND))
        self.express_print_btn.Show(status_type in (SYS_STATUS_PREPARESEND))
        self.scan_check_btn.Show(status_type in (SYS_STATUS_WAITSCANCHECK))
        self.scan_weight_btn.Show(status_type in (SYS_STATUS_WAITSCANWEIGHT))
        self.updateTableAndPaginator()
        self.select_all_check.SetValue(False)
        
    def setSearchData(self, datasource):
        self.paginator = paginator = Paginator(datasource, self.page_size)
        self.page = paginator.page(1)
        self.updateTableAndPaginator()
        self.select_all_check.SetValue(False)
   
    def onMouse(self,evt):
        if evt.Col == 0:
            row  = evt.Row
            wx.CallLater(100,self.toggleCheckBox,row)
        evt.Skip()

    def toggleCheckBox(self,row):
        if hasattr(self.grid,'cb'):
            self.grid.cb.Value = not self.grid.cb.Value
            self.afterCheckBox(self.grid.cb.Value,row)
    
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
    
    def onCellSelected(self, evt):
        if evt.Col == 0:
            self.grid._curow = evt.Row
            wx.CallAfter(self.grid.EnableCellEditControl)
        evt.Skip()

    def onEditorCreated(self, evt):
        if evt.Col == 0:
            self.grid.cb = evt.Control
            self.grid.cb.WindowStyle |= wx.WANTS_CHARS
            self.grid.cb.Bind(wx.EVT_CHECKBOX, self.onCheckBox)
        evt.Skip()


    def onCheckBox(self, evt):
        row = self.grid._curow
        self.afterCheckBox(evt.IsChecked(),row)
        evt.Skip()
    
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
     
    def afterCheckBox(self, isChecked,row):
        self.grid._curow = row
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
        self.updateGridCheckBoxValue()
        self.grid.ForceRefresh()
        self.selected_counts.SetLabel(str(len(self._selectedRows)))
        self.Layout()

    
    def updateGridCheckBoxValue(self):
        rows  = self.grid.GetNumberRows()
        for row in xrange(0,rows):
            if row in self._selectedRows:
                self.grid.SetCellValue(row,0,'1')
            else:
                self.grid.SetCellValue(row,0,'')
    
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
        if self.isSearchPanelShow:
            self.itempanel.Hide()
            self.static_button_down.SetLabel('^------------^')
            self.isSearchPanelShow = False
        else:
            self.itempanel.Show()
            self.static_button_down.SetLabel('v------------v')
            self.isSearchPanelShow = True
        self.Layout()    
            
    def fillOutSidToCell(self,evt):
        start_out_sid = self.fill_sid_text.GetValue()
        is_auto_fill  = self.fill_sid_checkbox1.IsChecked()
        with create_session(self.Parent) as session:
            if start_out_sid.isdigit() and is_auto_fill:
                start_out_sid = int(start_out_sid)
                for row in self._selectedRows:
                    trade_id = self.grid.GetCellValue(row,TRADE_ID_CELL_COL)
                    trade = session.query(MergeTrade).filter_by(id=trade_id).first()
                    company_regex = trade.logistics_company.reg_mail_no
                    id_compile = re.compile(company_regex)
                    if id_compile.match(str(start_out_sid)):
                        self.grid.SetCellValue(row,OUT_SID_CELL_COL,str(start_out_sid))  
                        start_out_sid += 1
            elif start_out_sid.isdigit():
                min_row_num = min(self._selectedRows)
                trade_id = self.grid.GetCellValue(row,TRADE_ID_CELL_COL)
                trade = session.query(MergeTrade).filter_by(id=trade_id).first()
                company_regex = trade.logistics_company.reg_mail_no
                id_compile = re.compile(company_regex)
                if id_compile.match(str(start_out_sid)):
                    self.grid.SetCellValue(min_row_num ,OUT_SID_CELL_COL,start_out_sid)
        self.fill_sid_btn2.Enable(True)
        self.fill_sid_text.Clear()
        self.grid.ForceRefresh()
        evt.Skip()
    
    
    def onClickActiveButton(self,evt):
        eventid = evt.GetId()
        cf = getconfig()
        operator = cf.get('user','username') 
        with create_session(self.Parent) as session: 
            if eventid == fill_sid_btn2_id:
                for row in self._selectedRows:
                    trade_id = self.grid.GetCellValue(row,TRADE_ID_CELL_COL)
                    out_sid = self.grid.GetCellValue(row,OUT_SID_CELL_COL)
                    trade = session.query(MergeTrade).filter_by(id=trade_id).first()
                    company_code = trade.logistics_company.code if trade else None
                    company_regex = trade.logistics_company.reg_mail_no if trade else None
                    id_compile = re.compile(company_regex)
                    if id_compile.match(out_sid) and not trade.operator:
                        session.query(MergeTrade).filter_by(id=trade_id)\
                            .update({'out_sid':out_sid,'operator':operator},synchronize_session='fetch')
                self.refreshTable()
                self.fill_sid_btn2.Enable(False)
                
            elif eventid == picking_print_btn_id:
                trade_ids = []
                for row in self._selectedRows:
                    trade_ids.append(self.grid.GetCellValue(row,1))
                DeliveryPrinter(parent=self,trade_ids=trade_ids).Show()
            
            elif eventid == express_print_btn_id:
                trade_ids = []
                pre_company_name = ''
                for row in self._selectedRows:
                    trade_id = self.grid.GetCellValue(row,TRADE_ID_CELL_COL)
                    company_name = self.grid.GetCellValue(row,LOG_COMPANY_CELL_COL)
                    if pre_company_name and pre_company_name !=company_name:
                        return
                    pre_company_name = company_name
                    trade_ids.append(trade_id)
                    
                ExpressPrinter(parent=self,trade_ids=trade_ids).Show()
            
            elif eventid == scan_check_btn_id:
                self.Parent.Parent._mgr.GetPane("scan_check_content").Show()
                self.Parent.Parent._mgr.Update()
            
            elif eventid == scan_weight_btn_id:
                self.Parent.Parent._mgr.GetPane("scan_weight_content").Show()
                self.Parent.Parent._mgr.Update()
                
        

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
        if self.page:
            self.page = self.paginator.page(self.page.number)
            object_list = self.parseObjectToList(self.page.object_list,self.Parent.selecttailnums)
        else:
            object_list = ()
        gridtable = weakref.ref(GridTable(object_list, self.rowLabels, self.colLabels, self.Parent.selectedRowColour))
        self.grid.SetTable(gridtable())
        self.grid.SetColSize(0, 20)
        self.grid.SetRowLabelSize(40)  
        self.updateCellBySelectedTradeIds(trade_ids)
        self.grid.ForceRefresh() 
    
    def updateCellBySelectedTradeIds(self,trade_ids):
        self._selectedRows.clear()
        rows  = self.grid.GetNumberRows()
        for row in xrange(0,rows):
            trade_id = self.grid.GetCellValue(row,TRADE_ID_CELL_COL)
            if trade_id in trade_ids:
                self._selectedRows.add(row)
        self.updateGridCheckBoxValue()
            
    def getSelectTradeIds(self,selectRows):
        trade_ids = []
        for row in selectRows:
            trade_id = self.grid.GetCellValue(int(row),TRADE_ID_CELL_COL)
            trade_ids.append(trade_id)
        return trade_ids
    
    def updateTableAndPaginator(self):
        self._selectedRows.clear()
        if self.page:
            object_list = self.parseObjectToList(self.page.object_list,self.Parent.selecttailnums)
        else:
            object_list = ()
           
        gridtable = weakref.ref(GridTable(object_list, self.rowLabels, self.colLabels,self.Parent.selectedRowColour))
        self.grid.SetTable(gridtable())
        self.grid.SetColSize(0, 20)
        self.grid.SetRowLabelSize(40)
        self.setupPager()
        for btn in self.button_array:
            btn.Enable(False)
        
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
        array_object = []
        for object in object_list:
            if not tailnums or object.tid%10 in tailnums:
                object_array = []
                object_array.append(object.id)
                object_array.append(object.seller_nick)
                object_array.append(object.buyer_nick)
                object_array.append(TRADE_TYPE.get(object.type,u'其他'))
                object_array.append(TRADE_STATUS.get(object.status,u'其他'))
                object_array.append(SYS_STATUS.get(object.sys_status,u'其他'))
                object_array.append(SHIPPING_TYPE.get(object.shipping_type,u'其他'))
                object_array.append(object.is_picking_print)
                object_array.append(object.is_express_print)
                object_array.append(object.is_send_sms)
                object_array.append(object.logistics_company and object.logistics_company.name or '')
                object_array.append(object.out_sid)
                object_array.append(object.operator)
                object_array.append(object.post_cost)
                object_array.append(object.payment)
                object_array.append(object.total_fee)
                object_array.append(str(object.total_num))
                object_array.append(object.pay_time)
                object_array.append(object.consign_time or '')
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
        #该panel中的表格是否可编辑
        if hasattr(self.Parent.Parent,'is_changeable'):
            if self.Parent.Parent.is_changeable:
                self.grid.EnableEditing(True)
            else:
                self.grid.EnableEditing(False)
        self.Layout()
    
    def parseObjectToList(self,trade):
        raise NotImplement(u"parseObjectToList-该方法没有实现")
        
 
class SimpleOrdersGridPanel(SimpleGridPanel):
     
    def parseObjectToList(self, trade):
        array_object = []
        if not trade :
            return array_object
        
        with create_session(self.Parent) as session:
            orders = session.query(MergeOrder).filter_by(merge_trade_id=trade.id)
            from taobao.dao.models import Product
            array_object = [] 
            for object in orders:
                object_array = []
                object_array.append(object.pic_path)
                object_array.append(object.id)
                object_array.append(object.outer_id or object.num_iid)
                object_array.append(object.title)
                object_array.append(object.outer_sku_id)
                object_array.append(object.sku_properties_name)
                object_array.append(object.num)
                object_array.append(object.price)
                object_array.append(object.payment)
                
                object_array.append(object.refund_id)
                object_array.append(REFUND_STATUS.get(object.refund_status,''))
                object_array.append(TRADE_STATUS.get(object.status,'其他'))
    
                array_object.append(object_array)
        return array_object
      
            
class WeightGridPanel(wx.Panel):
    def __init__(self, parent, id= -1): 
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
        items.append(TRADE_TYPE.get(trade.type,u'其它'))
        items.append(trade.buyer_nick)
        items.append(TRADE_STATUS.get(trade.status,u'其它'))
        items.append(SYS_STATUS.get(trade.sys_status,u'其它'))
        items.append(SHIPPING_TYPE.get(trade.shipping_type,u'其它'))
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
            orders = session.query(MergeOrder).filter_by(merge_trade_id=trade.id).filter(
                    MergeOrder.status.in_(('WAIT_SELLER_SEND_GOODS','WAIT_CONFIRM,WAIT_SEND_GOODS','CONFIRM_WAIT_SEND_GOODS')),
                    MergeOrder.refund_status.in_((NO_REFUND,REFUND_CLOSED,SELLER_REFUSE_BUYER)))
            from taobao.dao.models import Product
            array_object = [] 
            for object in orders:
                object_array = []     
                product = session.query(Product).filter_by(outer_id=object.outer_id).first()
                object_array.append(object.pic_path)
                object_array.append(str(object.id))
                object_array.append(object.outer_id or object.num_iid)
                
                object_array.append(product.name if product else '')
                object_array.append(object.num)
                object_array.append(object.outer_id)
                object_array.append(object.outer_sku_id)
                object_array.append(object.sku_properties_name)
                object_array.append(TRADE_STATUS.get(object.status,'其他'))
                object_array.append(0)
                
                array_object.append(object_array)
        return array_object
      

class CheckGridPanel(wx.Panel):
    
    def __init__(self,parent,id=-1):
        wx.Panel.__init__(self,parent,id)

        self.Session = parent.Session
        self.trade = None
        self.code_num_dict = {}
       
        colLabels = (u'商品图片',u'子订单ID',u'商品ID',u'商品简称',u'订购数量',u'商品外部编码',u'规格外部编码',u'规格属性',u'订单状态',u'扫描次数')
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
        is_fenxiao = self.trade.type =='fenxiao'
        with create_session(self.Parent) as session:
            orders = session.query(MergeOrder).filter_by(merge_trade_id=trade.id)
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
        
                