#! /usr/bin/env python
#coding=utf-8 
import sys
import win32com.client
#ocxname='ShouYan_SmsGate61.Smsgate'
ocxname = 'SMSOCX_SmsGate80.Smsgate'
axocx=win32com.client.Dispatch(ocxname)
axocx.CommPort=4#璁剧疆COM绔彛鍙�
axocx.SmsService='+8613010314500' #+8613010314500或008613010314500
axocx.Settings='9600,n,8,1'#璁剧疆com绔彛閫熷害
axocx.sn='meixqhi'
c=axocx.Connect(1)#杩炴帴鐭俊鐚垨鎵嬫満
print c
print dir(axocx)
print 'send',axocx.Link()

axocx.SendSms('python is very nice','18801806068',0)#鍙戦�鐭俊
