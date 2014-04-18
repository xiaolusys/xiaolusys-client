import os
import _winreg as _reg 

pageSetupPath = r"SOFTWARE\\Microsoft\\Internet Explorer\\PageSetup\\"

def writeRegdit(regPath,key,value):
    
    if not os.path.exists(regPath):
        _reg.CreateKey(_reg.HKEY_CURRENT_USER,pageSetupPath)
        
    reg_key = _reg.OpenKey(_reg.HKEY_CURRENT_USER,pageSetupPath, 0,_reg.KEY_WRITE)
    _reg.SetValueEx(reg_key,key,0,_reg.REG_SZ,value)
    _reg.CloseKey(reg_key)
    
    
def updateRegedit(reg_path,kv_map):
    
    for k,v in kv_map.iteritems():
        writeRegdit(reg_path,k,v)
        
        
def updatePageSetupRegedit(page_setup_kvmap):
    
    updateRegedit(pageSetupPath,page_setup_kvmap)
    

