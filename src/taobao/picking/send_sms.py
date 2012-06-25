#coding=utf-8 

'''
Created on 2012-6-14

@author: user1
'''
import sys
import win32com.client

ocxname = 'SMSOCX_SmsGate80.Smsgate'
sms_service_call = '+8613010314500'
comm_port = 4
rate = '9600,n,8,1'
sn   = 'meixqhi'

def send_message_to_buyer(msg,buyer_call,ocxname=ocxname,comm_port=comm_port
                          ,sms_service_call=sms_service_call,rate=rate,sn=sn):
    axocx=win32com.client.Dispatch(ocxname)
    axocx.CommPort=comm_port
    
    axocx.SmsService=sms_service_call #+8613010314500或008613010314500
    axocx.Settings=rate
    axocx.sn=sn
    c=axocx.Connect(1)
    axocx.Link()
    axocx.SendSms(msg,buyer_call,0)
