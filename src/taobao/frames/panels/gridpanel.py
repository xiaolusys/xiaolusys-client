#-*- coding:utf8 -*-
'''
Created on 2012-7-13

@author: user1
'''
import re
import weakref
import wx, wx.grid as grd
from taobao.frames.tables.gridtable import GridTable,SimpleGridTable
from taobao.frames.panels.itempanel import ItemPanel
from taobao.common.paginator import Paginator
from taobao.exception.exception import NotImplement
from taobao.dao.models import Order,SubPurchaseOrder,Refund,MergeTrade,LogisticsCompany
from taobao.dao.configparams import TRADE_TYPE,SHIPPING_TYPE,SYS_STATUS,TRADE_STATUS,REFUND_STATUS
from taobao.dao.configparams import SYS_STATUS_UNAUDIT,SYS_STATUS_AUDITFAIL,SYS_STATUS_PREPARESEND,\
    SYS_STATUS_SCANWEIGHT,SYS_STATUS_CONFIRMSEND,SYS_STATUS_FINISHED,SYS_STATUS_INVALID
from taobao.frames.prints.deliveryprinter import DeliveryPrinter 
from taobao.frames.prints.expressprinter import ExpressPrinter


edit_trade_item_btn_id = wx.NewId()
audit_pass_btn_id = wx.NewId()
reverse_audit_btn_id = wx.NewId()
fill_sid_btn_id = wx.NewId()
picking_print_btn_id = wx.NewId()
express_print_btn_id = wx.NewId()
prepare_finish_btn_id = wx.NewId()
scan_weight_btn_id = wx.NewId()
confirm_delivery_btn_id = wx.NewId()
reaudit_btn_id = wx.NewId()
invalid_btn_id = wx.NewId()

fill_sid_btn2_id = wx.NewId()
reverse_audit_btn2_id = wx.NewId()
invalid_btn2_id = wx.NewId()
class GridPanel(wx.Panel):
    def __init__(self, parent, id= -1, colLabels=None, rowLabels=None): 
        wx.Panel.__init__(self, parent, id) 
        
        self.session = parent.session
        self.datasource = None
        self.paginator = self.page = None
        self.page_size = 50
        self.rowLabels = rowLabels
        self.colLabels = colLabels
        self.grid = grid = grd.Grid(self, -1)
        
        self._selectedRows = set()
        self.select_all_label = wx.StaticText(self,-1,'  全  选')
        self.select_all_check = wx.CheckBox(self,-1)
        self.pt1 = wx.StaticText(self, -1, ",第")
        self.pt2 = wx.StaticText(self, -1, "/")
        self.pt3 = wx.StaticText(self, -1, "页(共")
        self.pt5 = wx.StaticText(self, -1, "条记录,已选中 ") 
        self.pt6 = wx.StaticText(self,-1,"条),每页")
        self.lblPageIndex = wx.StaticText(self, -1, "0")
        self.lblPageCount = wx.StaticText(self, -1, "0")
        self.lblTotalCount = wx.StaticText(self, -1, "0")
        self.selected_counts = wx.StaticText(self,-1,'0')
        self.page_size_select = wx.ComboBox(self,-1,choices=('20','50','100','200','500','1000','5000'),value='50')
        self.btnFirst = wx.Button(self, -1, label='首页', style=0)
        self.btnLast = wx.Button(self, -1, label='尾页', style=0)
        self.btnPrev = wx.Button(self, -1, label='上一页', style=0)
        self.btnNext = wx.Button(self, -1, label='下一页', style=0)
   
        self.edit_trade_item_btn  = wx.Button(self, edit_trade_item_btn_id, label='修改订单',name='修改交易订单属性')
        self.audit_pass_btn = wx.Button(self, audit_pass_btn_id, label='审核通过',name='订单信息完整无误，可以准备发货')
        self.reverse_audit_btn = wx.Button(self, reverse_audit_btn_id, label='反审核',name='订单暂时不能准备发货，需重审再确定')
        self.fill_sid_btn = wx.Button(self, fill_sid_btn_id, label='填物流单号',name='打印发货单前，需将物流单号与订单绑定')
        self.picking_print_btn = wx.Button(self, picking_print_btn_id, label='打印发货单',name='打印发货单，进行配货')
        self.express_print_btn = wx.Button(self,express_print_btn_id,label='打印物流单',name='打印物流单，为扫描称重准备')
        self.prepare_finish_btn = wx.Button(self,prepare_finish_btn_id,label='准备完成',name='发货准备完成')
        self.scan_weight_btn = wx.Button(self,scan_weight_btn_id,label='扫描称重',name='对发货包裹进行称重，物流结算')
        self.confirm_delivery_btn = wx.Button(self,confirm_delivery_btn_id,label='确认发货',name='确定订单可以发货，同步淘宝后台')
        self.reaudit_btn = wx.Button(self,reaudit_btn_id,label='重审通过',name='审核未通过的订单，重新准备发货')
        self.invalid_btn = wx.Button(self,invalid_btn_id,label='作废',name='订单已经无效，作废处理')
        
        self.button_array = []
        
        self.inner_panel  = wx.Panel(self,-1)
        self.fill_sid_panel   = wx.Panel(self.inner_panel,-1)
        self.fill_sid_label1  = wx.StaticText(self.fill_sid_panel,-1,'起始物流单号')
        self.fill_sid_text   = wx.TextCtrl(self.fill_sid_panel,-1,size=(200,-1))
        self.fill_sid_label2  = wx.StaticText(self.fill_sid_panel,-1,'自动自增物流单号')
        self.fill_sid_checkbox1   = wx.CheckBox(self.fill_sid_panel,-1)
        self.preview_btn      = wx.Button(self.fill_sid_panel,-1,'预览')
        self.fill_sid_btn2   = wx.Button(self.fill_sid_panel,fill_sid_btn2_id,'确定')
        self.fill_sid_btn3   = wx.Button(self.fill_sid_panel,-1,'取消')

        self.reverse_audit_panel   = wx.Panel(self.inner_panel,-1)
        self.reverse_audit_label  = wx.StaticText(self.reverse_audit_panel,-1,'反审核理由')
        self.reverse_audit_text  = wx.TextCtrl(self.reverse_audit_panel,-1,size=(900,-1))
        self.reverse_audit_btn2   = wx.Button(self.reverse_audit_panel,reverse_audit_btn2_id,'确定')
        self.reverse_audit_btn3   = wx.Button(self.reverse_audit_panel,-1,'取消')
        
        self.invalid_panel   = wx.Panel(self.inner_panel,-1)
        self.invalid_label1  = wx.StaticText(self.invalid_panel,-1,'作废理由')
        self.invalid_text  = wx.TextCtrl(self.invalid_panel,-1,size=(900,-1))
        self.invalid_btn2   = wx.Button(self.invalid_panel,-1,'确定')
        self.invalid_btn3   = wx.Button(self.invalid_panel,-1,'取消')
        
        
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
        self.edit_trade_item_btn.SetFont(font)
        self.audit_pass_btn.SetFont(font)
        self.reverse_audit_btn.SetFont(font)
        self.fill_sid_btn.SetFont(font)
        self.picking_print_btn.SetFont(font)
        self.express_print_btn.SetFont(font)
        self.prepare_finish_btn.SetFont(font)
        self.scan_weight_btn.SetFont(font)
        self.confirm_delivery_btn.SetFont(font)
        self.reaudit_btn.SetFont(font)
        self.invalid_btn.SetFont(font)
        
        self.button_array.append(self.edit_trade_item_btn)
        self.button_array.append(self.audit_pass_btn)
        self.button_array.append(self.reverse_audit_btn)
        self.button_array.append(self.fill_sid_btn)
        self.button_array.append(self.picking_print_btn)
        self.button_array.append(self.express_print_btn)
        self.button_array.append(self.prepare_finish_btn)
        #self.button_array.append(self.scan_weight_btn)
        self.button_array.append(self.confirm_delivery_btn)
        self.button_array.append(self.reaudit_btn)
        self.button_array.append(self.invalid_btn)
        
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
        fg.Add(self.edit_trade_item_btn, 0, 16)
        fg.Add(self.audit_pass_btn, 0, 17) 
        fg.Add(self.fill_sid_btn, 0, 18)
        fg.Add(self.picking_print_btn, 0, 19) 
        fg.Add(self.express_print_btn, 0, 20)
        fg.Add(self.prepare_finish_btn,0,21)
        fg.Add(self.scan_weight_btn, 0, 22)
        fg.Add(self.confirm_delivery_btn, 0, 23) 
        fg.Add(self.reaudit_btn, 0, 24)
        fg.Add(self.reverse_audit_btn, 0, 25)
        fg.Add(self.invalid_btn,0,26)
        
        self.fill_sid_sizer = wx.FlexGridSizer(hgap=15, vgap=15)
        self.fill_sid_sizer.Add(self.fill_sid_label1,0,0)
        self.fill_sid_sizer.Add(self.fill_sid_text,0,1)
        self.fill_sid_sizer.Add(self.fill_sid_label2,0,2)
        self.fill_sid_sizer.Add(self.fill_sid_checkbox1,0,3)
        self.fill_sid_sizer.Add(self.preview_btn,0,4)
        self.fill_sid_sizer.Add(self.fill_sid_btn2,0,5)
        self.fill_sid_sizer.Add(self.fill_sid_btn3,0,6)
        self.fill_sid_panel.SetSizer(self.fill_sid_sizer)
        
        self.reverse_audit_sizer = wx.FlexGridSizer(hgap=10, vgap=10)
        self.reverse_audit_sizer.Add(self.reverse_audit_label,0,0)
        self.reverse_audit_sizer.Add(self.reverse_audit_text,0,1)
        self.reverse_audit_sizer.Add(self.reverse_audit_btn2,0,2)
        self.reverse_audit_sizer.Add(self.reverse_audit_btn3,0,3)
        self.reverse_audit_panel.SetSizer(self.reverse_audit_sizer)
        
        self.invalid_sizer = wx.FlexGridSizer(hgap=10, vgap=10)
        self.invalid_sizer.Add(self.invalid_label1,0,0)
        self.invalid_sizer.Add(self.invalid_text,0,1)
        self.invalid_sizer.Add(self.invalid_btn2,0,2)
        self.invalid_sizer.Add(self.invalid_btn3,0,3)
        self.invalid_panel.SetSizer(self.invalid_sizer)

        self.inner_box_sizer = wx.BoxSizer(wx.VERTICAL) 
        self.inner_box_sizer.Add(self.fill_sid_panel,proportion=0,flag=wx.EXPAND)
        self.inner_box_sizer.Add(self.reverse_audit_panel,proportion=0,flag=wx.EXPAND)
        self.inner_box_sizer.Add(self.invalid_panel,proportion=0,flag=wx.EXPAND)
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
        self.Bind(wx.EVT_BUTTON, self.onChangeFlexSizer,self.reverse_audit_btn)
        self.Bind(wx.EVT_BUTTON, self.onChangeFlexSizer,self.invalid_btn)
        
        self.Bind(wx.EVT_BUTTON, self.onClickHideInnerPanel,self.fill_sid_btn3 )
        self.Bind(wx.EVT_BUTTON, self.onClickHideInnerPanel,self.reverse_audit_btn3)
        self.Bind(wx.EVT_BUTTON, self.onClickHideInnerPanel,self.invalid_btn3 )
        
        self.Bind(wx.EVT_BUTTON,self.onClickStaticButton,self.static_button_down)
        
        self.Bind(wx.EVT_BUTTON, self.fillOutSidToCell,self.preview_btn)
        
        
        #分页栏，订单操作事件
        self.Bind(wx.EVT_BUTTON, self.onClickActiveButton,self.edit_trade_item_btn)
        self.Bind(wx.EVT_BUTTON, self.onClickActiveButton,self.audit_pass_btn)
        self.Bind(wx.EVT_BUTTON, self.onClickActiveButton,self.reverse_audit_btn2)
        self.Bind(wx.EVT_BUTTON, self.onClickActiveButton,self.fill_sid_btn2)
        self.Bind(wx.EVT_BUTTON, self.onClickActiveButton,self.picking_print_btn)
        self.Bind(wx.EVT_BUTTON, self.onClickActiveButton,self.express_print_btn)
        self.Bind(wx.EVT_BUTTON, self.onClickActiveButton,self.prepare_finish_btn)
        #self.Bind(wx.EVT_BUTTON, self.onClickActiveButton,self.scan_weight_btn)
        self.Bind(wx.EVT_BUTTON, self.onClickActiveButton,self.confirm_delivery_btn)
        self.Bind(wx.EVT_BUTTON, self.onClickActiveButton,self.confirm_delivery_btn)
        self.Bind(wx.EVT_BUTTON, self.onClickActiveButton,self.reaudit_btn)
        self.Bind(wx.EVT_BUTTON, self.onClickActiveButton,self.invalid_btn2)
        
    
    def setDataSource(self, datasource):
        self.datasource = datasource
        self.paginator = paginator = Paginator(datasource, self.page_size)
        self.page = paginator.page(1)
        
        status_type = self.datasource.status_type
        self.edit_trade_item_btn.Show(status_type in (SYS_STATUS_UNAUDIT,SYS_STATUS_AUDITFAIL,))
        self.audit_pass_btn.Show(status_type in (SYS_STATUS_UNAUDIT))
        self.reverse_audit_btn.Show(status_type in (SYS_STATUS_UNAUDIT,SYS_STATUS_PREPARESEND,SYS_STATUS_SCANWEIGHT,SYS_STATUS_CONFIRMSEND))
        self.fill_sid_btn.Show(status_type in (SYS_STATUS_PREPARESEND))
        self.picking_print_btn.Show(status_type in (SYS_STATUS_PREPARESEND))
        self.express_print_btn.Show(status_type in (SYS_STATUS_PREPARESEND))
        self.prepare_finish_btn.Show(status_type in (SYS_STATUS_PREPARESEND))
        self.scan_weight_btn.Show(status_type in (SYS_STATUS_SCANWEIGHT))
        self.confirm_delivery_btn.Show(status_type in (SYS_STATUS_CONFIRMSEND))
        self.reaudit_btn.Show(status_type in (SYS_STATUS_AUDITFAIL))
        self.invalid_btn.Show(status_type in (SYS_STATUS_AUDITFAIL))
        
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
        item = wx.MenuItem(menu,self.popupID1,'刷新')
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
        self.reverse_audit_panel.Show(eventid == reverse_audit_btn_id)
        self.invalid_panel.Show(eventid == invalid_btn_id)
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
        rows  = self.grid.GetRowSize(0)
        for row in xrange(0,rows):
            if row in self._selectedRows:
                self.grid.SetCellValue(row,0,'1')
            else:
                self.grid.SetCellValue(row,0,'')
    
    def setSelectedRowBlue(self):
        """ 改变选中行的颜色 """
        for row in self._selectedRows:
            col = self.grid.GetColSize(row)
            for j in xrange(1,col):
                self.grid.SetCellBackgroundColour(row,j,'navy')
    
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
        if start_out_sid.isdigit() and is_auto_fill:
            start_out_sid = int(start_out_sid)
            for row in self._selectedRows:
                self.grid.SetCellValue(row,13,str(start_out_sid))
                start_out_sid += 1
        elif start_out_sid.isdigit():
            min_row_num = min(self._selectedRows)
            self.grid.SetCellValue(min_row_num ,13,start_out_sid)
        self.fill_sid_btn2.Enable(True)
        self.fill_sid_text.Clear()
        self.grid.ForceRefresh()
        evt.Skip()
    
    
    def onClickActiveButton(self,evt):
        eventid = evt.GetId()
        if eventid == edit_trade_item_btn_id:
            self.itempanel.refreshData()
        elif eventid in(audit_pass_btn_id,reaudit_btn_id):
            for row in self._selectedRows:
                trade_id = self.grid.GetCellValue(row,1)
                self.session.query(MergeTrade).filter_by(tid=trade_id)\
                    .update({'sys_status':SYS_STATUS_PREPARESEND})
            self.refreshTable()
            
        elif eventid == reverse_audit_btn2_id:
            reason = self.reverse_audit_text.GetValue()
            for row in self._selectedRows:
                trade_id = self.grid.GetCellValue(row,1)
                trade = self.session.query(MergeTrade).filter_by(tid=trade_id).first()
                trade.reverse_audit_times += 1
                trade.reverse_audit_reason += reason+','
                self.session.query(MergeTrade).filter_by(tid=trade_id)\
                    .update({'sys_status':SYS_STATUS_AUDITFAIL,
                             'reverse_audit_reason':trade.reverse_audit_reason,
                             'reverse_audit_times':trade.reverse_audit_times})
            self.refreshTable()
                    
        elif eventid == fill_sid_btn2_id:
            for row in self._selectedRows:
                trade_id = self.grid.GetCellValue(row,1)
                out_sid = self.grid.GetCellValue(row,13)
                
                trade = self.session.query(MergeTrade).filter_by(tid=trade_id).first()
                company_code = trade.logistics_company_code if trade else None
                company = self.session.query(LogisticsCompany).filter_by(code=company_code).first()
                company_regex = company.reg_mail_no if company else ''
                id_compile = re.compile(company_regex)
                if id_compile.match(out_sid):
                    self.session.query(MergeTrade).filter_by(tid=trade_id)\
                        .update({'out_sid':out_sid})

            self.refreshTable()
            self.fill_sid_btn2.Enable(False)
        elif eventid == picking_print_btn_id:
            trade_ids = []
            for row in self._selectedRows:
                trade_ids.append(self.grid.GetCellValue(row,1))
            DeliveryPrinter(parent=self,trade_ids=trade_ids).Show()
        
        elif eventid == express_print_btn_id:
            trade_ids = []
            for row in self._selectedRows:
                trade_ids.append(self.grid.GetCellValue(row,1))
            ExpressPrinter(parent=self,trade_ids=trade_ids).Show()
        
        elif eventid == prepare_finish_btn_id:
            for row in self._selectedRows:
                trade_id = self.grid.GetCellValue(row,1)
                self.session.query(MergeTrade).filter_by(tid=trade_id)\
                    .update({'sys_status':SYS_STATUS_SCANWEIGHT})
            self.refreshTable()
        
        elif eventid == scan_weight_btn_id:
            pass
        
        elif eventid == confirm_delivery_btn_id:
            for row in self._selectedRows:
                trade_id = self.grid.GetCellValue(row,1)
                self.session.query(MergeTrade).filter_by(tid=trade_id)\
                    .update({'sys_status':SYS_STATUS_CONFIRMSEND})
            self.refreshTable()
            
        elif eventid == invalid_btn2_id:
            invalid_reason = self.invalid_text.GetValue()
            for row in self._selectedRows:
                trade_id = self.grid.GetCellValue(row,1)
                trade = self.session.query(MergeTrade).filter_by(tid=trade_id).first()
                trade.reverse_audit_times += 1
                trade.reverse_audit_reason += invalid_reason+','
                self.session.query(MergeTrade).filter_by(tid=trade_id)\
                    .update({'sys_status':SYS_STATUS_INVALID,
                             'reverse_audit_reason':trade.reverse_audit_reason,
                             'reverse_audit_times':trade.reverse_audit_times})
            self.refreshTable()
        
        
        
    
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
        self.session.commit()  
        if self.page:
            self.page = self.paginator.page(self.page.number)
            object_list = self.parseObjectToList(self.page.object_list)
        else:
            object_list = ()
        gridtable = weakref.ref(GridTable(object_list, self.rowLabels, self.colLabels))
        self.grid.SetTable(gridtable())
        self.grid.SetColSize(0, 20)
        self.grid.SetRowLabelSize(40)  
        self.grid.ForceRefresh() 
    
    def updateTableAndPaginator(self):
        self._selectedRows.clear()
        if self.page:
            object_list = self.parseObjectToList(self.page.object_list)
        else:
            object_list = ()
           
        gridtable = weakref.ref(GridTable(object_list, self.rowLabels, self.colLabels))
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
        raise NotImplement("parseObjectToList-该方法没有实现") 
        
    
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
    
    def parseObjectToList(self, object_list):
        array_object = []
        for object in object_list:
            object_array = []
            object_array.append(object.tid)
            object_array.append(object.seller_nick)
            object_array.append(object.buyer_nick)
            object_array.append(TRADE_TYPE.get(object.type,'其他'))
            object_array.append(TRADE_STATUS.get(object.status,'其他'))
            object_array.append(SYS_STATUS.get(object.sys_status,'其他'))
            object_array.append(SHIPPING_TYPE.get(object.shipping_type,'其他'))
            object_array.append(object.has_refund)
            object_array.append(object.is_picking_print)
            object_array.append(object.is_express_print)
            object_array.append(object.is_send_sms)
            object_array.append(object.logistics_company_name)
            object_array.append(object.out_sid)
            object_array.append(object.payment)
            object_array.append(object.post_fee)
            object_array.append(object.total_fee)
            object_array.append(str(object.total_num))
            object_array.append(object.discount_fee)
            object_array.append(object.adjust_fee)
            object_array.append(object.pay_time)
            object_array.append(object.consign_time or '')
            object_array.append(object.reverse_audit_times)
            array_object.append(object_array)
        return array_object
    
    
class SimpleGridPanel(wx.Panel):
    def __init__(self, parent, id= -1, colLabels=None, rowLabels=None): 
        wx.Panel.__init__(self, parent, id) 
        
        self.session = parent.session
        self.rowLabels = rowLabels
        self.colLabels = colLabels
        self.grid =  grd.Grid(self, -1)
        self.setData(None)
        self.__set_properties()
        self.__do_layout()
        self.__evt_bind()
        
    def __set_properties(self):
        self.SetName('simple_grid_panel')
    
    def __do_layout(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.grid,-1,flag=wx.EXPAND)
        self.SetSizer(main_sizer)
        self.Layout()
        
    def __evt_bind(self):
        self.Bind(grd.EVT_GRID_CELL_CHANGE,self.cellContentChange,self.grid)
        
    def cellContentChange(self,evt):
        col = evt.Col
        if col == 6:
            row = evt.Row
            order_id = self.grid.GetCellValue(row,1)
            cell_value = self.grid.GetCellValue(row,col)
            
            if self.Parent.trade.type == 'fenxiao':
                self.session.query(SubPurchaseOrder).filter_by(fenxiao_id=order_id).update({'sku_properties':cell_value})
            else:
                self.session.query(Order).filter_by(oid=int(order_id)).update({'sku_properties_name':cell_value})
            self.Parent.Parent.is_changeable = False
            wx.CallAfter(self.grid.EnableEditing,False)
        evt.Skip()
        
    
    def setData(self,trade):
        object_list = self.parseObjectToList(trade)
        gridtable = weakref.ref(SimpleGridTable(object_list, self.rowLabels, self.colLabels))
        self.grid.SetTable(gridtable(),True)
        self.grid.AutoSize()
        self.grid.SetColSize(0,50)
        for i in range(0,len(object_list)):
            self.grid.SetRowSize(i,50)
        self.grid.ForceRefresh()
        if self.Parent.Parent.is_changeable:
            self.grid.EnableEditing(True)
        else:
            self.grid.EnableEditing(False)
        self.Layout()
    
    def parseObjectToList(self,trade):
        raise NotImplement("parseObjectToList-该方法没有实现")
        
 
class SimpleOrdersGridPanel(SimpleGridPanel):
     
    def parseObjectToList(self, trade):
        array_object = []
        if not trade :
            return array_object
        is_fenxiao = trade.type =='fenxiao'
        
        if is_fenxiao =='fenxiao':
            orders = self.session.query(SubPurchaseOrder).filter_by(id=trade.tid)
        else:
            orders = self.session.query(Order).filter_by(trade_id=trade.tid)
        
        from taobao.dao.models import Product
        array_object = [] 
        for object in orders:
            object_array = []
            object_array.append(object.snapshot_url if is_fenxiao else object.pic_path)
            object_array.append(object.fenxiao_id if is_fenxiao else str(object.oid))
            object_array.append(object.item_id if is_fenxiao else object.num_iid)
            object_array.append(object.title)
            
            product = self.session.query(Product).filter_by(outer_id=object.outer_id).first()
            object_array.append(product.name if product else '')
            
            object_array.append(object.sku_outer_id if is_fenxiao else object.outer_sku_id)
            object_array.append(object.sku_properties if is_fenxiao else object.sku_properties_name)
            object_array.append(object.num)
            object_array.append(object.price)
            object_array.append(object.buyer_payment if is_fenxiao else object.payment)
            
            if is_fenxiao:
                refund = self.session.query(Refund).filter_by(refund_id=object.refund_id).first()
            else:
                refund = self.session.query(Refund).filter_by(oid=object.oid).first()
            refund_id    = ('' if is_fenxiao else object.refund_id) if not refund else refund.refund_id
            refund_fee    = (object.refund_fee if is_fenxiao else '') if not refund else refund.refund_fee
            refund_status = ('' if is_fenxiao else object.refund_status) if not refund else refund.status
            refund_reason = refund.reason if refund else ''
            object_array.append(refund_id )
            object_array.append(refund_fee)
            object_array.append(REFUND_STATUS.get(refund_status,''))
            object_array.append(refund_reason)
            object_array.append(TRADE_STATUS.get(object.status,'其他'))

            array_object.append(object_array)
        return array_object
            
            
            
        