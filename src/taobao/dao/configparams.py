#-*- coding:utf8 -*-

TRADE_STATUS = {
    'TRADE_NO_CREATE_PAY':'卖家没有支付宝',
    'WAIT_BUYER_PAY':'等待买家付款',
    'WAIT_SELLER_SEND_GOODS':'等待发货',
    'WAIT_BUYER_CONFIRM_GOODS':'等待确认收货',
    'TRADE_BUYER_SIGNED':'买家已签收',
    'TRADE_FINISHED':'交易成功',
    'TRADE_CLOSED':'退款成功',
    'TRADE_CLOSED_BY_TAOBAO':'关闭交易',
}

TRADE_TYPE = {
    'fixed':'一口价',
    'auction':'拍卖',
    'guarantee_trade':'一口价拍卖',
    'auto_delivery':'自动发货',
    'independent_simple_trade':'旺店入门版交易',
    'independent_shop_trade':'旺店标准版交易',
    'ec':'直冲',
    'cod':'货到付款',
    'fenxiao':'分销',
    'game_equipment':'游戏装备',
    'shopex_trade':'ShopEX交易',
    'netcn_trade':'万网交易',
    'external_trade':'统一外部交易',
    
}

SYS_STATUS_ALL = 'ALL'
SYS_STATUS_UNAUDIT = 'UNAUDIT'
SYS_STATUS_AUDITFAIL = 'AUDITFAIL'
SYS_STATUS_PREPARESEND = 'PREPARESEND'
SYS_STATUS_SCANWEIGHT = 'SCANWEIGHT'
SYS_STATUS_CONFIRMSEND = 'CONFIRMSEND'
SYS_STATUS_FINISHED = 'FINISHED'
SYS_STATUS_INVALID = 'INVALID'

SYS_STATUS = {
    SYS_STATUS_UNAUDIT:'未审核',
    SYS_STATUS_AUDITFAIL:'准备发货',
    SYS_STATUS_PREPARESEND:'待扫描称重',
    SYS_STATUS_SCANWEIGHT:'待确认发货',
    SYS_STATUS_CONFIRMSEND:'已发货',
    SYS_STATUS_FINISHED:'审核未通过',
    SYS_STATUS_INVALID:'已作废',
}

SHIPPING_TYPE ={
    'free':'卖家包邮',
    'post':'平邮',
    'express':'快递',
    'ems':'EMS',
    'virtual':'虚拟发货',
}


REFUND_STATUS ={
    
}