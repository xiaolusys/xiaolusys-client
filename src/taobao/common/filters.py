'''
Created on 2012-6-5

@author: user1
'''


def datetimeformat(value,format='%Y-%m-%d %H:%M:%S'):
    return value.strftime(format)

def trans_string(string,decoding='utf8',encoding='gbk'):
    return string.decode(decoding).encode(encoding)


def print_wraps(orders,max_num=45,split_len=10):
    remain_nums = max_num - len(orders)*1.15
    row_lens = 0 
    for order in orders :
        item_name_len = len(order['item_name'])
        properties_len = len(order['properties'])
        item_name_rows = item_name_len/split_len if item_name_len%split_len==0 else item_name_len/split_len+1
        properties_rows = properties_len/split_len if properties_len%split_len==0 else properties_len/split_len+1
        row_len = max(item_name_rows,properties_rows)
        row_lens += row_len-1
    remain_nums -= row_lens*0.65
    return '<br>'*int(round(remain_nums,0))

def parse_val(value,parser='str(round(%d,%d))',decimal=2):
    if type(value) == float :
        return eval(parser%(value,decimal))
    return eval(parser%value)


def slice_string(string,split_len=10,pad_char='<br>'):
    
    if not string and type(string) != str:
        return string
    s_len = len(string)
    str_list = []
    slice_len = s_len/split_len 
    slice_len = slice_len if s_len%split_len == 0 else slice_len+1
    
    for i in range(0,slice_len):
        start = split_len*i
        end   = split_len*(i+1) 
        end   = -1 if end>=s_len else end
        str_list.append(string[start:end])
        
    return pad_char.join(str_list)


def cut_string(string,length=100):
    ls  = len(string)
    lt  = length if ls > length else ls   
    return string[0:lt]

def blur(string,start=3,end=-2):
    slen = len(string)

    if slen<start or slen<end:
        return string
    
    hs = string[0:start]
    es = string[end:-1]
    plen = slen - len(es)
    return hs.ljust(plen,'*')+es

    
