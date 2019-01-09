from elasticsearch import Elasticsearch
from datetime import datetime
from setting import *
import traceback
import json


class writeElasticsearch:

	def __init__(self,host,port):
		connect_str = [{"host": host,"port": port}]
		self.es = Elasticsearch(connect_str)
		self.doc_type = "webinfo_type"

	def writeES(self,doc):
		"""
		:return:
		"""

		ctime = datetime.now().strftime("%Y%m%d")
		index_name = "%s%s" %("webinfo_", ctime)
		if not self.es.indices.exists(index_name):
			with open("urlbase.map") as f:
				mapstr = f.read()
				maps = eval(mapstr)
			try:
				self.es.indices.create(index=index_name)
			except:
				LOGGER.error("index crate to failed!!")
				recodeExcept(*sys.exc_info())
				LOGGER.error(traceback.format_exc())
				LOGGER.error("Except EOF")
			LOGGER.info("create index {0}".format(index_name))
		LOGGER.info("be writing elasticsearch,index is {0}".format(index_name))
		try:
			self.es.index(index = index_name,doc_type = self.doc_type,body = doc)
		except:
			LOGGER.warn("write in elasticsearch  failed {0}".format(index_name))
			recodeExcept(*sys.exc_info())
			LOGGER.error(traceback.format_exc())
			LOGGER.error("Except EOF")

if __name__ == '__main__':
	with open("webpage/josnts") as f:
		content_str = f.read()
		json_str = json.dumps(eval(content_str), check_circular=False, indent=4)
		print(json_str)
		ws = writeElasticsearch('10.1.71.80',9200)
		ws.writeES(json_str)























