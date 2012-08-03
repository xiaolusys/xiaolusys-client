#-*- coding:utf8 -*-
'''
Created on 2012-7-27

@author: user1
'''
import wx,wx.grid
from taobao.dao.models import Trade

class DeliveryPanel(wx.Panel):
    
    def __init__(self,parent,id=-1):
        wx.Panel.__init__(self,parent,id,style=wx.TAB_TRAVERSAL | wx.CLIP_CHILDREN | wx.FULL_REPAINT_ON_RESIZE)
        
        self.session = parent.session
        self.datasource = None
        self.select_ids = set() 
        self.isSearchPanelShow = True
        self.isSearchResultShow = False
        self.colLabels = ('订单号','订单类型','订单来源','物流单号','物流公司','店铺简称','买家昵称','商品数量','支付金额','已审核','已打印发货单','已打印物流单','付款时间')
        
        self.delivery_label1 = wx.StaticText(self,-1,'来源单号')
        self.delivery_text1  = wx.TextCtrl(self,-1)
        self.delivery_label2 = wx.StaticText(self,-1,'来源平台')
        self.delivery_combobox1 = wx.ComboBox(self,-1,choices=('淘宝商城','淘宝分销'))
        self.delivery_button1    = wx.Button(self,-1,label='查询')
        self.error_label     = wx.StaticText(self,-1,'')
        self.logistic_label  = wx.StaticText(self,-1,'选择显示物流类型')
        self.logistic_combobox = wx.ComboBox(self,-1)
        
        self.delivery_line1 = wx.Button(self,-1,size=(-1,20))
        
        self.delivery_label4 = wx.StaticText(self,-1,'店铺简称')
        self.delivery_text2  = wx.TextCtrl(self,-1)
        self.delivery_label5 = wx.StaticText(self,-1,'买家名称')
        self.delivery_text3  = wx.TextCtrl(self,-1)
        self.delivery_label6 = wx.StaticText(self,-1,'商品数量')
        self.delivery_text4  = wx.TextCtrl(self,-1)
        self.delivery_label7 = wx.StaticText(self,-1,'支付金额')
        self.delivery_text5  = wx.TextCtrl(self,-1)
        self.delivery_label8 = wx.StaticText(self,-1,'已审核')
        self.delivery_checkbox1 = wx.CheckBox(self,-1)
        
        self.delivery_label9 = wx.StaticText(self,-1,'物流单号')
        self.delivery_text6  = wx.TextCtrl(self,-1)
        self.delivery_label10 = wx.StaticText(self,-1,'物流公司')
        self.delivery_text7  = wx.TextCtrl(self,-1)
        self.delivery_label11 = wx.StaticText(self,-1,'已打印发货单')
        self.delivery_checkbox2 = wx.CheckBox(self,-1)
        self.delivery_label12 = wx.StaticText(self,-1,'已打印物流单')
        self.delivery_checkbox3 = wx.CheckBox(self,-1)
        self.delivery_button2 = wx.Button(self,-1,'+添加+')
       
        self.static_button_up = wx.Button(self,-1,label='v------------v',size=(-1,11)) 
        self.delivery_grid = wx.grid.Grid(self,-1)
        
        self.delivery_line2 = wx.Button(self,-1,size=(-1,8))
        self.select_all_label = wx.StaticText(self,-1,'  全  选')
        self.select_all_check = wx.CheckBox(self,-1)
        self.delivery_label13  = wx.StaticText(self,-1,'物流单号')
        self.delivery_text8    = wx.TextCtrl(self,-1)
        self.delivery_label14  = wx.StaticText(self,-1,'自动填写')
        self.delivery_checkbox4 = wx.CheckBox(self,-1)
        self.delivery_button3  = wx.Button(self,-1,label='确认填写物流编号')
        
        self.delivery_button4  = wx.Button(self,-1,label='打印发货单')
        self.delivery_button5  = wx.Button(self,-1,label='打印物流单')
        
        self.__set_properties()
        self.__do_layout()
        
        self.__bind_evt()
        
    
    def __set_properties(self):    
        self.SetName('delivery_panel')
        font = wx.Font(10,wx.SWISS,wx.SLANT,wx.BOLD,False)
        self.delivery_button4.SetFont(font)
        self.delivery_button5.SetFont(font)
        
    
    def __do_layout(self):
        self.main_sizer = main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.search_sizer = box_sizer1 = wx.BoxSizer(wx.VERTICAL)
        flex_sizer1 = wx.FlexGridSizer(hgap=10, vgap=10)
        flex_sizer1.Add(self.delivery_label1,flag=wx.EXPAND)
        flex_sizer1.Add(self.delivery_text1,flag=wx.EXPAND)
        flex_sizer1.Add(self.delivery_label2,flag=wx.EXPAND)
        flex_sizer1.Add(self.delivery_combobox1,flag=wx.EXPAND)
        flex_sizer1.Add(self.delivery_button1,flag=wx.EXPAND)
        flex_sizer1.Add(self.error_label,flag=wx.EXPAND)
        flex_sizer1.Add(self.logistic_label,flag=wx.EXPAND)
        flex_sizer1.Add(self.logistic_combobox,flag=wx.EXPAND)
        
        self.grid_sizer = grid_sizer1 = wx.GridBagSizer(hgap=10,vgap=10)
        grid_sizer1.Add(self.delivery_label4,pos=(0,0),span=(1,1),flag=wx.EXPAND)
        grid_sizer1.Add(self.delivery_text2,pos=(0,1),span=(1,1),flag=wx.EXPAND)
        grid_sizer1.Add(self.delivery_label5,pos=(0,2),span=(1,1),flag=wx.EXPAND)
        grid_sizer1.Add(self.delivery_text3,pos=(0,3),span=(1,1),flag=wx.EXPAND)
        grid_sizer1.Add(self.delivery_label6,pos=(0,4),span=(1,1),flag=wx.EXPAND)
        grid_sizer1.Add(self.delivery_text4,pos=(0,5),span=(1,1),flag=wx.EXPAND)
        grid_sizer1.Add(self.delivery_label7,pos=(0,6),span=(1,1),flag=wx.EXPAND)
        grid_sizer1.Add(self.delivery_text5,pos=(0,7),span=(1,1),flag=wx.EXPAND)
        grid_sizer1.Add(self.delivery_label8,pos=(0,8),span=(1,1),flag=wx.EXPAND)
        grid_sizer1.Add(self.delivery_checkbox1,pos=(0,9),span=(1,1),flag=wx.EXPAND)
        
        grid_sizer1.Add(self.delivery_label9,pos=(1,0),span=(1,1),flag=wx.EXPAND)
        grid_sizer1.Add(self.delivery_text6,pos=(1,1),span=(1,1),flag=wx.EXPAND)
        grid_sizer1.Add(self.delivery_label10,pos=(1,2),span=(1,1),flag=wx.EXPAND)
        grid_sizer1.Add(self.delivery_text7,pos=(1,3),span=(1,1),flag=wx.EXPAND)
        grid_sizer1.Add(self.delivery_label11,pos=(1,4),span=(1,1),flag=wx.EXPAND)
        grid_sizer1.Add(self.delivery_checkbox2,pos=(1,5),span=(1,1),flag=wx.EXPAND)
        grid_sizer1.Add(self.delivery_label12,pos=(1,6),span=(1,1),flag=wx.EXPAND)
        grid_sizer1.Add(self.delivery_checkbox3,pos=(1,7),span=(1,1),flag=wx.EXPAND)
        grid_sizer1.Add(self.delivery_button2,pos=(1,8),span=(1,1),flag=wx.EXPAND)
        
        
        box_sizer1.Add(flex_sizer1,flag=wx.EXPAND)
        box_sizer1.Add(self.delivery_line1,flag=wx.EXPAND)
        box_sizer1.Add(grid_sizer1,flag=wx.EXPAND)
        
        box_sizer1.Hide(grid_sizer1)
        
        box_sizer6 = wx.FlexGridSizer(hgap=20, vgap=20)
        box_sizer6.Add(self.select_all_label,flag=wx.EXPAND)
        box_sizer6.Add(self.select_all_check,flag=wx.EXPAND)
        box_sizer6.Add(self.delivery_label13,flag=wx.EXPAND)
        box_sizer6.Add(self.delivery_text8,flag=wx.EXPAND)
        box_sizer6.Add(self.delivery_label14,flag=wx.EXPAND)
        box_sizer6.Add(self.delivery_checkbox4,flag=wx.EXPAND)
        box_sizer6.Add(self.delivery_button3,flag=wx.EXPAND)
        box_sizer6.Add(self.delivery_button4,flag=wx.EXPAND)
        box_sizer6.Add(self.delivery_button5,flag=wx.EXPAND)
        
        main_sizer.Add(box_sizer1,flag=wx.EXPAND)
        main_sizer.Add(self.static_button_up,flag=wx.EXPAND)
        main_sizer.Add(self.delivery_grid,1,flag=wx.EXPAND)
        main_sizer.Add(self.delivery_line2,flag=wx.EXPAND)
        main_sizer.Add(box_sizer6,flag=wx.EXPAND) 
        
        self.SetSizer(main_sizer)
        self.Layout()
        
        
        
    def __bind_evt(self):
        self.Bind(wx.EVT_BUTTON,self.onClickSearchButton,self.delivery_button1)
        self.Bind(wx.EVT_BUTTON,self.onClickStaticButton,self.static_button_up)
          
    def updateTable(self):
        self.parseIDToTuple(self.select_ids)
    
    
    def parseIDToTuple(self,trade_ids):
        #('订单号','物流单号','物流公司','店铺简称','买家昵称','商品数量','支付金额','已审核','已打印发货单','已打印物流单','付款时间')
        assert isinstance(trade_ids,(tuple,list,set))
        trades = self.session.query(Trade).filter(Trade.id.in_(trade_ids))
        array_object = []
        for object in trades:
            object_array = []
            object_array.append(object.id)
            object_array.append(object.type)
            object_array.append(object.buyer_nick)
            object_array.append(object.total_fee)
            object_array.append(object.discount_fee)
            object_array.append(object.adjust_fee)
            object_array.append(object.post_fee)
            object_array.append(object.payment)
            object_array.append(object.pay_time)
            object_array.append(object.shipping_type)
            object_array.append('ztc')
            object_array.append('中通快递')
            object_array.append('')
            array_object.append(object_array)
        return array_object
        
    
    def setData(self,datasource):
        pass
    
    def onSelectAllCheckbox(self,evt):
        rows = self.grid.NumberRows
        if evt.IsChecked():
            for i in xrange(0,rows):
                self.grid.SetCellValue(i,0,'1')
                self._selectedRows.add(i)
        else: 
            for i in xrange(0,rows):
                self.grid.SetCellValue(i,0,'')
            self._selectedRows.clear()
        self.grid.ForceRefresh() 
    
    def onClickSearchButton(self,evt):
        if self.isSearchResultShow:
            self.search_sizer.Hide(self.grid_sizer)
            self.isSearchResultShow=False
        else:
            self.search_sizer.Show(self.grid_sizer)
            self.isSearchResultShow=True
        self.main_sizer.Layout()
        self.Layout()
        
        
    
    def onClickStaticButton(self,evt):
        if self.isSearchPanelShow:
            self.main_sizer.Hide(self.search_sizer)
            self.search_sizer.Hide(self.grid_sizer)
            self.static_button_up.SetLabel('v------------v')
            self.isSearchPanelShow = False
            self.isSearchResultShow=False
        else:
            self.main_sizer.Show(self.search_sizer)
            self.static_button_up.SetLabel('^------------^')
            self.isSearchPanelShow = True
        if self.isSearchResultShow:
            self.search_sizer.Show(self.grid_sizer)
        else:
            self.search_sizer.Hide(self.grid_sizer)
        self.delivery_grid.Layout()
        self.main_sizer.Layout()
        self.Layout()


class MyFrame(wx.Frame): 
    def __init__(self, parent): 
        wx.Frame.__init__(self, parent, title="wxGrid Demo") 
        
        self.Sizer = wx.BoxSizer(wx.VERTICAL) 
        self.Sizer.Add(DeliveryPanel(self,-1),-1, wx.EXPAND) 
        self.Sizer.Layout()
        
        
if __name__ == "__main__": 
    app = wx.App(False) 
    frame = MyFrame(None).Show(True) 
    app.MainLoop() 
    
    
        