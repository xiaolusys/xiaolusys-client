::if exist #hide.vbs (del #hide.vbs &goto begin) else (echo createobject^("wscript.shell"^).run "%~fs0",0 >#hide.vbs&start #hide.vbs&exit)
if "%1" == "h" goto begin
mshta vbscript:createobject("wscript.shell").run("%~nx0 h",0)(window.close)&&exit
:begin

python C:\Users\user1\workspace\taobao-erp-client\src\auimain.py