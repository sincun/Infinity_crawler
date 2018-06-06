import random
import threading
import multiprocessing
from queue import Queue
import acrawler
from setting import *



urlQueue = Queue(500)
ISALIVE = []
tlock = threading.Lock()
class multiprocessresult(threading.Thread):
    def __init__(self,processins):
        #threading.Thread.__init__(self)
        super(multiprocessresult,self).__init__()
        self.ins = processins

    def run(self):
        result = self.ins.get(timeout=10)

        LOGGER.debug("analysis result {0}".format(result))
        tlock.acquire()
        for perurl in result:
            urlQueue.put(perurl)
        tlock.release()
        ISALIVE.remove(self)

    def getresult(self):
        return urlQueue


class LaunchCapture(object):
    """launching acrawler class"""
    def __init__(self):
        self.pool = multiprocessing.Pool(processes=4)

#    @staticmethod
    def main(self,url=None):
        if url:
            urlQueue.put(url)

        LOGGER.debug(urlQueue.qsize())
        while urlQueue.qsize() != 0 or ISALIVE:
            useUrl = urlQueue.get(timeout=10)
            crawler = acrawler.crawler(useUrl)
            multprocessResult = self.pool.apply_async(crawler.analysis)
            addQueue = multiprocessresult(multprocessResult)
            ISALIVE.append(addQueue)
            addQueue.start()
            addQueue.join()

        self.pool.close()
        self.pool.join()

    def urlIsNone(self):
        """generate a random url as initialization url"""

        pass

    def excuteAcrawler(self,url):
        """if url is specified ,running it,use multiprocessing"""
        pass

if __name__ ==  '__main__':
    url = 'http://www.bwlc.gov.cn/datacenter/ssq/jbzs_sanf.html?id=2'
    launching = LaunchCapture()
    launching.main(url)