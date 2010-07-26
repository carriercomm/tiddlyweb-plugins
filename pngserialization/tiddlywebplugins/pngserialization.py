"""
A svg to png TiddlyWeb Serializer
Requires ImageMagick!
Currently running the serializer on any tiddler will treat the source as svg, so will fail if not in svg format!
"""
from tiddlyweb.serializations import SerializationInterface
__version__ = "0.1"
from subprocess import call
import os
from tiddlyweb.web.validator import TIDDLER_VALIDATORS, InvalidTiddlerError

CACHE_LOCATION = "/tmp/tiddlyweb/svgtopng"
def init(config):
		# register serializer
		#content_type = "image/png"
		config["extension_types"]["png"] = "image/png+x"
		config["serializers"]["image/png+x"] = ['tiddlywebplugins.pngserialization', "image/png"]
		pass

class Serialization(SerializationInterface):
		def __init__(self,environ):
				self.environ=environ
		def tiddler_as(self, tiddler):
				path = "%s/%s/%s"%(CACHE_LOCATION,tiddler.bag, tiddler.title)
				pngPath = "%s.png"%path
				svgPath = "%s.svg"%path
				if not os.path.exists(svgPath):
						os.makedirs(path)
						f = open(svgPath, "wb")
						f.writelines(tiddler.text)
						f.close()
				if not os.path.exists(pngPath):
						call(['convert', svgPath, pngPath])
				try:
						f = open(pngPath, "rb")
						return f.readlines()
				except IOError:
						return ""

		def list_tiddlers(self, bag):
				return ""

		def list_recipes(self, recipes):
				return ""
		def list_bags(self, bags):
				return ""

def update_image_cache(tiddler, environ):
		path = "%s/%s/%s.png"%(CACHE_LOCATION, tiddler.bag, tiddler.title)
		svgPath = "%s.svg"%path
		pngPath = "%s.png"%path
		if ".." not in path:
			try:
				os.remove(svgPath)
			except OSError:
				pass
			try:
				os.remove(pngPath)
			except OSError:
				pass

TIDDLER_VALIDATORS.append(update_image_cache)
