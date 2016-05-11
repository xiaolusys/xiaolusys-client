# -*- coding:utf8 -*-
'''
Created on 2012-7-27

@author: user1
'''
import re
import winsound
import wx, wx.grid
from taobao.common.utils import create_session, MEDIA_ROOT
from taobao.frames.panels.gridpanel import WeightGridPanel
from taobao.common.utils import getconfig
from taobao.dao.webapi import WebApi
from taobao.dao import configparams as cfg

weight_regex = re.compile('[0-9\.]{1,7}$')


class ScanWeightPanel(wx.Panel):
    def __init__(self, parent, id=-1):
        wx.Panel.__init__(self, parent, id)

        self.trade = None
        self.valid_code = ''
        self.out_sid_label = wx.StaticText(self, -1, u'快递单号')
        self.out_sid_text = wx.TextCtrl(self, -1, size=(200, -1), style=wx.TE_PROCESS_ENTER)
        self.weight_label = wx.StaticText(self, -1, u'称重重量(g)')
        self.weight_text = wx.TextCtrl(self, -1, size=(200, -1), style=wx.TE_PROCESS_ENTER)

        self.cancel_button = wx.Button(self, -1, u'清除')

        self.error_text = wx.StaticText(self, -1)

        self.order_label1 = wx.StaticText(self, -1, u'店铺简称')
        self.order_content1 = wx.TextCtrl(self, -1)
        self.order_label3 = wx.StaticText(self, -1, u'订单类型')
        self.order_content3 = wx.TextCtrl(self, -1)
        self.order_label4 = wx.StaticText(self, -1, u'会员名称')
        self.order_content4 = wx.TextCtrl(self, -1)
        self.order_label5 = wx.StaticText(self, -1, u'快递公司')
        self.order_content5 = wx.TextCtrl(self, -1)
        self.order_label6 = wx.StaticText(self, -1, u'收货人')
        self.order_content6 = wx.TextCtrl(self, -1, size=(130, -1))
        self.order_label7 = wx.StaticText(self, -1, u'收货地址')
        self.order_content7 = wx.TextCtrl(self, -1, size=(300, -1))

        self.order_box1 = wx.StaticBox(self, -1, u'扫描订单详细信息')

        self.gridpanel = WeightGridPanel(self, -1)

        self.order_box2 = wx.StaticBox(self, -1, u'已称重订单列表')

        self.__set_properties()
        self.__do_layout()
        self.__evt_bind()

    def __set_properties(self):
        self.SetName('weight panel')

        self.control_array = []
        self.control_array.append(self.order_content1)
        self.control_array.append(self.order_content3)
        self.control_array.append(self.order_content4)
        self.control_array.append(self.order_content5)
        self.control_array.append(self.order_content6)
        self.control_array.append(self.order_content7)

        self.out_sid_text.SetFocus()

    def __do_layout(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        flex_sizer1 = wx.FlexGridSizer(hgap=5, vgap=5)
        flex_sizer1.Add((100, 10), 0, 1)
        flex_sizer1.Add(self.out_sid_label, 0, 2)
        flex_sizer1.Add(self.out_sid_text, 0, 3)
        flex_sizer1.Add(self.weight_label, 0, 4)
        flex_sizer1.Add(self.weight_text, 0, 5)

        flex_sizer1.Add(self.cancel_button, 0, 11)
        flex_sizer1.Add(self.error_text, 0, 12)

        sbsizer1 = wx.StaticBoxSizer(self.order_box1, wx.VERTICAL)
        bag_sizer1 = wx.GridBagSizer(hgap=5, vgap=5)
        bag_sizer1.Add(self.order_label1, pos=(0, 0), span=(1, 1), flag=wx.EXPAND)
        bag_sizer1.Add(self.order_content1, pos=(0, 1), span=(1, 1), flag=wx.EXPAND)
        bag_sizer1.Add(self.order_label3, pos=(0, 2), span=(1, 1), flag=wx.EXPAND)
        bag_sizer1.Add(self.order_content3, pos=(0, 3), span=(1, 1), flag=wx.EXPAND)
        bag_sizer1.Add(self.order_label4, pos=(0, 4), span=(1, 1), flag=wx.EXPAND)
        bag_sizer1.Add(self.order_content4, pos=(0, 5), span=(1, 1), flag=wx.EXPAND)
        bag_sizer1.Add(self.order_label5, pos=(0, 6), span=(1, 1), flag=wx.EXPAND)
        bag_sizer1.Add(self.order_content5, pos=(0, 7), span=(1, 1), flag=wx.EXPAND)
        bag_sizer1.Add(self.order_label6, pos=(0, 8), span=(1, 1), flag=wx.EXPAND)
        bag_sizer1.Add(self.order_content6, pos=(0, 9), span=(1, 1), flag=wx.EXPAND)
        bag_sizer1.Add(self.order_label7, pos=(0, 10), span=(1, 1), flag=wx.EXPAND)
        bag_sizer1.Add(self.order_content7, pos=(0, 11), span=(1, 1), flag=wx.EXPAND)

        sbsizer1.Add(bag_sizer1, proportion=0, flag=wx.EXPAND, border=10)

        sbsizer2 = wx.StaticBoxSizer(self.order_box2, wx.VERTICAL)
        sbsizer2.Add(self.gridpanel, proportion=1, flag=wx.EXPAND, border=10)

        main_sizer.Add(flex_sizer1, flag=wx.EXPAND)
        main_sizer.Add(sbsizer1, flag=wx.EXPAND)
        main_sizer.Add(sbsizer2, -1, flag=wx.EXPAND)
        self.SetSizer(main_sizer)
        self.Layout()

    def __evt_bind(self):

        self.Bind(wx.EVT_TEXT_ENTER, self.onOutsidTextChange, self.out_sid_text)
        self.Bind(wx.EVT_TEXT_ENTER, self.onWeightTextChange, self.weight_text)
        self.Bind(wx.EVT_BUTTON, self.onClickCancelBtn, self.cancel_button)

    def getSid(self, out_sid):

        if len(out_sid) < 20:
            return out_sid
        return out_sid[0:13]

    def getYDValidCode(self, out_sid):

        if len(out_sid) < 20:
            return ''
        return out_sid[13:17]

    def onOutsidTextChange(self, evt):

        out_sid = self.out_sid_text.GetValue().strip()
        if not out_sid:
            return
        try:
            from taobao.dao.dbsession import SessionProvider
            from taobao.dao.models import PackageOrder
            trade = WebApi.begin_scan_check(out_sid)
            po = SessionProvider.session.query(PackageOrder).filter(PackageOrder.out_sid==out_sid, PackageOrder.sys_status.in_([cfg.PKG_WAIT_PREPARE_SEND_STATUS, cfg.PKG_WAIT_CHECK_BARCODE_STATUS, cfg.PKG_WAIT_SCAN_WEIGHT_STATUS])).one()

            if po.redo_sign:
                dial = wx.MessageDialog(None, u'此包裹需要重打发货单，确认已经重打了吗', u'发货单重打提示',
                                        wx.OK | wx.CANCEL | wx.ICON_EXCLAMATION)
                result = dial.ShowModal()
                dial.Destroy()
                # 如果不继续，则退出
                if result != wx.ID_OK:
                    return False
                elif result == wx.ID_OK:
                    WebApi.clear_redo_sign(po.pid)
            self.trade = trade
            self.setTradeInfoPanel(trade)
            self.weight_text.SetFocus()
            self.error_text.SetLabel('')
            self.error_text.SetForegroundColour('white')
            self.error_text.SetBackgroundColour('black')

        except Exception, exc:
            self.error_text.SetLabel(exc.message)
            self.error_text.SetForegroundColour('black')
            self.error_text.SetBackgroundColour('red')
            self.clearTradeInfoPanel()
            self.weight_text.Clear()
            self.out_sid_text.Clear()
            self.out_sid_text.SetFocus()
            winsound.PlaySound(MEDIA_ROOT + 'wrong.wav', winsound.SND_FILENAME)

        evt.Skip()

    def clearTradeInfoPanel(self):
        for i in xrange(1, 7):
            try:
                content = eval('self.order_content%s' % str(i))
                content.Clear()
            except:
                pass

    def setTradeInfoPanel(self, trade):

        self.order_content1.SetValue(trade['seller_nick'] or '')
        self.order_content3.SetValue(trade['trade_type'] or '')
        self.order_content4.SetValue(trade['buyer_nick'] or '')
        self.order_content5.SetValue(trade['company_name'] or '')
        self.order_content6.SetValue(trade['receiver_name'] + '/' + trade['receiver_mobile'])
        self.order_content7.SetValue(' '.join([trade['receiver_state'],
                                               trade['receiver_city'],
                                               trade['receiver_district'],
                                               trade['receiver_address']]))

        self.Layout()

    def onWeightTextChange(self, evt):
        weight = self.weight_text.GetValue().strip()

        if weight_regex.match(weight) and self.trade:
            try:
                self.save_weight_to_trade(self.trade, weight)
                self.weight_text.Clear()
                self.out_sid_text.Clear()
                self.out_sid_text.SetFocus()
                winsound.PlaySound(MEDIA_ROOT + 'success.wav', winsound.SND_FILENAME)

            except Exception, exc:
                dial = wx.MessageDialog(None, u'重量保存出错:%s' % exc.message, u'扫描称重提示',
                                        wx.OK | wx.CANCEL | wx.ICON_EXCLAMATION)
                dial.ShowModal()
                dial.Destroy()
        else:
            winsound.PlaySound(MEDIA_ROOT + 'wrong.wav', winsound.SND_FILENAME)

    def save_weight_to_trade(self, trade, weight):
        WebApi.complete_scan_weight(trade['package_no'], weight)
        trade['weight'] = weight
        self.gridpanel.InsertTradeRows(trade)
        self.trade = None
        self.valid_code = ''
        for control in self.control_array:
            control.SetValue('')

    def getPreWeightStatus(self):
        conf = getconfig()
        is_need_check = conf.get('custom', 'check_barcode')
        if is_need_check.lower() == 'true':
            return (cfg.SYS_STATUS_WAITSCANWEIGHT,)
        return (cfg.SYS_STATUS_WAITSCANWEIGHT, cfg.SYS_STATUS_WAITSCANCHECK)

    def onClickCancelBtn(self, evt):
        self.out_sid_text.Clear()
        self.weight_text.Clear()
        for control in self.control_array:
            control.Clear()
        self.out_sid_text.SetFocus()
