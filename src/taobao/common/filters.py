'''
Created on 2012-6-5

@author: user1
'''


def datetimeformat(value,format='%Y-%m-%d %H:%M:%S'):
    return value.strftime(format)

def trans_string(string,decoding='utf8',encoding='gbk'):
    return string.decode(decoding).encode(encoding)


def print_wraps(orders,max_num=45):
    remain_nums = max_num - len(orders)
    return '<br>'*remain_nums

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
