import random
import socket
import traceback
from socket import *

import filedownload
from setting import *


#
#
#author: Mr.S

class crawler(object):

    def __init__(self,url):

        self.webPage = set()
        self.partition = re.compile(r'^(http[s]?)://([^/]*)')
        matched = self.partition.match(url)
        self.url = url
        self.port = 80
        heads = 'http://'

        if matched:
            #host = matched.group(0)[:-1]
            self.host = matched.group(2)
            self.website = matched.group(0)
            if matched.group(1) == 'https':
                    self.port = 443
                    heads = 'https://'
        else:
            LOGGER.warn("url format error '{0}'".format(url))
            sys.exit(1)

        host1 = self.website+'#'
        host2 = self.website+'javascript:;'
        self.sitearry = set([host1,host2])

        
    def buildsock(self):
        
        #partition = re.compile(r'^([a-z]+)://(.*?)/')
        #matched = partition.match(url)
        #if matched:
        #    #host = matched.group(0)[:-1]
        #    host = matched.group(2)
        #    website = matched.group(0)
        #    if matched.group(1) == 'https':
        #            port = 443
                    
        #print(self.port)
        #print(self.host)
        address = (self.host,self.port)
        LOGGER.debug(address)
        sock = socket()
        sock.settimeout(6)
        try:
            sock.connect(address)
        except :
            LOGGER.warn("acrawler url connnect timeout,{0}".format(address))
            recodeExcept(*sys.exc_info())
            LOGGER.error(traceback.format_exc())
            LOGGER.error("Except EOF")
            return None

        #request =  'GET {} HTTP/1.0\r\nHost:{}\r\n\r\n '.format(host,url)
        #User-Agent需要做成随机的防止封禁
        randomNum = random.randint(0,9)
        userAgent = USER_AGENT[randomNum]
        request =  'GET {} HTTP/1.0\r\nHost:{}\r\n\r\n User-Agent:{}\r\n\r\n'.format(self.url,self.host,userAgent)
        try:
            sock.send(request.encode())
        except  Exception as e:
            LOGGER.error("url error or host is change or ",userAgent)
            LOGGER.error(e)

        data = self.foreach(sock)

        return data
    
    def foreach(self,sock):
        
        recvdata = b''
        chunk = sock.recv(4096)
        while True:
            if chunk:
                #print('chunk',chunk)
                recvdata += chunk
                chunk = sock.recv(4096)
            else:
                if recvdata:
                    LOGGER.debug("fetcht page data! url:'{0}'".format(self.url))
                else:
                    LOGGER.error("chunk is None ,sock will close!{0}".format(sock))
                    LOGGER.error("failed page content ,url is '{0}'".format(self.url))
                sock.close()
                break
        #print('data',recvdata)
        try:
            recvdata = recvdata.decode()
        except UnicodeDecodeError as ude:
            LOGGER.error("Unicode Decode to utf8 Error,",ude)
            return None
        return recvdata

    def fullurl(self,link):
        #
        link = link.strip('"')
        if re.match(r'http',link):
            website = ""
        else:
            website = self.website
        #print('handle',website,"link",link)
        return website+link


    def analysisHandler(self,pagedata):
        # 超链接，表单，脚本，图片
        # 如果是绝对路径，直接使用绝对路径，否则进行拼接：
        # /js/plugin.js,拼接完就是http://www.bwlc.gov.cn/js/plugin.js
        #
        category = re.compile(r'<a href="(.*?)"|<tbody>(.*?)</tbody>|<script.*?src="(.*?)"|<img src="(.*?)"')
        if pagedata:
            matched = category.findall(pagedata)
        else:
            LOGGER.error("Fetching result is None,will exit fetch page")
            return set()
        # print('a',matched[1])
        # mlock = threading.Lock()
        # 下载页面自身，不计入待下载集合中
        # self.ophref(url,1)
        for i in matched:
            # print(i)
            if i[0]:
                # print(i[0])
                self.ophref(i[0])

            if i[1]:
                self.optable(self.fullurl(i[1]))

            if i[2]:
                self.opscript(i[2])

            if i[3]:
                self.opimgs(self.fullurl(i[3]))
# analysis url
    def analysis(self):
        
        if not self.host:
            LOGGER.error('host is analysis failed!url is error')
            return set()
        data = self.buildsock()
        self.analysisHandler(data)

        return self.webPage

        #--根据不同类型建立进程池，在进程池中分别建立多线程处理每种结果类型--

    def fetchfileurl(self,types,mkpath):

        partern = PARTERN
        protocol = re.compile(r'http[s]?://(.*)')

        #判断路径是否带有协议标识，有就去掉(https://)
        ifFullurl = protocol.match(mkpath)
        if ifFullurl:
            mkpath = ifFullurl.group(1)
        
        fullfilepath = [types,self.host]

        filename = mkpath.split('/')
        for p in filename[:-1]:
            #print(p)
            if p:
                if p == '.' or p == '/':
                    continue
                elif p == '..':
                    if fullfilepath and len(fullfilepath) >1:
                        fullfilepath.pop(-1)
                    else:
                        fullfilepath.append(p)
                else:    
                    fullfilepath.append(p)
            else:
                continue
        #print('1111111111',filename[-1])    
        fullfilepath.append(partern.match(filename[-1]).group(1))

        #print(fullfilepath)
        return fullfilepath
    #启动一个新的线程或进程继续解析连接
    def ophref(self,href,pagetype=None):

        fetchsuffix = re.compile(r'\S+\.(\w+)$')
        fullhref = self.fullurl(href)
        try:
            if fullhref in self.sitearry:
                return 1
            else:
                self.sitearry.add(fullhref)
            
            LOGGER.debug('page href link,will download:{0}'.format(href))
            path = self.fetchfileurl('webpage',href)

            #print('path',path)
            pagename = path[-1]
            matchsuffix = fetchsuffix.search(pagename)
            download = filedownload.fileDownload(fullhref,path)
            download.start()

            pagesuffix = pagename
            if matchsuffix:
                pagesuffix = matchsuffix.group(1)

            suffixname = STATICPAGE + DYNAMICPAGE
            if pagesuffix in suffixname and pagetype != 1:
                self.webPage.add(fullhref)
            #self.analysis(fullhref)
            #pass
            
        except TypeError as e:
            LOGGER.error("url is error",href)
            LOGGER.error(e)
        return 0

    def optable(self,table):
        #table中可能有链接或者图片，得分开对待
        print('optable',table)
        pass

    def opscript(self,script):
        #同href，超链接
        #print('opscript',script)
        self.ophref(script)

    def opimgs(self,imgs):
        #图片直接下载即可
        dirs = 'imges/'+self.host
        #names = imgs.split('/')[-1]

        #download = filedownload.fileDownload(imgs,dirs)
        #download.start()
        #path = dirs+'/'+names
        #self.mkdir(dirs)

        #print('opimgs',imgs)


    def opvidio(self,video):
        #视频，直接下载即可
        dirs = 'video'

        #download = filedownload.fileDownload(video,dirs)
        #download.start()
        #names = imgs.split('/')[-1]
        #path = dirs+'/'+names
        #self.mkdir(dirs)
        
        print('opvidio',video)
        
    def mkdir(self,dirs):

        try:
            if not os.path.exists(dirs):
                os.mkdir(dirs)
        except:
            print('Failded to create directory in %s'%dirs)
            exit(1)

        
    def analysistest(self,target):

        with open(target,'r',encoding='utf-8') as f:
            content = f.read()
            #print(content)

        self.analysis(content)
        if f:
            f.close()

        return content

if __name__ == '__main__':

    url = 'http://c.youdao.com/dict/activity/pronPrefTest/index.html?keyfrom=dict2.index'
    #url = 'http://www.google.com'
    crawler = crawler(url)
    r = crawler.analysis()
    print(r)
