# -*- coding:utf8 -*-
'''
Created on 2012-7-13

@author: user1
'''
import re
import datetime
import weakref
import wx, wx.grid as grd
from collections import defaultdict
from taobao.dao import configparams as cfg
from taobao.frames.tables.gridtable import GridTable, SimpleGridTable, WeightGridTable, ChargeGridTable
from taobao.frames.panels.itempanel import ItemPanel
from taobao.frames.tables.gridtable import CheckGridTable
from taobao.frames.panels.searchpanel import SearchPanel
from taobao.common.paginator import Paginator
from taobao.exception.exception import NotImplement
from taobao.common.utils import create_session, TEMP_FILE_ROOT
from taobao.dao.models import PackageOrder, LogisticsCompany, PackageSkuItem
from taobao.dao.webapi import WebApi
from taobao.dao.tradedao import get_oparetor, get_datasource_by_type_and_mode, locking_trade
from taobao.frames.prints.deliveryprinter import DeliveryPrinter
from taobao.frames.prints.expressprinter import ExpressPrinter
from taobao.frames.prints.pickleprinter import PicklePrinter
from taobao.frames.prints.revieworder import OrderReview
from taobao.dao import yundao
from taobao.common.logger import log_exception
from taobao.common.utils import logtime
from taobao.common import barcode as barcodeutils

ZERO_REGEX = '^[0]+'
YUNDA_CODE = 'YUNDA'
RM_CODE = '_QR'

fill_sid_btn_id = wx.NewId()
invoice_print_btn_id = wx.NewId()
express_print_btn_id = wx.NewId()
scan_check_btn_id = wx.NewId()
scan_weight_btn_id = wx.NewId()
review_orders_btn_id = wx.NewId()
pickle_print_btn_id = wx.NewId()
tag_trade_btn2_id = wx.NewId()
fill_sid_btn2_id = wx.NewId()
fill_sid_btn4_id = wx.NewId()  # 核对单号按钮


class GridPanel(wx.Panel):
    def __init__(self, parent, id=-1, colLabels=None, rowLabels=None):
        wx.Panel.__init__(self, parent, id)

        self.Session = parent.Session
        self.datasource = None
        self.counter = None
        self.paginator = self.page = None
        self.page_size = 25
        self.rowLabels = rowLabels
        self.colLabels = colLabels
        self.status_type = ''
        self.start_sid = ''
        self.end_sid = ''
        self.curRow = None
        self._can_fresh = True
        self.grid = grd.Grid(self, -1)
        self._logisticMap = {}

        self._selectedRows = set()
        self.pag_panel = pag_panel = wx.Panel(self, -1)
        self.select_all_label = wx.StaticText(pag_panel, -1, u'  全  选')
        self.select_all_check = wx.CheckBox(pag_panel, -1)
        self.pt1 = wx.StaticText(pag_panel, -1, u",第")
        self.pt2 = wx.StaticText(pag_panel, -1, u"/")
        self.pt3 = wx.StaticText(pag_panel, -1, u"页(共")
        self.pt5 = wx.StaticText(pag_panel, -1, u" 条,已选")
        self.pt6 = wx.StaticText(pag_panel, -1, u" 条),每页")
        self.lblPageIndex = wx.StaticText(pag_panel, -1, "0")
        self.lblPageCount = wx.StaticText(pag_panel, -1, "0")
        self.lblTotalCount = wx.StaticText(pag_panel, -1, "0")
        self.selected_counts = wx.StaticText(pag_panel, -1, "0")
        self.page_size_select = wx.ComboBox(pag_panel, -1, choices=('25', '50', '100', '200'), value='25')
        self.btnFirst = wx.Button(pag_panel, -1, label=u'首页', style=0)
        self.btnLast = wx.Button(pag_panel, -1, label=u'尾页', style=0)
        self.btnPrev = wx.Button(pag_panel, -1, label=u'上一页', style=0)
        self.btnNext = wx.Button(pag_panel, -1, label=u'下一页', style=0)

        self.fill_sid_btn = wx.Button(pag_panel, fill_sid_btn_id, label=u'填物流单号', name=u'打印发货单前，需将物流单号与订单绑定')
        self.picking_print_btn = wx.Button(pag_panel, invoice_print_btn_id, label=u'打印发货单', name=u'打印发货单，进行配货')
        self.express_print_btn = wx.Button(pag_panel, express_print_btn_id, label=u'打印物流单', name=u'打印物流单，为打印配货单准备')
        self.post_print_btn = wx.Button(pag_panel, pickle_print_btn_id, label=u'打印配货单', name=u'打印配货单，为扫描验货准备')
        self.review_orders_btn = wx.Button(pag_panel, review_orders_btn_id, label=u'审查订单', name=u'审查指定订单问题并处理')
        self.scan_check_btn = wx.Button(pag_panel, scan_check_btn_id, label=u'扫描验货', name=u'扫描验货,为扫描称重准备')
        self.scan_weight_btn = wx.Button(pag_panel, scan_weight_btn_id, label=u'扫描称重', name=u'扫描称重，订单发货流程结束')

        self.button_array = []

        self.inner_panel = wx.Panel(self, -1)
        self.fill_sid_panel = wx.Panel(self.inner_panel, -1)
        self.fill_sid_label1 = wx.StaticText(self.fill_sid_panel, -1, u'起始物流单号')
        self.fill_sid_text = wx.TextCtrl(self.fill_sid_panel, -1, size=(200, -1))
        self.fill_sid_label2 = wx.StaticText(self.fill_sid_panel, -1, u'热敏打印')
        self.fill_sid_checkbox1 = wx.CheckBox(self.fill_sid_panel, -1)
        # self.receive_btn      = wx.Button(self.fill_sid_panel,-1,u'接单')
        self.preview_btn = wx.Button(self.fill_sid_panel, -1, u'预览')
        self.fill_sid_btn2 = wx.Button(self.fill_sid_panel, fill_sid_btn2_id, u'确定')

        self.out_sid_start_label = wx.StaticText(self.fill_sid_panel, -1, u'连打始单号')
        self.out_sid_start_text = wx.TextCtrl(self.fill_sid_panel, -1, size=(120, -1))
        self.out_sid_end_label = wx.StaticText(self.fill_sid_panel, -1, u'连打尾单号')
        self.out_sid_end_text = wx.TextCtrl(self.fill_sid_panel, -1, size=(120, -1))
        self.fill_sid_btn4 = wx.Button(self.fill_sid_panel, fill_sid_btn4_id, u'核对')
        self.fill_sid_btn3 = wx.Button(self.fill_sid_panel, -1, u'复原')

        self.static_button_down = wx.Button(self, -1, label='^------------^', size=(-1, 11))
        self.isSearchPanelShow = 1

        self.itempanel = ItemPanel(self, -1)
        self.searchpanel = SearchPanel(self,-1)
        self.updateTableAndPaginator()
        self.__set_properties()
        self.__do_layout()
        self.__bind_evt()

    def __set_properties(self):
        self.SetName('grid_panel')
        font = wx.Font(10, wx.SWISS, wx.SLANT, wx.BOLD, False)
        self.fill_sid_btn.SetFont(font)
        self.picking_print_btn.SetFont(font)
        self.express_print_btn.SetFont(font)
        self.post_print_btn.SetFont(font)
        self.review_orders_btn.SetFont(font)
        self.scan_check_btn.SetFont(font)
        self.scan_weight_btn.SetFont(font)

        self.fill_sid_checkbox1.SetValue(False)

        self.button_array.append(self.fill_sid_btn)
        self.button_array.append(self.picking_print_btn)
        self.button_array.append(self.express_print_btn)
        self.button_array.append(self.fill_sid_btn3)

        self.initialFillSidPanel()
        self.review_orders_btn.Enable(False)
        # 初始化物流ID与名称Map
        self._logisticMap = self.logisticMapping

    def __do_layout(self):
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        fg = wx.FlexGridSizer(hgap=2, vgap=2)
        fg.Add(self.select_all_label, 0, 0)
        fg.Add(self.select_all_check, 0, 0)
        fg.Add(self.pt1, 0, 0)
        fg.Add(self.lblPageIndex, 0, 1)
        fg.Add(self.pt2, 0, 2)
        fg.Add(self.lblPageCount, 0, 3)
        fg.Add(self.pt3, 0, 4)
        fg.Add(self.lblTotalCount, 0, 5)
        fg.Add(self.pt5, 0, 6)
        fg.Add(self.selected_counts, 0, 7)
        fg.Add(self.pt6, 0, 8)
        fg.Add(self.page_size_select, 0, 9)
        fg.Add(self.btnFirst, 0, 10)
        fg.Add(self.btnPrev, 0, 11)
        fg.Add(self.btnNext, 0, 12)
        fg.Add(self.btnLast, 0, 13)
        fg.Add((10, 10), 0, 14)

        fg.Add(self.fill_sid_btn, 0, 15)
        fg.Add(self.express_print_btn, 0, 16)
        fg.Add(self.picking_print_btn, 0, 17)
        fg.Add(self.post_print_btn, 0, 18)
        fg.Add(self.review_orders_btn, 0, 19)
        fg.Add(self.scan_check_btn, 0, 20)
        fg.Add(self.scan_weight_btn, 0, 21)
        self.pag_panel.SetSizer(fg)

        self.fill_sid_sizer = wx.FlexGridSizer(hgap=15, vgap=15)
        self.fill_sid_sizer.Add(self.fill_sid_label1, 0, 0)
        self.fill_sid_sizer.Add(self.fill_sid_text, 0, 1)
        self.fill_sid_sizer.Add(self.fill_sid_label2, 0, 2)
        self.fill_sid_sizer.Add(self.fill_sid_checkbox1, 0, 3)
        self.fill_sid_sizer.Add(self.preview_btn, 0, 4)
        self.fill_sid_sizer.Add(self.fill_sid_btn2, 0, 5)
        self.fill_sid_sizer.Add(self.out_sid_start_label, 0, 6)
        self.fill_sid_sizer.Add(self.out_sid_start_text, 0, 7)
        self.fill_sid_sizer.Add(self.out_sid_end_label, 0, 8)
        self.fill_sid_sizer.Add(self.out_sid_end_text, 0, 9)
        self.fill_sid_sizer.Add(self.fill_sid_btn4, 0, 10)
        self.fill_sid_sizer.Add(self.fill_sid_btn3, 0, 11)
        self.fill_sid_panel.SetSizer(self.fill_sid_sizer)

        self.inner_box_sizer = wx.BoxSizer(wx.VERTICAL)
        self.inner_box_sizer.Add(self.fill_sid_panel, proportion=0, flag=wx.EXPAND)
        self.inner_panel.SetSizer(self.inner_box_sizer)

        self.__set_sizer(6, 4)

    def __set_sizer(self, grid_propt=6, item_propt=4):
        self.main_sizer.Clear()
        self.main_sizer.Add(self.grid, grid_propt, wx.EXPAND)
        self.main_sizer.Add(self.pag_panel, flag=wx.RIGHT | wx.EXPAND)
        self.main_sizer.Add(wx.StaticLine(self, -1), flag=wx.EXPAND)
        self.main_sizer.Add(self.inner_panel, flag=wx.EXPAND)
        self.main_sizer.Add(self.static_button_down, flag=wx.RIGHT | wx.EXPAND)
        self.main_sizer.Add(self.itempanel, item_propt, flag=wx.RIGHT | wx.EXPAND)
        self.SetSizer(self.main_sizer)

    def __bind_evt(self):
        self.Bind(grd.EVT_GRID_CELL_LEFT_CLICK, self.onMouse, self.grid)
        self.Bind(grd.EVT_GRID_SELECT_CELL, self.onCellSelected, self.grid)
        self.Bind(grd.EVT_GRID_EDITOR_CREATED, self.onEditorCreated, self.grid)
        self.Bind(grd.EVT_GRID_CELL_RIGHT_CLICK, self.showPopupMenu, self.grid)

        self.Bind(wx.EVT_CHECKBOX, self.onClickQRPrint, self.fill_sid_checkbox1)
        self.Bind(wx.EVT_CHECKBOX, self.onSelectAllCheckbox, self.select_all_check)
        self.Bind(wx.EVT_COMBOBOX, self.onComboBox, self.page_size_select)

        self.Bind(wx.EVT_BUTTON, self.onBtnFirstClick, self.btnFirst)
        self.Bind(wx.EVT_BUTTON, self.onBtnLastClick, self.btnLast)
        self.Bind(wx.EVT_BUTTON, self.onBtnPrevClick, self.btnPrev)
        self.Bind(wx.EVT_BUTTON, self.onBtnNextClick, self.btnNext)

        self.Bind(wx.EVT_BUTTON, self.onChangeFlexSizer, self.fill_sid_btn)

        self.Bind(wx.EVT_BUTTON, self.onClickRollBackBtn, self.fill_sid_btn3)
        self.Bind(wx.EVT_BUTTON, self.onClickStaticButton, self.static_button_down)
        self.Bind(wx.EVT_BUTTON, self.fillOutSidToCell, self.preview_btn)

        # 分页栏，订单操作事件
        self.Bind(wx.EVT_BUTTON, self.onClickActiveButton, self.fill_sid_btn2)
        self.Bind(wx.EVT_BUTTON, self.onClickActiveButton, self.fill_sid_btn4)
        self.Bind(wx.EVT_BUTTON, self.onClickActiveButton, self.scan_weight_btn)
        self.Bind(wx.EVT_BUTTON, self.onClickActiveButton, self.picking_print_btn)
        self.Bind(wx.EVT_BUTTON, self.onClickActiveButton, self.express_print_btn)
        self.Bind(wx.EVT_BUTTON, self.onClickActiveButton, self.post_print_btn)
        self.Bind(wx.EVT_BUTTON, self.onClickActiveButton, self.review_orders_btn)
        self.Bind(wx.EVT_BUTTON, self.onClickActiveButton, self.scan_check_btn)
        self.Bind(wx.EVT_BUTTON, self.onClickActiveButton, self.scan_weight_btn)

    @property
    def logisticMapping(self):
        if self._logisticMap:
            return self._logisticMap

        lg_map = {}
        session = self.Session
        for lg in session.query(LogisticsCompany).all():
            lg_map[lg.id] = lg.name

        return lg_map

    @logtime(tag="setDataSource")
    def setDataSource(self, status_type):
        """设置数据源"""
        self.status_type = status_type
        print_mode = self.Parent.getPrintMode()
        session = self.Parent.Session

        self.datasource, self.counter = get_datasource_by_type_and_mode(status_type,
                                                                        print_mode=print_mode,
                                                                        session=session)
        self.paginator = paginator = Paginator(self.datasource, self.page_size, counter=self.counter)
        self.page = paginator.page(1)

        self.fill_sid_btn.Show(status_type in (cfg.PKG_WAIT_PREPARE_SEND_STATUS))
        self.picking_print_btn.Show(status_type in (cfg.PKG_WAIT_PREPARE_SEND_STATUS))
        self.express_print_btn.Show(status_type in (cfg.PKG_WAIT_PREPARE_SEND_STATUS))
        self.post_print_btn.Show(status_type in (cfg.PKG_WAIT_PREPARE_SEND_STATUS))
        self.review_orders_btn.Show(status_type in (cfg.PKG_WAIT_CHECK_BARCODE_STATUS,
                                                    cfg.PKG_WAIT_SCAN_WEIGHT_STATUS,
                                                    cfg.PKG_FINISHED_STATUS))
        self.scan_check_btn.Show(status_type in (cfg.PKG_WAIT_CHECK_BARCODE_STATUS))
        self.scan_weight_btn.Show(status_type in (cfg.PKG_WAIT_SCAN_WEIGHT_STATUS))
        # self.fill_sid_btn.Show(False)
        # self.picking_print_btn.Show(False)
        # self.express_print_btn.Show(False)
        # self.post_print_btn.Show(False)
        # self.review_orders_btn.Show(False)
        # self.scan_check_btn.Show(False)
        # self.scan_weight_btn.Show(False)
        self.updateTableAndPaginator()
        self.Layout()

    def initialFillSidPanel(self):
        self.preview_btn.Enable()
        self.fill_sid_btn2.Enable(False)
        self.fill_sid_btn4.Enable(False)

    def setSearchData(self, datasource, counter=None):
        self.paginator = paginator = Paginator(datasource, self.page_size, counter=counter)
        self.page = paginator.page(1)
        self.updateTableAndPaginator()

    ##################checkbox 在grid中的事件绑定 ###################
    def onMouse(self, evt):
        if evt.Col == 0:
            wx.CallLater(100, self.toggleCheckBox)
        evt.Skip()

    def toggleCheckBox(self):
        if hasattr(self.grid, 'cb'):
            self.grid.cb.Value = not self.grid.cb.Value
            self.afterCheckBox(self.grid.cb.Value)

    def onCellSelected(self, evt):
        if evt.Col == 0:
            wx.CallAfter(self.grid.EnableCellEditControl)
        evt.Skip()

    def onEditorCreated(self, evt):
        if evt.Col == 0:
            self.grid.cb = evt.Control
            self.grid.cb.WindowStyle |= wx.WANTS_CHARS
            self.grid.cb.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)
            self.grid.cb.Bind(wx.EVT_CHECKBOX, self.onCheckBox)
        evt.Skip()

    def onKeyDown(self, evt):
        if evt.KeyCode == wx.WXK_UP:
            if self.GridCursorRow > 0:
                self.grid.DisableCellEditControl()
                self.grid.MoveCursorUp(False)
        elif evt.KeyCode == wx.WXK_DOWN:
            if self.grid.GridCursorRow < (self.grid.NumberRows - 1):
                self.grid.DisableCellEditControl()
                self.grid.MoveCursorDown(False)
        elif evt.KeyCode == wx.WXK_LEFT:
            if self.grid.GridCursorCol > 0:
                self.grid.DisableCellEditControl()
                self.grid.MoveCursorLeft(False)
        elif evt.KeyCode == wx.WXK_RIGHT:
            if self.grid.GridCursorCol < (self.grid.NumberCols - 1):
                self.grid.DisableCellEditControl()
                self.grid.MoveCursorRight(False)
        else:
            evt.Skip()

    def onCheckBox(self, evt):
        self.afterCheckBox(evt.IsChecked())

    def afterCheckBox(self, isChecked, singleRecord=False):
        self.curRow = 0 if singleRecord else self.grid.GridCursorRow
        if isChecked:
            self._selectedRows.add(self.curRow)
            self.grid.SetCellValue(self.curRow, 0, '1')
        else:
            try:
                self._selectedRows.remove(self.curRow)
            except:
                pass
            self.grid.SetCellValue(self.curRow, 0, '')
        wx.CallLater(100, self.updateStatuAfterCheck)

    def updateStatuAfterCheck(self):

        value = self.grid.GetCellValue(self.curRow, 1)
        self.itempanel.setData(value)

        if len(self._selectedRows) < 1:
            for btn in self.button_array:
                btn.Enable(False)
        else:
            for btn in self.button_array:
                btn.Enable(True)

        self.updateSelectAllCheck()
        # self.grid.ForceRefresh()
        # self.refreshTable()

    #####################check 在grid中事件绑定结束#########################


    def showPopupMenu(self, evt):
        if not hasattr(self, "popupID1"):
            self.popupID1 = wx.NewId()
        menu = wx.Menu()
        item = wx.MenuItem(menu, self.popupID1, u'刷新')
        menu.AppendItem(item)
        self.grid.PopupMenu(menu)
        menu.Destroy()
        self.Bind(wx.EVT_MENU, self.onMenuRefreshTable)

    def onClickQRPrint(self, evt):

        self.fill_sid_text.Enable(not evt.IsChecked())
        evt.Skip()

    def onMenuRefreshTable(self, evt):
        eventid = evt.GetId()
        if eventid == self.popupID1:
            self.refreshTable()

    def onComboBox(self, evt):
        size = self.page_size_select.GetValue()
        if size.isdigit():
            self.page_size = int(size)
            self.paginator = paginator = Paginator(self.datasource, self.page_size, self.counter)
            self.page = paginator.page(1)
            self.updateTableAndPaginator()

    def onChangeFlexSizer(self, evt):
        eventid = evt.GetId()
        if not self.fill_sid_panel.IsShown() and eventid == fill_sid_btn_id:
            self.inner_panel.Show()
            self.fill_sid_panel.Show()
        else:
            self.inner_panel.Hide()
            self.fill_sid_panel.Hide()
        self.inner_panel.Layout()
        self.itempanel.Layout()
        self.Layout()

    def onClickRollBackBtn(self, evt):
        """ 复原所选数据打印状态  """

        dial = wx.MessageDialog(None, u'复原后订单打印信息会清空，顺序会重排，确定要复原吗？', u'复原订单确认',
                                wx.OK | wx.CANCEL | wx.ICON_EXCLAMATION)
        result = dial.ShowModal()
        dial.Destroy()

        if result == wx.ID_OK:
            operator = get_oparetor()
            trade_ids = set()
            for row in self._selectedRows:
                trade_ids.add(int(self.grid.GetCellValue(row, cfg.TRADE_ID_CELL_COL)))
            WebApi.revert_packages(trade_ids)
            self.initialFillSidPanel()
            self.refreshTable()

        evt.Skip()

    def onSelectAllCheckbox(self, evt):
        rows = self.grid.NumberRows
        if evt.IsChecked():
            for i in xrange(0, rows):
                self.grid.SetCellValue(i, 0, '1')
                self._selectedRows.add(i)
            for btn in self.button_array:
                btn.Enable(True)
        else:
            for i in xrange(0, rows):
                self.grid.SetCellValue(i, 0, '')
            self._selectedRows.clear()
            for btn in self.button_array:
                btn.Enable(False)

        self.grid.ForceRefresh()
        self.selected_counts.SetLabel(str(len(self._selectedRows)))

    def onClickStaticButton(self, evt):
        if self.isSearchPanelShow == 0:
            self.__set_sizer(6, 4)
            self.itempanel.Show()
            self.isSearchPanelShow = 1
            self.static_button_down.SetLabel('^------------^')
        elif self.isSearchPanelShow == 1:
            self.__set_sizer(1, 9)
            self.isSearchPanelShow = 2
            self.static_button_down.SetLabel('v------------v')
        else:
            self.__set_sizer(8, 2)
            self.isSearchPanelShow = 0
            self.static_button_down.SetLabel('^------------^')
            self.itempanel.Hide()
        self.Layout()

    def isCompanyConsistent(self):

        pre_company_id = ''
        for row in self._selectedRows:
            company_id = self.grid.GetCellValue(row, cfg.LOG_COMPANY_CELL_COL)

            if pre_company_id and pre_company_id != company_id:
                return False
            pre_company_id = company_id
        return True

    def get_yunda_ids(self, session=None):

        trade_ids = []

        selectedRows = sorted(list(self._selectedRows))
        trade_user_code = ''
        for row in selectedRows:

            trade_id = self.grid.GetCellValue(row, cfg.TRADE_ID_CELL_COL).strip()
            logistic_code = self.grid.GetCellValue(row, cfg.LOG_COMPANY_CELL_COL).strip().split('-')[1]
            if not (logistic_code.startswith(YUNDA_CODE) and logistic_code.endswith(RM_CODE)):
                dial = wx.MessageDialog(None, u'请选择韵达热敏', u'快递单号预览提示',
                                        wx.OK | wx.ICON_EXCLAMATION)
                dial.ShowModal()
                return
            trade_ids.append(trade_id)

        return trade_ids

    @log_exception
    def fillOutSidToCell(self, evt):
        if self._can_fresh:
            self.refreshTable()

        if not self.isCompanyConsistent():
            dial = wx.MessageDialog(None, u'请选择同一个快递的订单预览', u'订单预览提示',
                                    wx.OK | wx.ICON_EXCLAMATION)
            dial.ShowModal()
            return
        print "zuile"
        operator = get_oparetor()
        start_out_sid = self.fill_sid_text.GetValue()
        is_yunda_qrcode = self.fill_sid_checkbox1.IsChecked()
#########################################################################
        id_sid_map = {}
        sto_out_sid = {}
        lgts_name = self.Parent.search_panel.logistics_company_select.GetValue()
        exp_info = {u"申通快递":"STO", u"邮政小包":"POSTB"}
        if lgts_name in exp_info.keys() and is_yunda_qrcode:
            for row in self._selectedRows:
                trade_id = self.grid.GetCellValue(row, cfg.TRADE_ID_CELL_COL)
                company_id = self.grid.GetCellValue(row, cfg.LOG_COMPANY_CELL_COL)
                out_sid = self.grid.GetCellValue(row, cfg.OUT_SID_CELL_COL)
                pre_company_id = ''
                if pre_company_id and pre_company_id != company_id:
                    dial = wx.MessageDialog(None, u'请确保批打订单快递相同', u'快递单打印提示',
                                            wx.OK | wx.ICON_EXCLAMATION)
                    dial.ShowModal()
                    return
                pre_company_id = company_id
                if out_sid and operator:
                    id_sid_map[trade_id] = out_sid
                sto_out_sid[trade_id] = out_sid
            print sto_out_sid
            import STO_extra
            out_sids = []
            with create_session(self.Parent) as session:
                cp_code = exp_info[lgts_name]
                print u'物流编码',exp_info[lgts_name]
                result = STO_extra.get_detail_info_no_print(session,cp_code,*sto_out_sid.keys())
            WebApi.operate_packages(result.keys(), operator)
            for row in self._selectedRows:
                trade_id = self.grid.GetCellValue(row, cfg.TRADE_ID_CELL_COL)
                self.grid.SetCellValue(row, cfg.OUT_SID_CELL_COL, result[int(trade_id)])
            self.preview_btn.Enable(False)
            self.fill_sid_btn2.Enable(True)
            self._can_fresh = False
            self.fill_sid_text.Clear()
            self.grid.ForceRefresh()
            evt.Skip()
 #############################################################################               
        with create_session(self.Parent) as session:
            # 单号为数字，则默认单号递增
            exp_info = {}
            if not is_yunda_qrcode and start_out_sid.isdigit() and lgts_name not in exp_info.keys():
                self.start_sid = start_out_sid
                zero_head = ''
                zhregex = re.compile(ZERO_REGEX)
                zero_match = zhregex.match(start_out_sid)
                if zero_match:
                    zero_head = zero_match.group()

                company_regex = None
                start_out_sid = int(start_out_sid)
                incr_value = None
                trade_ids = []
                for row in self._selectedRows:
                    trade_id = self.grid.GetCellValue(row, cfg.TRADE_ID_CELL_COL)
                    if not company_regex or not incr_value:
                        package_order = session.query(PackageOrder).filter_by(pid=trade_id).first()
                        if not company_regex:
                            company_regex_no = package_order.logistics_company.reg_mail_no
                            company_regex = re.compile(company_regex_no)
                        if not incr_value:
                            if package_order.logistics_company.code == 'SF':
                                incr_value = 9
                            else:
                                incr_value =1
                    out_sid = zero_head + str(start_out_sid)
                    if not company_regex.match(out_sid):
                        dial = wx.MessageDialog(None, u'物流单号快递不符', u'快递单号预览提示',
                                                wx.OK | wx.ICON_EXCLAMATION)
                        dial.ShowModal()
                        self.fill_sid_text.Clear()
                        self.refreshTable()
                        return

                    self.grid.SetCellValue(row, cfg.OUT_SID_CELL_COL, out_sid)
                    start_out_sid += incr_value
                    trade_ids.append(int(trade_id))
                WebApi.operate_packages(trade_ids, operator)

                self.end_sid = str(start_out_sid - incr_value)

                self.preview_btn.Enable(False)
                self.fill_sid_btn2.Enable(True)
            # 如果单号非数字，则只填写一个单号，不递增
            elif not is_yunda_qrcode and start_out_sid:
                min_row_num = min(self._selectedRows)
                trade_id = self.grid.GetCellValue(min_row_num, cfg.TRADE_ID_CELL_COL)
                trade = session.query(PackageOrder).filter_by(pid=trade_id).first()
                company_regex = trade.logistics_company.reg_mail_no
                id_compile = re.compile(company_regex)
                if id_compile.match(str(start_out_sid)):
                    if locking_trade(trade.id, operator, session=session):
                        dial = wx.MessageDialog(None, u'订单已被其他用户锁定', u'订单预览提示',
                                                wx.OK | wx.ICON_EXCLAMATION)
                        dial.ShowModal()
                        self.fill_sid_text.Clear()
                        self.refreshTable()
                        evt.Skip()
                        return
                    self.grid.SetCellValue(min_row_num, cfg.OUT_SID_CELL_COL, start_out_sid)
                else:
                    dial = wx.MessageDialog(None, u'物流单号快递不符', u'快递单号预览提示',
                                            wx.OK | wx.ICON_EXCLAMATION)
                    dial.ShowModal()
                    self.fill_sid_text.Clear()
                    self.refreshTable()
                    evt.Skip()
                    return

                self.preview_btn.Enable(False)
                self.fill_sid_btn2.Enable(True)
            # 如果选择使用韵达二维码，则系统自动从韵达获取单号
            elif is_yunda_qrcode and lgts_name not in [u'申通快递',u'邮政小包']:
                print 'zuile3'
                # 对选中订单进行过滤
                yunda_ids = self.get_yunda_ids(session=session)
                if not yunda_ids:
                    return
                WebApi.operate_packages(yunda_ids, operator)
                try:
                    yd_customer = yundao.getYDCustomerByTradeId(yunda_ids[0],
                                                                session=session)
                    yundao.modify_order(yunda_ids,
                                        session=session,
                                        partner_id=yd_customer.qr_id,
                                        secret=yd_customer.qr_code)
                    # 创建韵达订单
                    yunda_online_ids = [i for i in yunda_ids]
                    im_map = yundao.create_order(yunda_online_ids,
                                                 session=session,
                                                 partner_id=yd_customer.qr_id,
                                                 secret=yd_customer.qr_code)
                    from taobao.dao.dbsession import SessionProvider
                    # 将运单号填入系统订单，并标记订单为二维码订单
                    for row in self._selectedRows:
                        trade_pid = self.grid.GetCellValue(row, cfg.TRADE_ID_CELL_COL)
                        package_order = SessionProvider.session.query(PackageOrder).filter_by(pid=trade_pid).one()
                        trade_id = package_order.id
                        if not im_map.has_key(trade_id):
                            continue
                        out_sid = im_map[trade_id]['mailno'].strip()
                        is_qrode = False #TODO
                        qr_msg = im_map[trade_id]['msg']
                        WebApi.express_order(trade_pid, out_sid, is_qrode, qr_msg)
                        if im_map[trade_id]['status']:
                            self.grid.SetCellValue(row, cfg.OUT_SID_CELL_COL, out_sid)
                        else:
                            self.grid.SetCellValue(row, cfg.QR_MSG_CELL_COL, qr_msg)

                except Exception, exc:
                    dial = wx.MessageDialog(None, u'预览错误：' + exc.message, u'快递单号预览提示',
                                            wx.OK | wx.ICON_EXCLAMATION)
                    dial.ShowModal()
                    raise exc
                else:
                    self.preview_btn.Enable(False)
                    self.fill_sid_btn2.Enable(True)
        self._can_fresh = False
        self.fill_sid_text.Clear()
        self.grid.ForceRefresh()
        evt.Skip()

    @log_exception
    def receiveYundaOrder(self, evt):

        is_yunda_qrcode = self.fill_sid_checkbox1.IsChecked()
        if not is_yunda_qrcode:
            return

        with create_session(self.Parent) as session:
            # 对选中订单进行过滤
            yunda_ids = self.get_yunda_ids()
            if not yunda_ids:
                return
            try:
                pass
            except Exception, exc:
                dial = wx.MessageDialog(None, u'接单错误：' + exc.message, u'快递单号预览提示',
                                        wx.OK | wx.ICON_EXCLAMATION)
                dial.ShowModal()
                raise exc

        self.preview_btn.Enable()
        self._can_fresh = True

        evt.Skip()

    def disablePicklePrintBtn(self):
        """ 将打印配货单按钮设无效 """
        self.post_print_btn.Enable(False)

    def enablePicklePrintBtn(self):
        """ 将打印配货单按钮设有效 """
        self.post_print_btn.Enable(True)

    @log_exception
    def onClickActiveButton(self, evt):
        print "zuile4"
        eventid = evt.GetId()
        operator = get_oparetor()
        with create_session(self.Parent) as session:
            if eventid == fill_sid_btn2_id:
                effect_row = 0
                is_yunda_qrcode = self.fill_sid_checkbox1.IsChecked()

                for row in self._selectedRows:
                    try:
                        trade_id = self.grid.GetCellValue(row, cfg.TRADE_ID_CELL_COL)
                        out_sid = self.grid.GetCellValue(row, cfg.OUT_SID_CELL_COL)
                        WebApi.express_order(trade_id, out_sid, False, '')
                        self.grid.SetCellValue(row, cfg.OUT_SID_CELL_COL, out_sid)
                        self.grid.SetCellValue(row, cfg.OPERATOR_CELL_COL, operator)
                        effect_row += 1
                    except Exception, exc:
                        dial = wx.MessageDialog(None, u'单号填充错误:' + exc.message, u'快递单打印提示',
                                                wx.OK | wx.ICON_EXCLAMATION)
                        dial.ShowModal()
                        break

                if effect_row > 1 and not is_yunda_qrcode:
                    self.disablePicklePrintBtn()
                    self.fill_sid_btn4.Enable(True)

                self.fill_sid_btn2.Enable(False)
                self.preview_btn.Enable(is_yunda_qrcode or effect_row == 1)
                self._can_fresh = True

            elif eventid == fill_sid_btn4_id:
                start_out_sid = self.out_sid_start_text.GetValue()
                end_out_sid = self.out_sid_end_text.GetValue()

                if self.start_sid == start_out_sid and self.end_sid == end_out_sid:
                    self.enablePicklePrintBtn()
                    self.out_sid_start_text.Clear()
                    self.out_sid_end_text.Clear()
                    self.fill_sid_btn4.Enable(False)
                    self.preview_btn.Enable(True)
                else:
                    dial = wx.MessageDialog(None, u'输入的起始单号与所填单号不符', u'快递单打印提示',
                                            wx.OK | wx.ICON_EXCLAMATION)
                    dial.ShowModal()
            elif eventid == invoice_print_btn_id:
                trade_ids = []
                for row in self._selectedRows:
                    trade_id = self.grid.GetCellValue(row, cfg.TRADE_ID_CELL_COL)
                    out_sid = self.grid.GetCellValue(row, cfg.OUT_SID_CELL_COL).strip()
                    toperator = self.grid.GetCellValue(row, cfg.OPERATOR_CELL_COL).strip()

                    if out_sid and toperator:
                        trade_ids.append(trade_id)

                if not trade_ids:
                    dial = wx.MessageDialog(None, u'请选择正确的订单项', u'发货单打印提示',
                                            wx.OK | wx.ICON_EXCLAMATION)
                    dial.ShowModal()
                    return
                WebApi.print_picking(trade_ids)
                DeliveryPrinter(parent=self, trade_ids=trade_ids) \
                    .ShowFullScreen(True, style=wx.FULLSCREEN_NOBORDER)

            elif eventid == express_print_btn_id:
                lgts_name = self.Parent.search_panel.logistics_company_select.GetValue()
                print lgts_name
                print self.fill_sid_checkbox1.IsChecked()
                id_sid_map = {}
                sto_out_sid = dict()
                pre_company_id = ''
                is_yunda_qrcode = self.fill_sid_checkbox1.IsChecked()
                trade_ids = []
                for row in self._selectedRows:
                    trade_id = self.grid.GetCellValue(row, cfg.TRADE_ID_CELL_COL)
                    trade_ids.append(trade_id)
                    company_id = self.grid.GetCellValue(row, cfg.LOG_COMPANY_CELL_COL)
                    out_sid = self.grid.GetCellValue(row, cfg.OUT_SID_CELL_COL)

                    if pre_company_id and pre_company_id != company_id:
                        dial = wx.MessageDialog(None, u'请确保批打订单快递相同', u'快递单打印提示',
                                                wx.OK | wx.ICON_EXCLAMATION)
                        dial.ShowModal()
                        return
                    pre_company_id = company_id
                    if out_sid and operator:
                        id_sid_map[trade_id] = out_sid
                    sto_out_sid[trade_id] = out_sid
                print sto_out_sid
                import STO_extra
                exp_info = {u"申通快递":"STO", u"邮政小包":"POSTB"}
                if lgts_name in exp_info.keys() and is_yunda_qrcode and sto_out_sid:
                    cp_code = exp_info[lgts_name]
                    print cp_code
                    with create_session(self.Parent) as session:
                        result = STO_extra.get_detail_info(session,cp_code,*sto_out_sid.keys())
                        print result
                        if result == "success":
                            self.refreshTable()
                            print "success"
                            dial = wx.MessageDialog(None, u'生成打印预览文件成功了', u'预览打印提示', 
                            wx.OK | wx.ICON_EXCLAMATION)
                            dial.ShowModal()
                        elif result == "printer error":
                            dial = wx.MessageDialog(None, u'', u'无法生成预览文件', 
                            wx.OK | wx.ICON_EXCLAMATION)
                            dial.ShowModal()
                        elif result["error_code"] == 41:
                            logger.warn({"error_code":result["error_code"]})
                            print {"error_code":result["error_code"]}
                            result = result['detail']
                            addr_info = '省:%s,市:%s,区:%s,详细地址:%s,姓名:%s，手机号:%s,订单号:%s'
                            print {"province":result['province']}
                            error_addr_info = (result['province'],result['city'],result['district'],result['detail'],\
                                               result['name'],\
                                               result['mobile'],result['trade_id'])
                            addr_info = addr_info % error_addr_info
                            addr_info = addr_info + u'    =>   此地址有出入，导致无法申请到运单号'
#                           error_addr_info = "你好".encode("GBK")
                            dial = wx.MessageDialog(None, addr_info, u'生成错误', 
                            wx.OK | wx.ICON_EXCLAMATION)
                            dial.ShowModal()
                            return 
                        else:
                            print 'cuole'
                            print result
                            dial = wx.MessageDialog(None, u'无法生成预览文件', u'生成错误', 
                            wx.OK | wx.ICON_EXCLAMATION)
                            dial.ShowModal()
                if id_sid_map and not is_yunda_qrcode:
                    ExpressPrinter(parent=self, trade_ids=id_sid_map.keys()).ShowFullScreen(True,
                                                                                            style=wx.FULLSCREEN_NOBORDER)

                elif id_sid_map and is_yunda_qrcode:
                    sort_list = sorted(id_sid_map.items(), key=lambda d: d[1], reverse=False)
                    sort_ids = [d[0] for d in sort_list]
                    trades = session.query(PackageOrder).filter(PackageOrder.pid.in_(sort_ids)).filter_by(
                        is_express_print=True)
                    rept_num = trades.count()
                    if rept_num > 0:
                        dial = wx.MessageDialog(None, u'该批订单有（%d）单已打印快递单，还要继续吗？' % rept_num, u'快递单重打提示',
                                                wx.OK | wx.CANCEL | wx.ICON_EXCLAMATION)
                        result = dial.ShowModal()
                        dial.Destroy()
                        # 如果不继续，则退出
                        if result != wx.ID_OK:
                            return
                            # 调用韵达本地服务打印
                    # yundao.printYUNDAService(sort_ids,session=session)
                    # 调用韵达打印接口并打印
                    try:
                        yundao.printYUNDAPDF(sort_ids, session=session)
                    except WindowsError:
                        dial = wx.MessageDialog(None, u'请关闭上批快单打印PDF文件', u'快递单重打提示',
                                                wx.OK | wx.CANCEL | wx.ICON_EXCLAMATION)
                        result = dial.ShowModal()
                        dial.Destroy()


            elif eventid == pickle_print_btn_id:
                PicklePrinter(parent=self).ShowFullScreen(True, style=wx.FULLSCREEN_ALL)  # .Show()

            elif eventid == review_orders_btn_id:
                if len(self._selectedRows) == 1:
                    trade_id = self.grid.GetCellValue(list(self._selectedRows)[0], cfg.TRADE_ID_CELL_COL)
                    OrderReview(parent=self, trade_id=trade_id).ShowFullScreen(True, style=wx.FULLSCREEN_ALL)  # .Show()

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
        # 修改状态后 ，刷新当前表单

        trade_ids = self.getSelectTradeIds(self._selectedRows)
        if self.page:
            self.page = self.paginator.page(self.page.number)
            object_list = self.parseObjectToList(self.page.object_list)
        else:
            object_list = ()

        print_mode = self.Parent.getPrintMode()
        if not object_list and self.status_type == cfg.SYS_STATUS_PREPARESEND and print_mode == cfg.DIVIDE_MODE:
            self.setDataSource(self.status_type)
            return
        gridtable = weakref.ref(GridTable(object_list, self.rowLabels, self.colLabels, self.Parent.selectedRowColour))
        self.grid.SetTable(gridtable())
        self.grid.SetColSize(0, 20)
        self.grid.SetColSize(cfg.LOCKED_CELL_COL, 35)
        self.grid.SetColSize(cfg.EXPRESS_CELL_COL, 50)
        self.grid.SetColSize(cfg.PICKLE_CELL_COL, 50)
        self.grid.SetColSize(cfg.REVIEW_CELL_COL, 35)
        self.grid.SetColSize(cfg.OUT_SID_CELL_COL, 120)
        self.grid.SetRowLabelSize(40)
        self.updateCellBySelectedTradeIds(trade_ids)
        self.updateSelectAllCheck()
        self.grid.ForceRefresh()

    def updateCellBySelectedTradeIds(self, trade_ids):
        self._selectedRows.clear()
        rows = self.grid.GetNumberRows()
        for row in xrange(0, rows):
            trade_id = self.grid.GetCellValue(row, cfg.TRADE_ID_CELL_COL)
            if trade_id in trade_ids:
                self._selectedRows.add(row)
                self.grid.SetCellValue(row, 0, '1')

    def getSelectTradeIds(self, selectRows):
        trade_ids = []
        for row in selectRows:
            trade_id = self.grid.GetCellValue(int(row), cfg.TRADE_ID_CELL_COL)
            trade_ids.append(trade_id)
        return trade_ids

    def updateSelectAllCheck(self):

        self.review_orders_btn.Enable(len(self._selectedRows) == 1)
        self.selected_counts.SetLabel(str(len(self._selectedRows)))
        self.setupPager()
        row = self.grid.GetNumberRows()
        if row > 0 and row == len(self._selectedRows):
            self.select_all_check.SetValue(True)
        else:
            self.select_all_check.SetValue(False)

    def updateTableAndPaginator(self):
        self._selectedRows.clear()
        if self.page:
            object_list = self.parseObjectToList(self.page.object_list)
        else:
            object_list = ()

        gridtable = weakref.ref(GridTable(object_list, self.rowLabels, self.colLabels, self.Parent.selectedRowColour))
        self.grid.SetTable(gridtable())
        self.grid.SetColSize(0, 20)
        self.grid.SetColSize(cfg.LOCKED_CELL_COL, 35)
        self.grid.SetColSize(cfg.EXPRESS_CELL_COL, 50)
        self.grid.SetColSize(cfg.PICKLE_CELL_COL, 50)
        self.grid.SetColSize(cfg.REVIEW_CELL_COL, 35)
        self.grid.SetColSize(cfg.OUT_SID_CELL_COL, 120)
        self.grid.SetRowLabelSize(40)
        for btn in self.button_array:
            btn.Enable(False)

        if len(object_list) == 1:
            self.grid.SetCellValue(0, 0, '1')
            self.afterCheckBox(True, singleRecord=True)

        self.updateSelectAllCheck()

        self.inner_panel.Hide()
        self.fill_sid_panel.Hide()
        self.inner_panel.Layout()
        self.pag_panel.Layout()
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

    def enableAutoIncrSidBtn(self, is_enable):
        self.fill_sid_checkbox1.Enable(is_enable)
        self.fill_sid_checkbox1.SetValue(is_enable)


class ListArrayGridPanel(GridPanel):
    def parseObjectToList(self, object_list):
        return object_list


class QueryObjectGridPanel(GridPanel):
    def parseObjectToList(self, object_list):
        array_object = []
        #        session      = self.Session
        for order in object_list:
            # session.expire(order)

            object_array = []
            object_array.append(order.pid)
            object_array.append(order.seller.nick)
            object_array.append(order.buyer_nick)
            object_array.append(cfg.TRADE_TYPE.get('sale', u'其他'))
            # object_array.append('sale')
            object_array.append(cfg.TRADE_STATUS.get(order.status, u'其他'))
            object_array.append(cfg.PACKAGE_STATUS_DICT.get(order.sys_status, u'其他'))
            object_array.append(order.receiver_state + '-' + order.receiver_city + '-' + order.receiver_district)
            object_array.append(order.is_locked)
            object_array.append(order.is_express_print)
            object_array.append(order.is_picking_print)
            object_array.append(order.can_review)
            object_array.append(u'%s-%s' % (order.logistics_company and order.logistics_company.name or u'其它',
                                            order.logistics_company and order.logistics_company.code or u'NONE'))
            object_array.append(order.out_sid)
            object_array.append(order.out_sid and order.operator or '')
            object_array.append(order.qrcode_msg)
            object_array.append(str(order.prod_num))
            object_array.append(order.payment)
            object_array.append(order.total_fee)
            object_array.append(order.scanner)
            object_array.append(order.pay_time)
            object_array.append(order.consign_time or '')
            object_array.append(order.weight_time or '')
            array_object.append(object_array)
        return array_object


class SimpleGridPanel(wx.Panel):
    def __init__(self, parent, id=-1, colLabels=None, rowLabels=None):
        wx.Panel.__init__(self, parent, id)

        if hasattr(parent, 'Session'):
            self.Session = parent.Session

        self.rowLabels = rowLabels
        self.colLabels = colLabels
        self.grid = grd.Grid(self, -1)
        self.setData(None)
        self.grid.SetMinSize((1100, 600))
        self.__set_properties()
        self.__do_layout()

    def __set_properties(self):
        self.SetName('simple_grid_panel')

    def __do_layout(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.grid, -1, flag=wx.EXPAND)
        self.SetSizer(main_sizer)
        self.Layout()

    def setData(self, trade, grid_table_type=SimpleGridTable):
        object_list = self.parseObjectToList(trade)
        print 'debug detial list:', object_list
        gridtable = weakref.ref(grid_table_type(object_list,
                                                self.rowLabels,
                                                self.colLabels))
        self.grid.SetTable(gridtable(), True)
        self.grid.AutoSize()
        self.grid.SetColSize(0, 80)
        for i in range(0, len(object_list)):
            self.grid.SetRowSize(i, 60)
        self.grid.DisableCellEditControl()
        self.grid.ForceRefresh()
        self.Layout()

    def parseObjectToList(self, trade):
        raise NotImplement(u"parseObjectToList-该方法没有实现")


class SimpleOrdersGridPanel(SimpleGridPanel):
    def parseObjectToList(self, trade):
        array_object = []
        if not trade:
            return array_object

        with create_session(self.Parent) as session:
            # datasource.filter(PackageOrder.seller_id.in_(seller_ids))
            orders = session.query(PackageSkuItem).filter(PackageSkuItem.package_order_id==trade.id,
                                                          PackageSkuItem.sys_status==cfg.IN_EFFECT)
            array_object = []
            for order in orders:
                object_array = []
                # object_array.append(order.pic_path)
                object_array.append(u'图片地址')
                object_array.append(order.get_type_display())
                object_array.append(order.id)
                object_array.append(order.outer_id or order.num_iid)
                object_array.append(order.title)
                object_array.append(order.outer_sku_id)
                object_array.append(order.sku_properties_name)
                object_array.append(order.num)
                object_array.append(order.price)
                object_array.append(order.payment)
                object_array.append(order.refund_id)
                object_array.append(cfg.REFUND_STATUS.get(order.refund_status, ''))
                object_array.append(cfg.ORDER_TYPE.get(order.gift_type, u'其他'))
                #object_array.append(cfg.TRADE_STATUS.get(order.status, u'其他'))
                object_array.append(cfg.ASSIGN_STATUS.get(order.assign_status, u'其他'))
                object_array.append(cfg.SYS_ORDERS_STATUS.get(order.sys_status, u'其他'))
                array_object.append(object_array)
        print 'order detail:', array_object
        return array_object


class WeightGridPanel(wx.Panel):
    def __init__(self, parent, id=-1):
        wx.Panel.__init__(self, parent, id)

        self.grid = grd.Grid(self, -1)
        colLabels = (u'内部单号', u'店铺简称', u'会员名称', u'系统状态', u'快递公司', u'运单号', u'称重重量',
                     u'收货人', u'所在省', u'所在市', u'所在地区', u'收货地址', u'收货人手机')
        gridtable = weakref.ref(WeightGridTable(colLabels=colLabels))
        self.grid.SetTable(gridtable(), True)
        self.grid.SetColLabelSize(40)

        box_sizer = wx.BoxSizer(wx.HORIZONTAL)
        box_sizer.Add(self.grid, flag=wx.EXPAND)

        self.grid.SetMinSize((1200, 600))
        self.grid.SetColSize(5, 120)
        self.SetSizer(box_sizer)
        self.Layout()

    def InsertTradeRows(self, trade):
        items = self.getTradeItems(trade)
        for index, item in enumerate(items):
            self.grid.SetCellValue(0, index, item)

        self.grid.InsertRows(0, 1, True)
        self.grid.SetRowSize(0, 40)
        self.grid.ProcessTableMessage(grd.GridTableMessage(
            self.grid.Table, grd.GRIDTABLE_NOTIFY_ROWS_INSERTED, 0, 1))

        self.grid.ForceRefresh()

    def getTradeItems(self, trade):
        items = []
        items.append(str(trade['trade_id']))
        items.append(trade['seller_nick'])
        items.append(trade['buyer_nick'])
        items.append(trade['sys_status'])
        items.append(trade['company_name'])
        items.append(trade['package_no'])
        items.append(trade['weight'])
        items.append(trade['receiver_name'])
        items.append(trade['receiver_state'])
        items.append(trade['receiver_city'])
        items.append(trade['receiver_district'])
        items.append(trade['receiver_address'])
        items.append(trade['receiver_mobile'])

        return items


class ChargeGridPanel(wx.Panel):
    def __init__(self, parent, id=-1, datasource=()):
        wx.Panel.__init__(self, parent, id)

        self.grid = grd.Grid(self, -1)
        self.colLabels = (u'快递单号', u'重量(kg)', u'省', u'市', u'区', u'邮编')
        gridtable = weakref.ref(ChargeGridTable(datasource=datasource, colLabels=self.colLabels))
        self.grid.SetTable(gridtable(), True)
        self.grid.SetRowLabelSize(40)

        box_sizer = wx.BoxSizer(wx.HORIZONTAL)
        box_sizer.Add(self.grid, flag=wx.EXPAND)

        self.grid.SetMinSize((1300, 500))
        self.SetSizer(box_sizer)
        self.Layout()

    def InsertChargeRows(self, trade):

        self.grid.ProcessTableMessage(grd.GridTableMessage(
            self.grid.Table, grd.GRIDTABLE_NOTIFY_ROWS_INSERTED, 0, 1))

        items = self.getItem(trade)
        self.grid.InsertRows(0, 1, True)
        for index, item in enumerate(items):
            self.grid.SetCellValue(0, index, item)

        self.grid.ForceRefresh()

    def getItem(self, trade):
        items = []
        items.append(trade.out_sid)
        items.append(self.formatWeight(trade.weight))
        items.append(trade.receiver_state)
        items.append(trade.receiver_city)
        items.append(trade.receiver_district)
        items.append(trade.receiver_zip)
        return items

    def formatWeight(self, weight):
        if not weight:
            return '0'
        v = float(weight)
        if weight.isdigit():
            v = v / 1000

        if v < 1.3:
            return '1.0'
        return '%.2g' % v

    def getItems(self, trades):

        trade_list = []
        for trade in trades:
            t = self.getItem(trade)
            trade_list.append(t)

        return trade_list

    def setData(self, datasource):
        source = self.getItems(datasource)
        gridtable = weakref.ref(ChargeGridTable(source, colLabels=self.colLabels))
        self.grid.SetTable(gridtable())
        self.grid.SetColSize(0, 120)
        self.grid.ForceRefresh()


class CheckOrdersGridPanel(SimpleGridPanel):
    """商品检验部分的panel """

    def parseObjectToList(self, trade):
        array_object = []
        if not trade:
            return array_object

        array_object = []
        for order in trade['order_items']:
            object_array = []

            object_array.append(order['pic_path'])
            object_array.append(str(order['order_id']))
            object_array.append('')

            object_array.append(order['title'])
            object_array.append(order['num'])
            object_array.append(order['outer_id'])
            object_array.append(order['outer_sku_id'])
            object_array.append(order['sku_properties_name'])
            object_array.append(order['sku_name'])
            object_array.append(order['post_check'] and 'Y' or 'N')
            object_array.append(order['status'])
            object_array.append(order['barcode'])
            object_array.append(0)

            array_object.append(object_array)

        return array_object


class CheckGridPanel(wx.Panel):
    def __init__(self, parent, id=-1):
        wx.Panel.__init__(self, parent, id)

        self.trade = None
        self.code_num_dict = {}

        colLabels = (u'商品图片', u'子订单ID', u'商品ID', u'商品简称', u'订购数量', u'商品编码', u'规格编码', u'订单属性',
                     u'商品属性', u'需验单', u'订单状态', u'商品条码', u'扫描次数')
        self.ordergridpanel = CheckOrdersGridPanel(self, colLabels=colLabels)

        self.__set_properties()
        self.__do_layout()

    def __set_properties(self):
        self.SetName('detail_panel')

    def __do_layout(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.ordergridpanel, -1, wx.EXPAND)
        self.Layout()
        self.SetSizer(main_sizer)

    def getOrderCodeMapNumDict(self, trade):
        from taobao.dao.dbsession import SessionProvider
        code_num_dict = {}
        for order in trade['order_items']:
            barcode = order['barcode']
            post_check = order['post_check']
            order_num = order['num']
            if code_num_dict.has_key(barcode):
                code_num_dict[barcode]['rnums'] += order_num
            else:
                code_num_dict[barcode] = {'rnums': order_num,
                                          'cnums': 0,
                                          'sku_id': order['sku_id'],
                                          'batch_nos': defaultdict(dict),
                                          'post_check': post_check}

        return code_num_dict

    def isCheckOver(self):
        for key, value in self.code_num_dict.items():
            if value['rnums'] != value['cnums']:
                return False
        return True

    def setBarCode(self, barcode):
        if barcode.lower() == 'pass':
            for key, value in self.code_num_dict.items():
                value['cnums'] = value['rnums']
            return True

        barcode, batch_no = barcodeutils.decode(barcode)
        if self.code_num_dict.has_key(barcode):
            grid = self.ordergridpanel.grid
            record = self.code_num_dict[barcode]
            cnum = record['cnums'] = record['cnums'] + 1
            record['batch_nos'][batch_no] = record['batch_nos'].get(batch_no, 0) + 1

            for row in xrange(0, grid.NumberRows):
                code = grid.GetCellValue(row, cfg.BAR_CODE_COL)

                if barcode != code:
                    continue

                gcnum = int(grid.GetCellValue(row, cfg.ORIGIN_NUM_COL))
                fcnum = int(grid.GetCellValue(row, cfg.NUM_STATUS_COL))

                if fcnum >= gcnum:
                    cnum = cnum - fcnum
                    continue

                if cnum <= gcnum:
                    grid.SetCellValue(row, cfg.NUM_STATUS_COL, str(cnum))
                    cnum = 0
                    break

            grid.ForceRefresh()
            if cnum == 0:
                return True
        return False

    def serial_data(self):
        data = {}
        for key, value in self.code_num_dict.items():
            data[value['sku_id']] = value['batch_nos']
        return data

    def setData(self, trade, grid_table_type=CheckGridTable):
        if not trade:
            return
        self.trade = trade
        # self.trade =
        self.ordergridpanel.setData(trade, grid_table_type=CheckGridTable)
        self.code_num_dict = self.getOrderCodeMapNumDict(trade)
        self.ordergridpanel.Layout()

    def clearTable(self):
        """ 清除表格  """
        self.trade = None
        self.ordergridpanel.setData(None)
        self.code_num_dict = {}
        self.ordergridpanel.Layout()

