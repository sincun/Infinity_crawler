import re,threading
from queue import Queue
import logging
import sys

LOGGER = logging.getLogger("Acrawler")
_formatter = logging.Formatter('%(asctime)s  %(module)s %(lineno)s %(name)s %(levelname)s:  %(message)s')
_file_handler = logging.FileHandler('acrawler.log',encoding='utf-8')
_file_handler.setFormatter(_formatter)
_console_handler = logging.StreamHandler(sys.stdout)
_console_handler.setFormatter(_formatter)
LOGGER.addHandler(_file_handler)
LOGGER.addHandler(_console_handler)
LOGGER.setLevel(logging.DEBUG)

#@staticmethod
def recodeExcept(etype,evalue,etraceback):

    _err_lineno = etraceback.tb_lineno
    _co_filename = etraceback.tb_frame.f_code.co_filename
    _except_dict = evalue.__dict__
    _except_name = etype.__name__
    if _except_dict:
        _except_reason = evalue.reason
        LOGGER.error(_except_reason)

    _message = "line: {0} file: {1} ExceptName: {2} dictMessage: {3}".format(_err_lineno,_co_filename,_except_name,str(_except_dict))
    LOGGER.error(_message)


THREADINGLOCK = threading.Lock()
THREADINGRLOCK = threading.RLock()
COOKIES_ENABLED = False
PROXY_ADDR = "61.163.39.70:9999"
WEIXIN_UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Mobile/12A365 MicroMessenger/5.4.1 NetType/WIFI"
USER_AGENT = ['Mozilla/5.0(Windows;U;WindowsNT6.1;en-us)AppleWebKit/534.50(KHTML,likeGecko)Version/5.1Safari/534.50',
              'Mozilla/5.0(compatible;MSIE9.0;WindowsNT6.1;Trident/5.0',
              'Mozilla/4.0(compatible;MSIE8.0;WindowsNT6.0;Trident/4.0',
              'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299',
              'Mozilla/5.0(WindowsNT6.1;rv:2.0.1)Gecko/20100101Firefox/4.0.1',
              'Opera/9.80(WindowsNT6.1;U;en)Presto/2.8.131Version/11.11',
              'Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;Trident/4.0;SE2.XMetaSr1.0;SE2.XMetaSr1.0;.NETCLR2.0.50727;SE2.XMetaSr1.0)',
              'Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;360SE)',
              'Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;Trident/4.0;TencentTraveler4.0;.NETCLR2.0.50727)',
              'Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;Maxthon2.0)',
              'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.3']

DN_QUEUE = Queue(500)
ANALY_QUEUE = Queue(500)
#之前已经处理过的url
USEURL = set()
#cut suffix
PARTERN = re.compile(r'^([^\?]*)[\?]?')
STATICPAGE = ('htm','html','shtml','xml')
DYNAMICPAGE = ('aspx','asp','jsp','php','perl','cgi')
EXCLUDEPAGE = ("js","css")

#splitcontent class
NON_ENDLABLE = ('link','meta','img','base','basefont','br','col','embed','frame','hr','input','keygen','param','source','wbr')
#http global attribute
#all global attribute 'accesskey','class','dir','id','lang','style','tabindex','title','contenteditable','contextmenu','data-*','draggable',
#               'dropzone','hidden','spellcheck','translate'
GLOBAL_ATTRIBUTE = ('lang','data-*')
DOWNLOAD_ATTRIBUTE = ('href','src','poster')
#http lable,and attribute
#<a> lable attribute
A_ATTRIBUTE = ('href')

#<script> lable attributs
SCRIPT_ATTRIBUTE = ('src')

#<img> lable attributes
IMG_ATTRIBUTE = ('src')

#<video> lable attributes
VIDEO_ATTRIBUTE = ('poster','src')

#<source> lable attributes
SOURCE_ATTRIBUTE = ('src')

#<link> lable attributes
LINK_ATTRIBUTE = ('href')

#<table> lable attributes
TABLE_ATTRIBUTE = ()

#<tr> lable attributes
TR_ATTRIBUTE = ()

#<td> lable attributes
TD_ATTRIBUTE = ()

#<textarea > lable attributes
TEXTAREA_ATTRIBUTE = ()

#<p> lable attributes
P_ATTRIBUTE = ()

#<h> lable attributes
H_ATTRIBUTE = ()