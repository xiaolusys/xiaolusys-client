#-*- coding:utf8 -*-

TRADE_STATUS_NO_PAY = 'TRADE_NO_CREATE_PAY'
TRADE_STATUS_WAIT_PAY = 'WAIT_BUYER_PAY'
TRADE_STATUS_WAIT_SEND_GOODS = 'WAIT_SELLER_SEND_GOODS'
TRADE_STATUS_WAIT_CONFIRM_GOODS = 'WAIT_BUYER_CONFIRM_GOODS'
TRADE_STATUS_COD_SIGNED = 'TRADE_BUYER_SIGNED'
TRADE_STATUS_FINISHED = 'TRADE_FINISHED'
TRADE_STATUS_CLOSED = 'TRADE_CLOSED'
TRADE_STATUS_CLOSED_BY_TAOBAO = 'TRADE_CLOSED_BY_TAOBAO'

TRADE_STATUS = {
    TRADE_STATUS_NO_PAY:'卖家没有支付宝',
    TRADE_STATUS_WAIT_PAY:'等待买家付款',
    TRADE_STATUS_WAIT_SEND_GOODS:'等待发货',
    TRADE_STATUS_WAIT_CONFIRM_GOODS:'等待确认收货',
    TRADE_STATUS_COD_SIGNED:'货到付款已签收',
    TRADE_STATUS_FINISHED:'交易成功',
    TRADE_STATUS_CLOSED:'退款成功',
    TRADE_STATUS_CLOSED_BY_TAOBAO:'关闭交易',
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

SYS_STATUS_ALL     = 'ALL'
SYS_STATUS_UNAUDIT = 'WAIT_AUDIT'
SYS_STATUS_AUDITFAIL = 'AUDITFAIL'
SYS_STATUS_PREPARESEND = 'WAIT_PREPARE_SEND'
SYS_STATUS_SCANWEIGHT = 'WAIT_SCAN_WEIGHT'
SYS_STATUS_CONFIRMSEND = 'WAIT_CONFIRM_SEND'
SYS_STATUS_SYSTEMSEND = 'SYSTEM_SEND_TAOBAO'
SYS_STATUS_FINISHED = 'FINISHED'
SYS_STATUS_INVALID = 'INVALID'

SYS_STATUS = {
    SYS_STATUS_UNAUDIT:'未审核',
    SYS_STATUS_AUDITFAIL:'待发货准备',
    SYS_STATUS_PREPARESEND:'待扫描称重',
    SYS_STATUS_SCANWEIGHT:'待确认发货',
    SYS_STATUS_SYSTEMSEND:'待更新发货状态',
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
    'WAIT_SELLER_AGREE':'等待卖家同意',
    'WAIT_BUYER_RETURN_GOODS':'等待买家退货',
    'WAIT_SELLER_CONFIRM_GOODS':'等待买家确认收货',
    'SELLER_REFUSE_BUYER':'卖家拒绝退款',
    'CLOSED':'退款关闭',
    'SUCCESS':'退款成功',
}