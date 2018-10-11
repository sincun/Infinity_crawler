import random
import threading
import traceback
import multiprocessing
from multiprocessing import Manager
import acrawler
from splitcontent import *
from setting import *



ISALIVE = []
tlock = threading.Lock()
class multiProcessResultThread(threading.Thread):
	def __init__(self,processins):
		#threading.Thread.__init__(self)
		super(multiProcessResultThread,self).__init__()
		self.ins = processins
		self.result = ()

	def run(self):
		try:
			self.json_str,self.lablecount = self.ins.get(timeout=20)

			LOGGER.debug("analysis result {0}".format(self.result))
			#队列的添加移到解析文件的时候增加
			#tlock.acquire()
			#for perurl in result:
			#	DN_QUEUE.put(perurl)
			#tlock.release()

		except:
			recodeExcept(*sys.exc_info())
			LOGGER.error(traceback.format_exc())
			LOGGER.error("Except EOF")
		ISALIVE.remove(self)

	def getresult(self):
		return self.json_str,self.lablecount


class LaunchCapture(object):
	"""launching acrawler class"""
	def __init__(self):
		self.pool = multiprocessing.Pool(processes=4)

	def queueCallback(self):
		pass
	@staticmethod
	def dnPutCallback(queues):
		global DN_QUEUE
		#DN_QUEUE.put(queues)
		pass
#    @staticmethod
	def main(self,url=None):

		#analy_queue = ANALY_QUEUE
		#dn_queue = DN_QUEUE
		if url:
			DN_QUEUE.put(url)
		useUrl = DN_QUEUE.get(timeout=120)
		crawler = acrawler.crawler(statistics=0)
		try:
			downloadurlPro = multiprocessing.Process(target=crawler.analysis,args=(useUrl,DN_QUEUE,ANALY_QUEUE))
			downloadurlPro.start()
		except:
			LOGGER.warn("process start failed")
			recodeExcept(*sys.exc_info())
			LOGGER.error(traceback.format_exc())
			LOGGER.error("Except EOF")

		LOGGER.debug("start queue length {0},download process {1},status: {2}".format(DN_QUEUE.qsize(),downloadurlPro.pid,downloadurlPro.is_alive()))
		error_getcount = 0
		while ANALY_QUEUE.qsize() != 0 or downloadurlPro.is_alive() or ISALIVE:
			#you could rewirte analysisHandler method,if you need.‘analysisHandler' method is major handle web page.
			# get what you want,but must reutrn  a python "set()" which  name is referred to slef.webPage ,it's con-
			# tain web page from last analysis url."set()" will be as next url by analysis.
			#
			#ophref method function is downurl,and add set().

			try:
				analyUrl = ANALY_QUEUE.get(timeout=10)
			except:
				LOGGER.warn("fetch analysis queue timeout")
				recodeExcept(*sys.exc_info())
				LOGGER.error(traceback.format_exc())
				LOGGER.error("Except EOF")
				error_getcount += 1
				LOGGER.info("download process status {0}".format(downloadurlPro.is_alive()))
				LOGGER.error("get analysis queue count {0}".format(error_getcount))
				if error_getcount > 12 and not downloadurlPro.is_alive():
					LOGGER.info("exit url analysis")
					break
				continue
			splitcontent = splitContent(self.dnPutCallback)
			multprocessResult = self.pool.apply_async(splitcontent.pagesplit,args=(analyUrl,DN_QUEUE,))
			addQueue = multiProcessResultThread(multprocessResult)
			ISALIVE.append(addQueue)

			addQueue.start()
		LOGGER.info("will exit,waitting threading end!!!")
		addQueue.join()
		LOGGER.info("threading end!!!")
		self.pool.close()
		self.pool.join()
		downloadurlPro.join()


	def urlIsNone(self):
		"""generate a random url as initialization url"""

		pass

	def excuteAcrawler(self,url):
		"""if url is specified ,running it,use multiprocessing"""
		pass

if __name__ ==  '__main__':

	manage = Manager()
	DN_QUEUE = manage.Queue(500)
	ANALY_QUEUE = manage.Queue(500)
	url = 'https://blog.csdn.net/sicofield/article/details/8635351'
	launching = LaunchCapture()
	launching.main(url)