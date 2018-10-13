import os
import ssl
import urllib
import traceback
from setting import *
from urllib import request
#from urllib.request import urlopen


class fileDownload(threading.Thread):

    def __init__(self,url,requests,filepath,dynamic=False,handler=True,addanalyqueue=None):
        
        threading.Thread.__init__(self)
        self.requests = requests
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

        if addanalyqueue:
            self.addanalyqueue = addanalyqueue
        else:
            LOGGER.error("argment error,accept object must be queue")
            sys.exit(99)

        self.__dynamic_page = dynamic
        self.__handler_flag = handler
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
            #urllib.request.urlretrieve(downurl,fileurl,self.schedule)
            self.urlretrieve(downurl, self.requests, fileurl, self.schedule)
            #添加待解析页面到队列
            if self.__handler_flag:
                #THREADINGLOCK.acquire()
                LOGGER.info("put analysis queue {0}".format(fileurl))
                self.addanalyqueue.put([self.headers,fileurl])
                #THREADINGLOCK.release()
            LOGGER.debug("url {0} dwonload complate!,queue length {1}".format(downurl,self.addanalyqueue.qsize()))
        except urllib.error.HTTPError as e:
            FAILED_URL.add(downurl)
            LOGGER.warn("url not download {0}".format(downurl))
            LOGGER.warn(e)
        except urllib.error.URLError:
            FAILED_URL.add(downurl)
            LOGGER.error("url open failed '{0}'".format(downurl))
            LOGGER.info("url open failed list  '{0}'".format(FAILED_URL))
            recodeExcept(*sys.exc_info())
            LOGGER.error(traceback.format_exc())
            LOGGER.error("Except EOF")
        except PermissionError:
            FAILED_URL.add(downurl)
            urlstrs = 'fileurl:'+fileurl+'  ,downurl:'+downurl
            LOGGER.warn(urlstrs+'(PermissionError)')
        except:
            LOGGER.error("url open failed '{0}'".format(downurl))
            LOGGER.info("url open failed list  '{0}'".format(FAILED_URL))
            FAILED_URL.add(downurl)
            recodeExcept(*sys.exc_info())
            LOGGER.error(traceback.format_exc())
            LOGGER.error("Except EOF")
    #重写urlretrieve，添加接受requests对象
    def urlretrieve(self,url,requests, filename=None, reporthook=None, data=None):
        """
        Retrieve a URL into a temporary location on disk.

        Requires a URL argument. If a filename is passed, it is used as
        the temporary file location. The reporthook argument should be
        a callable that accepts a block number, a read size, and the
        total file size of the URL target. The data argument should be
        valid URL encoded data.

        If a filename is passed and the URL points to a local resource,
        the result is a copy from local file to new file.

        Returns a tuple containing the path to the newly created
        data file as well as the resulting HTTPMessage object.
        """
        url_type, path = urllib.request.splittype(url)

        with urllib.request.contextlib.closing(urllib.request.urlopen(requests, data)) as fp:
            headers = fp.info()

            # Just return the local path and the "headers" for file://
            # URLs. No sense in performing a copy unless requested.
            if url_type == "file" and not filename:
                return os.path.normpath(path), headers

            # Handle temporary file setup.
            if filename:
                tfp = open(filename, 'wb')
            else:
                tfp = urllib.request.tempfile.NamedTemporaryFile(delete=False)
                filename = tfp.name
                urllib.request._url_tempfiles.append(filename)

            with tfp:
                result = filename, headers
                bs = 1024 * 8
                size = -1
                read = 0
                blocknum = 0
                if "content-length" in headers:
                    size = int(headers["Content-Length"])

                if reporthook:
                    reporthook(blocknum, bs, size)

                while True:
                    block = fp.read(bs)
                    if not block:
                        break
                    read += len(block)
                    tfp.write(block)
                    blocknum += 1
                    if reporthook:
                        reporthook(blocknum, bs, size)

        if size >= 0 and read < size:
            raise urllib.request.ContentTooShortError(
                "retrieval incomplete: got only %i out of %i bytes"
                % (read, size), result)

        return result

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
                if not os.path.isdir(tempdir):
                    #print(tempdir)
                    os.mkdir(tempdir)
            except NameError:
                LOGGER.error('Failded to create directory in %s'%dirs)
                exit()
            except:
                LOGGER.error("Failded to create directory in '{0}'".format(self.__downurl))
                recodeExcept(*sys.exc_info())
                LOGGER.error(traceback.format_exc())
                LOGGER.error("Except EOF")