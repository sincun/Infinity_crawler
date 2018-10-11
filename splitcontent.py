import re
from setting import *
import traceback
import json
from queue import Queue


class splitContent():
	"""handler html text or analogous text content"""
	
	def __init__(self,queuefunc):
		# self.startSymbol = startSymbol
		# self.endSymbol  = endSymbol
		self.func = queuefunc
		self.stopCode = []
		self.scopeLable = ''
		self.dataContent = {}
		#标签中的属性
		self.singleAttribute = ''
		#存放标签列表，存放正在处理的标签，处理完成后从列表清除
		self.s_LableList = []
		self.htmlDict = {}
		#drop
		self.startParttern = re.compile(r'^\s*<(\w+)|>\s*<(\w+)')
		self.endParttern = re.compile(r'\s*(/\w*)>\s*$|\s*(/\w*)>\s*<')

		self.spaceParttern = re.compile(r'\s')
		self.endMarkParttern = re.compile(r'</(\w*)\s*>')
		# for fetcheLables
		self.s_LableParttern = re.compile(r'<(\w+)')
		#drop
		self.standardEndLableP = re.compile(r'/(\w*)\s*>')
		self.t_startLable = None
		self.t_endLable = None
		self.non_endLable = NON_ENDLABLE
		self.joinattr = []
		#判处处理的属性是注释或其他非标准内容
		self.extraAttrSign = False
		#注释
		self.annotation_lable = 0
		self.annotation_start = False
		#存放非标准内容
		self.extraAttr = ""
		# 统计处理标签个数
		self.lableCount = 0
		# 处理后标签数量
		self.lableAttrRecord = 0
		# 重复标签重命名
		self.globalKey = None

		#标签处理位置记录
		self.scriptlablestatus = "readly"
		#标签属性外的内容
		self.persingleAttribute = ''
		#结束标签获取
		self.nonspace = True
		#本地文件名
		self.Localurl = None

	def fetcheLables(self, line):
		"""

		:param line:
		:return:
		"""
		
		attribute_split = self.propertySplit(line)
		for atb in attribute_split:
			#
			LOGGER.debug("fetcheLables handler atb {0}".format(atb))
			t_attData = []
			if atb == '<':
				continue
			elif atb == '<!--':
				self.annotation_lable += 1
				self.extraAttr += atb
				continue
			elif atb == '-->' and self.annotation_lable:
				self.annotation_lable -= 1
				self.extraAttr += atb
				if not self.annotation_lable:
					t_attData = self.mapDict(self.extraAttr, keys="annotation")
					self.gen_ExpectionDict(t_attData)
					self.extraAttr = ""
				continue
			elif self.annotation_lable:
				self.extraAttr += atb
				continue
			elif atb == '>' or re.match(r'/\s*>',atb):
				
				try:
					# 处理没有结束标签的标签，在setting中设置
					if self.s_LableList and self.t_startLable.group(1) in self.non_endLable:
						self.s_LableList.pop()

					self.t_startLable = None

				except:
					LOGGER.error("delete Lable failed {0}".format(self.t_startLable))
					recodeExcept(*sys.exc_info())
					LOGGER.error(traceback.format_exc())
					LOGGER.error("Except EOF")
					#存在不标准内容或注释时处理，
					if self.extraAttrSign:
						LOGGER.error("write Lable extraAttr {0}".format(self.globalKey))
						t_attData = self.mapDict(self.extraAttr + atb, keys="extraAttr")
						self.gen_ExpectionDict(t_attData)
						self.lableAttrRecord += 1
						self.extraAttrSign = False
						self.extraAttr = ""
						self.annotation_lable = False
						continue
					elif self.annotation_lable:
						self.extraAttr += atb
						continue

					exit(100)
				continue
			# 存在起始标签,处理标签中属性
			if self.t_startLable:
				# Disassemble the content
				# return key,value
				t_attData = self.mapDict(atb)
				#处理非标准格式的html，同一个属性值被换行，进行组合
				if len(t_attData) == 2:
					if self.joinattr:
						self.gen_ExpectionDict(["non-key", self.joinattr])
						self.joinattr = []
					self.gen_ExpectionDict(t_attData)
					self.lableAttrRecord += 1
				else:
					self.joinattr.append(t_attData)
					if len(self.joinattr) == 3 and self.joinattr[1] == "=":
						self.gen_ExpectionDict([self.joinattr[0], self.joinattr[2]])
						self.joinattr = []
			else:
				# 判断是否是标签开始
				self.t_startLable = self.s_LableParttern.match(atb)
				if self.t_startLable:
					# 如果出现新的开始标签时，还存在注释，直接处理
					if self.extraAttrSign:
						LOGGER.error("correct write Lable extraAttr {0}".format(self.t_startLable))
						t_attData = self.mapDict(self.extraAttr + atb, keys="extraAttr")
						self.gen_ExpectionDict(t_attData)
						self.extraAttrSign = False
						self.extraAttr = ""
					self.s_LableList.append(self.t_startLable.group(1))
					self.lableCount += 1
					self.lableAttrRecord = 0
					self.globalKey = None
				else:
					self.t_endLable = self.endMarkParttern.match(atb)
					# 如果当前值带有结束标签
					if self.t_endLable:
						#
						# 标签是否结束
						endSymbol = self.t_endLable.group(1)
						if endSymbol:
							LOGGER.info("clear end lable {0},LableList is {1}".format(endSymbol, self.s_LableList))
							try:
								if endSymbol in self.s_LableList:
									while len(self.s_LableList) > 0:
										l_endSymbol = self.s_LableList.pop()
										if l_endSymbol == endSymbol:
											break
								else:
									LOGGER.warn("end tag is alone {0}".format(endSymbol))
								# 标签结束存在注释，重置标签属性计数
								self.lableAttrRecord = 0
								self.globalKey = None
							except:
								LOGGER.error("index is error '{0}'".format(endSymbol))
								recodeExcept(*sys.exc_info())
								LOGGER.error(traceback.format_exc())
								LOGGER.error("Except EOF")
						else:
							LOGGER.debug("clear end lable {0}".format(self.s_LableList))
							self.s_LableList.pop()
							self.lableAttrRecord = 0
							self.globalKey = None
					else:

						#self.extraAttrSign = True
						#self.extraAttr += repr(atb)
						
						#    self.s_LableList.pop()
						t_attData = self.mapDict(atb, keys="values")
						self.gen_ExpectionDict(t_attData)
				# fetch values
	
	# ----------------------------
	#        if self.t_startLable:
	#           if len(self.t_startLable) == 1:
	#               startStandardLable = self.t_startLable[0]
	#               non_startStandardLable = self.t_startLable[1]
	#
	#        if self.t_endLable:
	#            if len(self.t_endLable) == 1:
	#                endStandardLable = self.t_endLable[0]
	#                non_endStandardLable = self.t_endLable[1]
	#
	#        if startStandardLable:
	#            if endStandardLable:
	#                attribute = startStandardLable.upper() + '_ATTRIBUTE'
	#                t_attribute = getattr(self, attribute, None)

	#当前路径转换为绝对路径
	def fullurl(self, link):
		#
		link = link.strip('"')
		if re.match(r'http', link):
			website = ""
		elif re.match(r'//', link):
			website = self.htmlpro
		else:
			website = self.htmlpro +"//" + self.sitename
		# print('handle',website,"link",link)
		return website + link

	def mapDict(self, attr, keys=None):
		#
		if keys:
			return [keys, attr]
		else:
			if re.match(r'"', attr):
				return attr
			t_attrList = attr.split('=', 1)
			if len(t_attrList) != 2:
				return attr
			try:
				t_attrList[1] = t_attrList[1].strip('"')
				t_attrList[1] = t_attrList[1].strip("'")
				if t_attrList[0] in DOWNLOAD_ATTRIBUTE:
					#补充为完整的url
					downurl = self.fullurl(t_attrList[1])
					LOGGER.info("put  download queue {0},filename {1}".format(downurl,self.Localurl))
					self.dn_queue.put(downurl)
					self.func(downurl)
			except:
				LOGGER.error("attribute is error '{0}'".format(t_attrList))
				recodeExcept(*sys.exc_info())
				LOGGER.error(traceback.format_exc())
				LOGGER.error("Except EOF")
			return t_attrList if t_attrList[1] else ['non-key', t_attrList[1]]
	
	def gen_ExpectionDict(self, kv_data):
		"""
		将获取的属性加入字典
		:param kv_data:
		:return:
		"""
		#
		LOGGER.debug("will write date {0}".format(kv_data))
		LOGGER.debug("s_LableList is{0}".format(self.s_LableList))
		LOGGER.debug("htmlData is {0}".format(self.htmlDict))
		desc_k = self.s_LableList.copy()
		
		while desc_k:
			if self.s_LableList:
				endkeys = desc_k[-1]
			else:
				pass
				exit(1)
			t_htmlDict = self.htmlDict
			# LOGGER.debug("handler after LableList {0}".format(desc_k))
			l_lenght = len(desc_k)
			l_number = 0
			for k in desc_k:
				l_number += 1
				if k in t_htmlDict.keys():
					if k == endkeys and l_number == l_lenght:
						if isinstance(kv_data, dict):
							t_htmlDict[k] = kv_data
						else:
							LOGGER.info('writing lable data {0} ,endkey {1}'.format(kv_data, endkeys))
							#处理重复标签名称，给每个标签加上编号
							if self.globalKey:
								k = self.globalKey
							LOGGER.debug("current t_htmlDict keys {0}".format(t_htmlDict.keys()))
							if self.lableAttrRecord == 0:
								k = k + repr(len(t_htmlDict.keys()))
								self.globalKey = k
								t_htmlDict[k] = {kv_data[0]: kv_data[1]}
							elif kv_data[0] in t_htmlDict[k].keys():
								kv_dataKey = kv_data[0] + repr(len(t_htmlDict[k].keys()))
								t_htmlDict[k][kv_dataKey] = kv_data[1]
							else:
								t_htmlDict[k][kv_data[0]] = kv_data[1]
							# kv_data = t_htmlDict
					else:
						t_htmlDict = t_htmlDict[k]
				elif k == endkeys:
					if isinstance(kv_data, dict):
						t_htmlDict[k] = kv_data
					else:
						t_htmlDict[k] = {kv_data[0]: kv_data[1]}
					# t_htmlDict[k] = {kv_data[0]:kv_data[1]}
				else:
					t_htmlDict = {}
					# continue
				# print("per key status result:{0},keylist:{1}".format(t_htmlDict, k))
			kv_data = t_htmlDict
			desc_k.pop()
		LOGGER.debug("kv_data is {0}".format(kv_data))
		if isinstance(kv_data,list):
			self.htmlDict = {kv_data[0]:kv_data[1]}
		elif isinstance(kv_data,dict):
			self.htmlDict = kv_data
	
	def standardContent(self, startLable, endLable, line):
		
		if endLable == '/':
			self.non_endMark(line, startLable)
		else:
			self.standardContentHandle(line, startLable)
	
	def non_endMark(self, line, startLable):
		pass
	
	def standardContentHandle(self, line, startLable):
		pass
	
	def propertySplit(self, line):
		"""
		解析html页面返还切割属性值生成器
		:param line:
		:return:
		"""
		
		for char in line:
			# LOGGER.debug("split char is {0} ,stopCode {1}".format(char,self.stopCode))
			# stopCode存放双引号个数，每出现两个双引号后重置stopCode，如果存在stopCode，说明关键属性在双引号中，则忽略
			# scopeLable等于">"说明一个标签的结束，可以返还获取到的内容了
			if  not self.stopCode and self.singleAttribute == '<!--':
				self.annotation_start = True
				if self.persingleAttribute.strip():
					diff = yield self.persingleAttribute
					self.persingleAttribute = ""
				diff = yield self.singleAttribute
				self.singleAttribute = ""
				self.singleAttribute += char
				continue
			elif self.annotation_start:
				self.singleAttribute += char
				annotation_content = self.singleAttribute[:-3]
				annotation_end = self.singleAttribute[-3:]
				if annotation_end == '-->':
					self.annotation_start = False
					diff = yield annotation_content
					annotation_content = ""
					diff = yield annotation_end
					annotation_end = ""
				continue

			if self.spaceParttern.match(char) and not self.stopCode and self.scopeLable != ">" and self.nonspace:
				# singleAttribute为获取的属性，为空则忽略
				if not self.singleAttribute:
					continue
				elif self.s_LableParttern.match(self.singleAttribute) and (self.scriptlablestatus == "readly" or self.scopeLable == '<'):
					self.scriptlablestatus = "mark"
					LOGGER.debug("return attribute content is {0}.".format(self.singleAttribute))
					if self.persingleAttribute.strip():
						diff = yield self.persingleAttribute
						self.persingleAttribute = ""
					diff = yield self.singleAttribute
				#处理标签中属性，如：<div class="mask-dark">中的class="mask-dark"
				elif self.scriptlablestatus == "mark":
					diff = yield self.singleAttribute
				else:
					self.persingleAttribute += self.singleAttribute
					self.scopeLable = ">"
				self.singleAttribute = ''
			else:
				#处理""中的内容不做拆分，stopCode为封闭符
				if (char == '"' or char == "'") and self.scopeLable != ">":
					if not self.stopCode:
						self.stopCode.append(char)
					elif char in self.stopCode:
						self.stopCode.pop(-1)
						self.singleAttribute += char
						diff = yield self.singleAttribute
						self.singleAttribute = ""
						continue

				elif char == "<" and not self.stopCode:
					# 处理特殊标签，如<em>
					if char == self.scopeLable:
						LOGGER.warn("line data style error!present line {0}.".format(line))
					else:
						LOGGER.debug("start Lable attribute {0}.".format(self.singleAttribute))
						# 打上标签状态"<",标签新的开始，返还之前获取属性
						self.scopeLable = char
						# 去除左右两端空格再判断
						#self.singleAttribute = self.singleAttribute.strip()
						self.persingleAttribute += self.singleAttribute
						#if self.singleAttribute and not self.spaceParttern.match(self.singleAttribute):
						#	LOGGER.debug("return start lable attribute is {0}.".format(self.singleAttribute))
						#	diff = yield self.singleAttribute
						#	self.singleAttribute = ''
						#else:
						#	LOGGER.info("LF and  attribute null will be ignore")
						self.singleAttribute = ''
				# 处理结束标签，处理跟结束符‘/’没有使用空格分隔的属性“rel=alternate/>”
				elif char == '/' and not self.stopCode and self.scopeLable != ">":
					LOGGER.debug("return attribute content is {0}.end char '/'".format(self.singleAttribute))
					if self.singleAttribute != '<':
						if self.singleAttribute:
							diff = yield self.singleAttribute
							self.singleAttribute = ''
					self.nonspace = False
				self.singleAttribute += char
				# print(self.singleAttribute)
				# 拆分结束标签跟结束符">"
				if not self.stopCode:
					atbendptn = self.endMarkParttern.match(self.singleAttribute)
					if atbendptn:
						LOGGER.debug("return stop lable attribute is {0}.".format(self.singleAttribute))

						if atbendptn.group(1) in self.s_LableList:
							self.scriptlablestatus = "readly"
							if self.persingleAttribute.strip():
								diff = yield self.persingleAttribute
							diff = yield self.singleAttribute
							self.scopeLable = '>'
							self.singleAttribute = ''
							self.persingleAttribute = ''
							self.nonspace = True
						else:
							self.scopeLable = '>'
					# 不标准结束符做拆分
					elif char == ">":
						if self.scopeLable == "<":
							self.scopeLable = '>'
							
							t_singleAttribute = self.singleAttribute[:-1].strip()
							if t_singleAttribute == "/"  and self.scriptlablestatus != "handling":
								LOGGER.debug("return before stop lable attribute is {0}.".format(self.singleAttribute))
								self.scriptlablestatus = "readly"
								diff = yield self.singleAttribute
								self.nonspace = True
								LOGGER.debug("return stop lable attribute is {0}.".format(self.singleAttribute))
							elif self.s_LableParttern.match(t_singleAttribute) or self.scriptlablestatus != "handling":
								if t_singleAttribute:
									diff = yield t_singleAttribute

								diff = yield char
								self.scriptlablestatus = "handling"
							self.singleAttribute = ""
						else:
							LOGGER.info("return style error attribute is {0}.".format(self.singleAttribute))
							#diff = yield self.singleAttribute
							LOGGER.info("date style error!date:{0}.".format(line))
						#self.singleAttribute = ''
	def pagesplit(self,anayurl,dn_queue):
		"""
		anayurl:/webpage/website/*
		:param anayurl:
		:return:
		"""

		self.htmlpro = anayurl[0]
		self.Localurl = anayurl[1]
		self.sitename = self.Localurl.split("/")[1]
		self.dn_queue = dn_queue
		LOGGER.info("start analysis url {0}".format(self.dn_queue))
		with open(self.Localurl,'r',encoding='UTF-8',errors='ignore') as f:
			for line in f.readlines():
				fetcheLable = self.fetcheLables(line)

			json_str = json.dumps(self.htmlDict,check_circular=False, indent=4)
			return json_str,self.lableCount

if __name__ == '__main__':
	line = 'webpage/blog.csdn.net/sicofield/article/details/8635351'
	line2 = 'webpage/blog.csdn.net/python_nice/article/details/81013267'
	line3 = 'C:/Users/belief/Desktop/Mr.S/GitHub/Infinity_crawler/webpage/aa'
	queue = Queue(1000)
	splitcontent = splitContent(lambda x:print("a"))
	itercontent,lablesnumber = splitcontent.pagesplit(['http',line2],queue)
	print(repr(lablesnumber)+":"+itercontent)

