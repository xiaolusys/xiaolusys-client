#-*- coding:utf8 -*-

NORMAL_MODE = 0
DIVIDE_MODE = 1

TRADE_ID_CELL_COL = 1
LOCKED_CELL_COL  = 8
EXPRESS_CELL_COL = 9
PICKLE_CELL_COL = 10
REVIEW_CELL_COL  = 11
LOG_COMPANY_CELL_COL = 12
OUT_SID_CELL_COL = 13
OPERATOR_CELL_COL = 14
QR_MSG_CELL_COL = 15

OUTER_ID_COL = 5
OUTER_SKU_ID_COL = 6
ORIGIN_NUM_COL = 4
BAR_CODE_COL     = 11
NUM_STATUS_COL   = 12

TRADE_STATUS_NO_PAY = 'TRADE_NO_CREATE_PAY'
TRADE_STATUS_WAIT_PAY = 'WAIT_BUYER_PAY'
TRADE_STATUS_WAIT_SEND_GOODS = 'WAIT_SELLER_SEND_GOODS'
TRADE_STATUS_WAIT_CONFIRM_GOODS = 'WAIT_BUYER_CONFIRM_GOODS'
TRADE_STATUS_COD_SIGNED = 'TRADE_BUYER_SIGNED'
TRADE_STATUS_FINISHED = 'TRADE_FINISHED'
TRADE_STATUS_CLOSED = 'TRADE_CLOSED'
TRADE_STATUS_CLOSED_BY_TAOBAO = 'TRADE_CLOSED_BY_TAOBAO'

TRADE_STATUS = {
    TRADE_STATUS_NO_PAY:u'买家没有支付宝',
    TRADE_STATUS_WAIT_PAY:u'等待买家付款',
    TRADE_STATUS_WAIT_SEND_GOODS:u'等待发货',
    TRADE_STATUS_WAIT_CONFIRM_GOODS:u'等待确认收货',
    TRADE_STATUS_COD_SIGNED:u'货到付款已签收',
    TRADE_STATUS_FINISHED:u'交易成功',
    TRADE_STATUS_CLOSED:u'退款成功',
    TRADE_STATUS_CLOSED_BY_TAOBAO:u'关闭交易',
}



TRADE_TYPE = {
    'fixed':u'淘宝&商城',
    'fenxiao':u'分销',
    'jd':u'京东',
    'dd':u'当当',
    'wx':u'微信',
    'yhd':u'一号店',
    'amz':u'亚马逊',
    'direct':u'内售',
    'exchange':u'退换货',
    'reissue':u'补发'
}

SYS_STATUS_ALL     = 'ALL'
SYS_STATUS_WAITAUDIT = 'WAIT_AUDIT'
SYS_STATUS_PREPARESEND = 'WAIT_PREPARE_SEND'
SYS_STATUS_WAITSCANCHECK   = 'WAIT_CHECK_BARCODE'
SYS_STATUS_WAITSCANWEIGHT = 'WAIT_SCAN_WEIGHT'
SYS_STATUS_FINISHED = 'FINISHED'
SYS_STATUS_INVALID = 'INVALID'
SYS_STATUS_REGULAR_REMAIN = 'REGULAR_REMAIN'
SYS_STATUS_ON_THE_FLY = 'ON_THE_FLY'
IN_EFFECT = 'IN_EFFECT'

SYS_STATUS = {
    SYS_STATUS_WAITAUDIT:u'问题单',
    SYS_STATUS_PREPARESEND:u'待发货准备',
    SYS_STATUS_WAITSCANCHECK:u'待扫描验货',
    SYS_STATUS_WAITSCANWEIGHT:u'待扫描称重',
    SYS_STATUS_FINISHED:u'已发货',
    SYS_STATUS_INVALID:u'已作废',
    SYS_STATUS_ON_THE_FLY:u'飞行模式',
    SYS_STATUS_REGULAR_REMAIN:u'定时提醒',
}
PKG_NEW_CREATED = 'PKG_NEW_CREATED'
PKG_WAIT_PREPARE_SEND_STATUS = 'WAIT_PREPARE_SEND_STATUS'
PKG_WAIT_CHECK_BARCODE_STATUS = 'WAIT_CHECK_BARCODE_STATUS'
PKG_WAIT_SCAN_WEIGHT_STATUS = 'WAIT_SCAN_WEIGHT_STATUS'
PKG_WAIT_CUSTOMER_RECEIVE = 'WAIT_CUSTOMER_RECEIVE'
PKG_FINISHED_STATUS = 'FINISHED_STATUS'
PKG_DELETE = 'DELETE'
PACKAGE_STATUS = (
    (PKG_NEW_CREATED, u'初始状态'),
    (PKG_WAIT_PREPARE_SEND_STATUS, u'待发货准备'),
    (PKG_WAIT_CHECK_BARCODE_STATUS, u'待扫描验货'),
    (PKG_WAIT_SCAN_WEIGHT_STATUS, u'待扫描称重'),
    (PKG_WAIT_CUSTOMER_RECEIVE, u'待收货'),
    (PKG_FINISHED_STATUS, u'已到货'),
    (PKG_DELETE, u'已作废')
)
PACKAGE_STATUS_DICT = dict(PACKAGE_STATUS)
SYS_ORDERS_STATUS = {
    IN_EFFECT:u'有效', 
    SYS_STATUS_INVALID:u'无效'
}

SHIPPING_TYPE ={
    'post':u'平邮',
    'express':u'快递',
    'ems':u'EMS',
    'extract':u'无需物流',
    "free":u'卖家包邮',
    "FAST":u'快递',
    "SELLER":u'卖家包邮',
    'EMS':u'EMS',
    'ORDINARY':u'平邮',
}

NO_REFUND = 'NO_REFUND'
WAIT_SELLER_AGREE = 'WAIT_SELLER_AGREE'
WAIT_BUYER_RETURN_GOODS = 'WAIT_BUYER_RETURN_GOODS'
WAIT_SELLER_CONFIRM_GOODS = 'WAIT_SELLER_CONFIRM_GOODS'
SELLER_REFUSE_BUYER = 'SELLER_REFUSE_BUYER'
REFUND_CLOSED = 'CLOSED'
REFUND_SUCCESS = 'SUCCESS'

REFUND_STATUS ={
    'NO_REFUND':u'没有退款',
    'WAIT_SELLER_AGREE':u'等待卖家同意',
    'WAIT_BUYER_RETURN_GOODS':u'等待买家退货',
    'WAIT_SELLER_CONFIRM_GOODS':u'等待买家确认收货',
    'SELLER_REFUSE_BUYER':u'卖家拒绝退款',
    'CLOSED':u'退款关闭',
    'SUCCESS':u'退款成功',
}

REAL_ORDER_GIT_TYPE = 0 #实付
CS_PERMI_GIT_TYPE   = 1 #赠送
OVER_PAYMENT_GIT_TYPE = 2 #满就送
COMBOSE_SPLIT_GIT_TYPE = 3 #拆分
RETURN_GOODS_GIT_TYPE = 4 #退货
CHANGE_GOODS_GIT_TYPE = 5 #换货

ORDER_TYPE = {
    REAL_ORDER_GIT_TYPE:u'实付',
    CS_PERMI_GIT_TYPE:u'赠送',
    OVER_PAYMENT_GIT_TYPE:u'满就送',
    COMBOSE_SPLIT_GIT_TYPE:u'拆分',
    RETURN_GOODS_GIT_TYPE:u'退货',
    CHANGE_GOODS_GIT_TYPE:u'换货',
}

#聚划算系统内部编码
JUHUASUAN_CODE = 16
YUNDA_CODE     = ('YUNDA','YUNDA_QR')
