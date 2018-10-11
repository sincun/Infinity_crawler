import random
import socket
import traceback
from socket import *
import urllib.request
import urllib.parse
import urllib.error
import http.cookiejar
import filedownload
from setting import *
from splitcontent import *


#
#
# author: Mr.S

class crawler(object):
	
	def __init__(self, statistics=0):

		self.sitearry = set()
		self.statistics = statistics
	
	# ***************************had been replace by buildOpenUrl*********************
	#socket connnects
	def buildsock(self):

		address = (self.host, self.port)
		LOGGER.debug(address)
		sock = socket()
		sock.settimeout(6)
		try:
			sock.connect(address)
		except:
			LOGGER.warn("acrawler url connnect timeout,{0}".format(address))
			recodeExcept(*sys.exc_info())
			LOGGER.error(traceback.format_exc())
			LOGGER.error("Except EOF")
			return None
		
		# request =  'GET {} HTTP/1.0\r\nHost:{}\r\n\r\n '.format(host,url)
		# User-Agent需要做成随机的防止封禁
		randomNum = random.randint(0, 9)
		userAgent = USER_AGENT[randomNum]
		request = 'GET {} HTTP/1.0\r\nHost:{}\r\n\r\n User-Agent:{}\r\n\r\n'.format(self.url, self.host, userAgent)
		try:
			sock.send(request.encode())
		except  Exception as e:
			LOGGER.error("url error or host is change or ", userAgent)
			LOGGER.error(e)
		
		data = self.foreach(sock)
		
		return data
	#Outdated methods，use socket fetch page data
	def foreach(self, sock):
		
		recvdata = b''
		chunk = sock.recv(4096)
		while True:
			if chunk:
				# print('chunk',chunk)
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
		# print('data',recvdata)
		try:
			recvdata = recvdata.decode()
		except UnicodeDecodeError as ude:
			LOGGER.error("Unicode Decode to utf8 Error,", ude)
			return None
		return recvdata
	
	##************************，above method will not by used************************
	def proxy_acs(self, proxy_addr=None, cookies=None):
		if proxy_addr:
			proxy = urllib.request.ProxyHandler({'http': proxy_addr})
			if cookies:
				cookjar = http.cookiejar.CookieJar()
				cookie = urllib.request.HTTPCookieProcessor(cookjar)
				opener = urllib.request.build_opener(proxy, urllib.request.HTTPHandler, cookie)
			else:
				opener = urllib.request.build_opener(proxy, urllib.request.HTTPHandler)
		elif cookies:
			cookjar = http.cookiejar.CookieJar()
			cookie = urllib.request.HTTPCookieProcessor(cookjar)
			opener = urllib.request.build_opener(cookie)
		else:
			return None
		urllib.request.install_opener(opener)
	#有cookies时使用
	def cookie_use(self):
		auth = {'username': 'zhangsan', 'password': '123456'}
		postdata = urllib.parse.urlencode(auth).encode()
		
		return postdata
	#构建urlopen，urlopen方式暂时未使用，目前直接下载页面到本地再解析
	def buildOpenUrl(self, url, proxy_addr=None, cookies=None, post=None):
		# User-Agent需要做成随机的防止封禁
		randomNum = random.randint(0, 9)
		header = {"User-Agent": USER_AGENT[randomNum]}
		
		self.proxy_acs(proxy_addr, cookies)
		if post:
			if isinstance(post, dict):
				post = urllib.parse.urlencode(post).encode()
				requests = urllib.request.Request(url, data=post, headers=header)
			else:
				LOGGER.warn("psot data format error '{0}'".format(post))
				requests = urllib.request.Request(url, headers=header)
		else:
			requests = urllib.request.Request(url, headers=header)
		try:
			response = urllib.request.urlopen(requests)
		except:
			LOGGER.error("urlopen error '{0}'".format(url))
			recodeExcept(*sys.exc_info())
			LOGGER.error(traceback.format_exc())
			LOGGER.error("Except EOF")
		
		return requests

	#当前路径转换为绝对路径
	def fullurl(self, link):
		#
		link = link.strip('"')
		if re.match(r'http', link):
			website = ""
		elif re.match(r'//', link):
			website = self.heads
		else:
			website = self.website
		# print('handle',website,"link",link)
		return website + link

	# */
	# analysis url
	def analysis(self,dnurl,downqueue,analyqueue):
		"""

		:param dnurl:
		:return:
		"""
		#限制和记录下载解析多少个页面
		urlnum = 0
		threadlist = []
		fetchsuffix = re.compile(r'\S+\.(\w+)$')
		error_getcount = 0

		while True:

			if isinstance(dnurl,list) and dnurl:
				currenturl = dnurl.pop()
			elif dnurl:
				currenturl = dnurl
				dnurl = None
			#如果都不存在url了，可以在这里加入随机生成url的代码
			else:
				try:
					currenturl = downqueue.get(10)
				except:
					LOGGER.warn("fetch download queue timeout")
					recodeExcept(*sys.exc_info())
					LOGGER.error(traceback.format_exc())
					LOGGER.error("Except EOF")
					error_getcount += 1
					LOGGER.error("get download queue count {0}".format(error_getcount))
					if error_getcount > 3:
						break
					continue

			access_url = re.sub(r'(#.*$)', '', currenturl)

			if re.search(r'javascript:',currenturl):
				continue
			if currenturl in self.sitearry:
				continue
			#如果url之前已经解析则跳过
			if access_url in USEURL:
				continue
			USEURL.add(access_url)
			analyhtml = True
			path = self.fetchfileurl('webpage', currenturl)
			pagename = path[-1]
			matchsuffix = fetchsuffix.search(pagename)
			pagesuffix = pagename
			if matchsuffix:
				pagesuffix = matchsuffix.group(1)
			if pagesuffix in STATICPAGE:
				dynamichtml = False
			elif pagesuffix in DYNAMICPAGE:
				dynamichtml = True
			elif pagesuffix == pagename:
				dynamichtml = False
			else:
				analyhtml = False

			requests = self.buildOpenUrl(currenturl,proxy_addr=None, cookies=None, post=None)
			download = filedownload.fileDownload(currenturl,requests, path,dynamic=dynamichtml,handler=analyhtml,addanalyqueue=analyqueue)
			download.start()
			threadlist.append(download)

			self.sitearry.add(access_url)
			urlnum += 1
			if urlnum == self.statistics:
				LOGGER.warn("download url  finsh,process exit")
				LOGGER.debug("complate download url list (0)".format(self.sitearry))
				break
		for t in threadlist:
				t.join()

	
	# --根据不同类型建立进程池，在进程池中分别建立多线程处理每种结果类型--
	
	def fetchfileurl(self, types, mkpath):
		
		partern = PARTERN
		protocol = re.compile(r'http[s]?://(.*)')
		
		# 判断路径是否带有协议标识，有就去掉(https://)
		ifFullurl = protocol.match(mkpath)
		if ifFullurl:
			mkpath = ifFullurl.group(1)
		
		fullfilepath = [types]
		
		filename = mkpath.split('/')
		for p in filename[:-1]:
			# print(p)
			if p:
				if p == '.' or p == '/':
					continue
				elif p == '..':
					if fullfilepath and len(fullfilepath) > 1:
						fullfilepath.pop(-1)
					else:
						fullfilepath.append(p)
				else:
					fullfilepath.append(p)
			else:
				continue
		# print('1111111111',filename[-1])
		fullfilepath.append(partern.match(filename[-1]).group(1))
		
		# print(fullfilepath)
		return fullfilepath
	
	# 启动一个新的线程或进程继续解析连接
	def ophref(self, href, pagetype=None):
		
		fetchsuffix = re.compile(r'\S+\.(\w+)$')
		fullhref = self.fullurl(href)
		try:
			if fullhref in self.sitearry:
				return 1
			else:
				self.sitearry.add(fullhref)
			
			LOGGER.debug('page href link,will download:{0}'.format(href))
			path = self.fetchfileurl('webpage', href)
			
			# print('path',path)
			pagename = path[-1]
			matchsuffix = fetchsuffix.search(pagename)
			download = filedownload.fileDownload(fullhref, path)
			download.start()
			
			pagesuffix = pagename
			if matchsuffix:
				pagesuffix = matchsuffix.group(1)
			LOGGER.debug("page suffix is '{0}'".format(pagesuffix))
			
			suffixname = EXCLUDEPAGE
			if pagesuffix not in suffixname and pagetype != 1:
				LOGGER.debug("add queue url '{0}' for next crawler page".format(fullhref))
				self.webPage.add(fullhref)
		# self.analysis(fullhref)
		# pass
		
		except TypeError as e:
			LOGGER.error("url is error", href)
			LOGGER.error(e)
		return 0


	def mkdir(self, dirs):
		
		try:
			if not os.path.exists(dirs):
				os.mkdir(dirs)
		except:
			print('Failded to create directory in %s' % dirs)
			exit(1)
	
	def analysistest(self, target):
		
		with open(target, 'r', encoding='utf-8') as f:
			content = f.read()
		# print(content)
		
		self.analysis(content)
		if f:
			f.close()
		
		return content


if __name__ == '__main__':
	url = 'https://blog.csdn.net/sicofield/article/details/8635351'
	# url = 'http://www.google.com'
	crawler = crawler(url)
	r = crawler.analysis()
	print(r)
