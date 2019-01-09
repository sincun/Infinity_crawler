<h5># Infinity_crawler</>

<h6>#python Environmen  at python3.5</>
<h6>#startup</>
<h6>./launchCapture.py</>
<h6>writees = True表示数据将写入es,false则是不写入，解析后html字段超过1000将不能写入es</>
<h6>所有下载的web页面都在webpage目录，目前没有写随机生成url方法，需要手动传入初始url,INIT_URL指定初始url</>
<h6>解析url可能会有部分带有脚本代码的html会导致解析错误，该类错误将被忽略，可在日志中查看，该工具仅供学习使用，没有保证结果的绝对正确</>
<h6>statistics=0表示下载url不受限制，程序将不会停止，后边跟数字，如statistics=1表示下载完1个url后下载程序将退出，后续解析程序也将退出</>
<h6>urlbase.map为es maps,由于python es有部分设置无法创建，暂时未使用，使用默认创建的maps</>
<h6>launchCapture.py:启动文件，脚本启动一个进程和一个进程池，分别下载和解析web页面</>
<h6>acrawler.py:判断页面是否下载，解析url路径</>
<h6>filedownload.py：下载web页面中的内容，如图片、url等</>
<h6>splitcontent.py：解析url生成json数据</>
<h6>writeES.py：写入es方法</>
<h6>setting.py：全局设置文件</>
<h6>-----------------待优化内容-------------------</>
<h6>1.自动爬去动态页面和需要授权页面</>

