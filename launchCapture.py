import random
import threading
import traceback
import multiprocessing
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

	def run(self):
		try:
			result = self.ins.get(timeout=10)

			LOGGER.debug("analysis result {0}".format(result))
			tlock.acquire()
			for perurl in result:
				DN_QUEUE.put(perurl)
			tlock.release()

		except:
			recodeExcept(*sys.exc_info())
			LOGGER.error(traceback.format_exc())
			LOGGER.error("Except EOF")
		ISALIVE.remove(self)

	def getresult(self):
		return DN_QUEUE


class LaunchCapture(object):
	"""launching acrawler class"""
	def __init__(self):
		self.pool = multiprocessing.Pool(processes=4)

#    @staticmethod
	def main(self,url=None):
		if url:
			DN_QUEUE.put(url)
		useUrl = DN_QUEUE.get(timeout=120)
		crawler = acrawler.crawler(statistics=3)
		downloadurlPro = multiprocessing.Process(crawler.analysis,target=(useUrl,))

		downloadurlPro.start()

		LOGGER.debug(DN_QUEUE.qsize())
		while ANALY_QUEUE.qsize() != 0 or downloadurlPro.is_alive() or ISALIVE:
			#you could rewirte analysisHandler method,if you need.‘analysisHandler' method is major handle web page.
			# get what you want,but must reutrn  a python "set()" which  name is referred to slef.webPage ,it's con-
			# tain web page from last analysis url."set()" will be as next url by analysis.
			#
			#ophref method function is downurl,and add set().
			splitcontent = splitContent()
			try:
				analyUrl = ANALY_QUEUE.get(timeout=120)
			except:
				LOGGER.warn("fetch Queue timeout")
				recodeExcept(*sys.exc_info())
				LOGGER.error(traceback.format_exc())
				LOGGER.error("Except EOF")
				continue

			multprocessResult = self.pool.apply_async(splitcontent.pagesplit,args=(analyUrl,))
			addQueue = multiProcessResultThread(multprocessResult)
			ISALIVE.append(addQueue)

			addQueue.start()
		addQueue.join()

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
	url = 'https://blog.csdn.net/sicofield/article/details/8635351'
	launching = LaunchCapture()
	launching.main(url)