if "%1" == "h" goto begin
mshta vbscript:createobject("wscript.shell").run("%~nx0 h",0)(window.close)&&exit
:begin
;echo  'abc' >> ./test.txt
python C:\Users\user1\workspace\taobao-erp-client\src\auimain.py