import random
import threading
import traceback
from datetime import datetime
import multiprocessing
from multiprocessing import Manager
import acrawler
from splitcontent import *
from writeES import writeElasticsearch
from setting import *


ISALIVE = []
tlock = threading.Lock()
class multiProcessResultThread(threading.Thread):
	def __init__(self,processins,analyUrl):
		#threading.Thread.__init__(self)
		super(multiProcessResultThread,self).__init__()
		self.ins = processins
		self.handler_url = analyUrl
		self.result = ()

	def run(self):
		try:
			self.json_str,self.lablecount,self.localFilePath = self.ins.get(timeout=120)

			LOGGER.debug("analysis result {0}".format(self.result))
			#队列的添加移到解析文件的时候增加
			#tlock.acquire()
			#for perurl in result:
			#	DN_QUEUE.put(perurl)
			#tlock.release()

		except:
			LOGGER.error("url analysis timeout '{0}'".format(self.handler_url))
			recodeExcept(*sys.exc_info())
			LOGGER.error(traceback.format_exc())
			LOGGER.error("Except EOF")
		#ISALIVE.remove(self)

	def getresult(self):
		return self.json_str,self.lablecount,self.localFilePath


class LaunchCapture(object):
	"""launching acrawler class"""
	def __init__(self,writees = False):
		self.pool = multiprocessing.Pool(processes=4)
		self.is_write_es = writees

	def queueCallback(self):
		pass
	@staticmethod
	def dnPutCallback(queues):
		global DN_QUEUE
		#DN_QUEUE.put(queues)
		pass

	def getJson(self,processQueue):
		"""
		:param processQueue:
		:return:
		"""
		try:
			htmldict, lablecount, localUrlPath = processQueue.getresult()
			current_date = datetime.now()
			htmldict['timestamp'] = current_date.strftime("%Y-%m-%d %H:%M:%S")
			#htmldict['timestamp'] = datetime.now()
			htmldict['filepath'] = localUrlPath
			htmldict['statistics'] = lablecount
			json_str = json.dumps(htmldict, check_circular=False, indent=4)
			#json_str = htmldict
			# 生成es doc
			if self.is_write_es:
				LOGGER.debug(json_str)
				self.write_es.writeES(json_str)
				LOGGER.info("write success to elasticsearch")
			ISALIVE.remove(processQueue)
			LOGGER.info(json_str)
			LOGGER.info(lablecount)
			return json_str,lablecount, localUrlPath
		except:
			LOGGER.info("thread have not done to fetch result,continue wait")
			recodeExcept(*sys.exc_info())
			LOGGER.error(traceback.format_exc())
			LOGGER.error("Except EOF")
			return None

	def getAnalyResult(self):
		for processQueue in ISALIVE:
			self.getJson(processQueue)

#    @staticmethod
	def main(self,url=None):

		#analy_queue = ANALY_QUEUE
		#dn_queue = DN_QUEUE
		if self.is_write_es:
			self.write_es = writeElasticsearch('10.1.71.80',9200)
		if url:
			DN_QUEUE.put(url)
		useUrl = DN_QUEUE.get(timeout=120)
		#statistics: Download limit,0 is unlimited
		crawler = acrawler.crawler(statistics=STATISTICS)
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
		#multiProcessResultThread.setDaemon(True)
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
				self.getAnalyResult()
				continue
			splitcontent = splitContent(self.dnPutCallback)
			multprocessResult = self.pool.apply_async(splitcontent.pagesplit,args=(analyUrl,DN_QUEUE,))
			addQueue = multiProcessResultThread(multprocessResult,analyUrl)

			ISALIVE.append(addQueue)
			addQueue.start()
			self.getAnalyResult()

		LOGGER.info("will exit,waitting threading end!!! {0}".format(ISALIVE))
		if ISALIVE:
			for laterThread in ISALIVE:
				try:
					laterThread.join()
					json_str, *args = self.getJson(laterThread)
					LOGGER.info("thread out {0}".format(json_str))
				except:
					LOGGER.error("result is failed ,to review  analysis timeout url")
		LOGGER.info("threading end!!!")
		self.pool.close()
		self.pool.join()
		LOGGER.info("end!!!")
		#if downloadurlPro:
		#	downloadurlPro.join()


	def urlIsNone(self):
		"""generate a random url as initialization url"""

		pass

	def excuteAcrawler(self,url):
		"""if url is specified ,running it,use multiprocessing"""
		pass

if __name__ ==  '__main__':

	manage = Manager()
	#queue
	DN_QUEUE = manage.Queue(500)
	ANALY_QUEUE = manage.Queue(50000)
	#initial url
	url = INIT_URL
	launching = LaunchCapture(writees = WRITEES)
	launching.main(url)