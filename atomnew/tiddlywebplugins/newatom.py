"""
A New version of the atom TiddlyWeb serializer.
"""
from tiddlywebplugins.simplerizer import Simplerization as SerializationInterface
__version__ = "0.1"
from tiddlyweb.store import Store, NoBagError,NoTiddlerError
from tiddlyweb.config import config
from tiddlywebplugins.utils import get_store
import cgi
import urllib
import datetime

def init(config):
    # register serializer
    content_type = "application/atom+xml"#application/atom+xml
    config["extension_types"]["atom"] = content_type
    config["serializers"][content_type] = [__name__, "application/atom+xml; charset=UTF-8"]

class Serialization(SerializationInterface):
    def __init__(self,environ):
      if environ and 'tiddlyweb.query' not in environ:
        environ['tiddlyweb.query'] = {}
        environ['tiddlyweb.query']['fat'] = 'y'
      self.environ=environ
      self._bag_perms_cache = {}
    
    def tiddler_dump(self,tiddler,baseurl):
      output = u""
      url = "%s%s"%(baseurl,urllib.quote(tiddler["title"]))
      mode =''
      if 'modifier' in tiddler:
        modifier_string = u"<author><name>%s</name></author>"%tiddler['modifier']
      else:
        modifier_string = "<author><name></name></author>"
      if "type" in tiddler:
        if tiddler["type"] != "html":
          tidType = tiddler["type"]
          mode = 'mode="base64" '
        else:
          tidType = "html"
      else:
        tidType = "html"  
      if "text" in tiddler:
        text =  u'<content %stype="%s">%s</content>'%(mode,tidType,cgi.escape(tiddler["text"]))
      else:
        text = u""
      mod = tiddler["modified"]
      mask = "200108150000000"
      if len(mod) < len(mask):
        mod += mask[len(mod):]
      date = '%s-%s-%sT%s:%s:%sZ'%(mod[0:4],mod[4:6],mod[6:8],mod[8:10],mod[10:12],mod[12:14])
      output += u"""<entry>
	<title>%s</title>
	<id>%s</id>
	<link rel="alternate" type="text/html" href="%s"/>
	%s
	%s
	<updated>%s</updated>
  """%(cgi.escape(tiddler["title"]),url,url,text,modifier_string,date)
      for tag in tiddler["tags"]:
        output += u'''
        	<category term="%s"/>
        '''%cgi.escape(tag)
      
      if "geo.long" in tiddler["fields"] and "geo.lat" in tiddler["fields"]:
        lat = tiddler["fields"]["geo.lat"]
        lon = tiddler["fields"]["geo.long"]
        output +=u"""
	<georss:point>%s %s</georss:point>
	<geo:lat>%s</geo:lat>
	<geo:long>%s</geo:long>
"""%(lat,lon,lat,lon)
      output += u"</entry>"
      return output
      
    def dump(self, obj, otype):
        environ = self.environ
        now = datetime.datetime.now()
        nowstr = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        try:
          resource_name =urllib.quote(self.environ['selector.vars']['bag_name'])
          resource_type ="bag"
        except KeyError:
          resource_name =self.environ['selector.vars']['recipe_name']
          resource_type ="recipe"
        baseuri =  "%s://%s%s"%(environ['tiddlyweb.config']['server_host']['scheme'],environ['tiddlyweb.config']['server_host']['host'],environ['tiddlyweb.config']['server_prefix'])
        uri =self.environ['SCRIPT_URI']
        output ="""<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"
	xmlns:geo="http://www.w3.org/2003/01/geo/wgs84_pos#"
	xmlns:georss="http://www.georss.org/georss">
	<title>tiddlers in %s %s</title>
	<link rel="self" type="application/rss+xml" href="%s%s"/>
	<id>%s%s</id>
	<updated>%s</updated>
"""%(resource_type,resource_name,baseuri,uri,baseuri,uri,nowstr)
        
        tiddlerbaseuri = "%s/%ss/%s/tiddlers/"%(baseuri,resource_type,resource_name)
        if(type(obj) == type([])):
          for tiddler in obj:
            output += self.tiddler_dump(tiddler,tiddlerbaseuri)
        else:
          output += self.tiddler_dump(obj,tiddlerbaseuri)
          
        output += "</feed>"
        return output

