import os
import ssl
import urllib
import traceback
from setting import *
from urllib import request
#from urllib.request import urlopen


class fileDownload(threading.Thread):

    def __init__(self,url,filepath):
        
        threading.Thread.__init__(self)
        #结尾没有是/或？号，表示目录下有主页，人为给首页index.html
        partern = re.compile(r'/\??$')
        try:
            self.headers = re.match(r'^(http[s]?:)',url).group(1)
        except:
            LOGGER.error("url format error '{0}'".format(url))
            recodeExcept(*sys.exc_info())
            LOGGER.error(traceback.format_exc())
            LOGGER.error("Except EOF")
        self.__downurl = url
        TorF = partern.search(url)
        if TorF:
            self.__filepath = '/'.join(filepath)+"index.html"
        else:
            self.__filepath = '/'.join(filepath)

        self.__filename = filepath.pop(-1)
        self.lock = THREADINGLOCK
        self.mkdir(filepath)

    ssl._create_default_https_context = ssl._create_unverified_context
    def run(self):
        fileurl = self.__filepath
        downurl = self.__downurl
        #print('downurl:',downurl)
        #print('filepat',fileurl)
        try:
            LOGGER.debug("start download page： {0}".format(downurl))
            LOGGER.debug("download path '{0}'".format(fileurl))
            urllib.request.urlretrieve(downurl,fileurl,self.schedule)
            #添加待解析页面到队列
            THREADINGLOCK.acquire()
            ANALY_QUEUE.put([self.headers,fileurl])
            THREADINGLOCK.release()
        except urllib.error.HTTPError as e:
            LOGGER.warn("url not download {0}".format(downurl))
            LOGGER.warn(e)
        except urllib.error.URLError:
            LOGGER.error("url open failed '{0}'".format(downurl))
            recodeExcept(*sys.exc_info())
            LOGGER.error(traceback.format_exc())
            LOGGER.error("Except EOF")
        except PermissionError:
            urlstrs = 'fileurl:'+fileurl+'  ,downurl:'+downurl
            LOGGER.warn(urlstrs+'(PermissionError)')
        except:
            LOGGER.error("url open failed '{0}'".format(downurl))
            recodeExcept(*sys.exc_info())
            LOGGER.error(traceback.format_exc())
            LOGGER.error("Except EOF")

    def schedule(self,blocknum,blocksize,totalsize):
        """
        blocknum:块个数
        blockszie:块大小
        totalszie:总大小
        """

        if totalsize == -1:
            totalsize = 1
            
        per = 100.0 * blocknum * blocksize/totalsize

        if per > 100:
                per = 100

        self.lock.acquire()
        #a=self.__filename+'blocknum'+str(blocknum)+'blocksize'+str(blocksize)+'totalsize'+str(totalsize)+'##'
        #print(a,end='\n')
        strs = '下载进度：'+self.__filename+'>>>>>>>> '+str(per)+'%'
        #sys.stdout.write(strs+'\n')
        #sys.stdout.flush()
        self.lock.release()

    def mkdir(self,dirs):

        tempdir = ''
        for d in dirs:
            if tempdir:
                tempdir = tempdir+'/'+d
            else:
                tempdir = d

            #print('dirs',tempdir)
            try:
                if not os.path.exists(tempdir):
                    #print(tempdir)
                    os.mkdir(tempdir)
            except NameError:
                print('Failded to create directory in %s'%dirs)
                exit()
