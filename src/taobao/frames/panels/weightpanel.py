#-*- coding:utf8 -*-
'''
Created on 2012-7-27

@author: user1
'''
import wx,wx.grid

class ScanWeightPanel(wx.Panel):
    
    def __init__(self,parent,id=-1):
        wx.Panel.__init__(self,parent,id)
        
        self.company_label = wx.StaticText(self,-1,'快递公司')
        self.company_select = wx.Choice(self,-1)
        self.out_sid_label = wx.StaticText(self,-1,'快递单号')
        self.out_sid_text  = wx.TextCtrl(self,-1)
        self.weight_label  = wx.StaticText(self,-1,'称重重量')
        self.weight_text  = wx.TextCtrl(self,-1)
        
        self.order_label1  = wx.StaticText(self,-1,'店铺简称')
        self.order_content1  = wx.TextCtrl(self,-1)
        self.order_label2  = wx.StaticText(self,-1,'订单类型')
        self.order_content2  = wx.TextCtrl(self,-1)
        self.order_label3  = wx.StaticText(self,-1,'来源单号')
        self.order_content3  = wx.TextCtrl(self,-1)
        self.order_label4  = wx.StaticText(self,-1,'会员名称')
        self.order_content4  = wx.TextCtrl(self,-1)
        self.order_label5  = wx.StaticText(self,-1,'物流公司')
        self.order_content5  = wx.ComboBox(self,-1)
        self.order_label6  = wx.StaticText(self,-1,'物流单号')
        self.order_content6  = wx.TextCtrl(self,-1)

        self.order_label8  = wx.StaticText(self,-1,'物流成本')
        self.order_content8  = wx.TextCtrl(self,-1)
        self.order_label9  = wx.StaticText(self,-1,'订单状态')
        self.order_content9  = wx.TextCtrl(self,-1)
        self.order_label10  = wx.StaticText(self,-1,'系统状态')
        self.order_content10  = wx.TextCtrl(self,-1)
        self.order_label11  = wx.StaticText(self,-1,'收货人')
        self.order_content11  = wx.TextCtrl(self,-1)
        self.order_label12  = wx.StaticText(self,-1,'收货人固定电话')
        self.order_content12  = wx.TextCtrl(self,-1,'') 
        self.order_label13  = wx.StaticText(self,-1,'收货人手机')
        self.order_content13  = wx.TextCtrl(self,-1)
        
        self.order_label14  = wx.StaticText(self,-1,'收货邮编')
        self.order_content14  = wx.TextCtrl(self,-1)
        self.order_label15  = wx.StaticText(self,-1,'所在省')
        self.order_content15  = wx.TextCtrl(self,-1)
        self.order_label16  = wx.StaticText(self,-1,'所在市')
        self.order_content16  = wx.TextCtrl(self,-1)
        self.order_label17  = wx.StaticText(self,-1,'所在地区')
        self.order_content17  = wx.TextCtrl(self,-1)
        self.order_label18  = wx.StaticText(self,-1,'收货人信息')
        self.order_content18 = wx.TextCtrl(self,-1)
        self.order_label19  = wx.StaticText(self,-1,'收货地址')
        self.order_content19  = wx.TextCtrl(self,-1,size=(200,-1))
        
        self.grid = wx.grid.Grid(self,-1)
        self.grid.CreateGrid(10,8)
        self.order_box = wx.StaticBox(self,-1,'已称重订单列表')
        
        
        self.__set_properties()
        self.__do_layout()
        self.__evt_bind()
    
    
    def __set_properties(self):
        pass
    
    def __do_layout(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        box_sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        box_sizer1.Add(self.company_label,flag=wx.EXPAND)
        box_sizer1.Add(self.company_select,flag=wx.EXPAND)
        box_sizer1.Add(self.out_sid_label,flag=wx.EXPAND)
        box_sizer1.Add(self.out_sid_text,flag=wx.EXPAND)
        box_sizer1.Add(self.weight_label,flag=wx.EXPAND)
        box_sizer1.Add(self.weight_text,flag=wx.EXPAND)
        
        bag_sizer1 = wx.GridBagSizer(hgap=5,vgap=5)
        bag_sizer1.Add(self.order_label1,pos=(0,0),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_content1,pos=(0,1),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_label2,pos=(0,2),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_content2,pos=(0,3),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_label3,pos=(0,4),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_content3,pos=(0,5),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_label4,pos=(0,6),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_content4,pos=(0,7),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_label5,pos=(0,8),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_content5,pos=(0,9),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_label6,pos=(0,10),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_content6,pos=(0,11),span=(1,1),flag=wx.EXPAND)
        
        bag_sizer1.Add(self.order_label8,pos=(1,0),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_content8,pos=(1,1),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_label9,pos=(1,2),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_content9,pos=(1,3),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_label10,pos=(1,4),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_content10,pos=(1,5),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_label11,pos=(1,6),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_content11,pos=(1,7),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_label12,pos=(1,8),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_content12,pos=(1,9),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_label13,pos=(1,10),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_content13,pos=(1,11),span=(1,1),flag=wx.EXPAND)
        
        bag_sizer1.Add(self.order_label14,pos=(2,0),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_content14,pos=(2,1),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_label15,pos=(2,2),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_content15,pos=(2,3),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_label16,pos=(2,4),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_content16,pos=(2,5),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_label17,pos=(2,6),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_content17,pos=(2,7),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_label18,pos=(2,8),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_content18,pos=(2,9),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_label19,pos=(2,10),span=(1,1),flag=wx.EXPAND)
        bag_sizer1.Add(self.order_content19,pos=(2,11),span=(1,1),flag=wx.EXPAND)

        sbsizer=wx.StaticBoxSizer(self.order_box,wx.VERTICAL)
        sbsizer.Add(self.grid,proportion=0,flag=wx.EXPAND,border=10) 
        
        main_sizer.Add(box_sizer1,flag=wx.EXPAND)
        main_sizer.Add(bag_sizer1,flag=wx.EXPAND)
        main_sizer.Add(sbsizer,1,flag=wx.EXPAND)
        self.SetSizer(main_sizer)
        self.Layout()
        
    def __evt_bind(self):
        pass
        
        
class TestFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, "Custom cell editor test", size=(900,600))

        grid = ScanWeightPanel(self,-1)
        self.CentreOnScreen()

class MyApp(wx.App):
    def OnInit(self):
        frame = TestFrame(None)
        frame.Show(True)
        self.SetTopWindow(frame)
        return True  
          
MyApp(0).MainLoop()        