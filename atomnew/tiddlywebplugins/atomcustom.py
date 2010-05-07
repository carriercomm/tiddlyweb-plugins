"""
A New version of the atom TiddlyWeb serializer.
"""
from tiddlywebplugins.simplerizer import Simplerization as SerializationInterface
__version__ = "0.1"
from tiddlyweb.store import Store, NoBagError,NoTiddlerError,NoRecipeError
from tiddlyweb.config import config
from tiddlywebplugins.utils import get_store
import cgi,logging,urllib,datetime
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.model.recipe import Recipe
from tiddlyweb import control
from tiddlywebplugins.wikklytextrender import wikitext_to_wikklyhtml
from tiddlyweb.web.util import encode_name
def init(config):
        # register serializer
        content_type = "application/atom+xml"#application/atom+xml
        config["extension_types"]["atom"] = content_type
        config["serializers"][content_type] = [__name__, "application/atom+xml; charset=UTF-8"]

class Serialization(SerializationInterface):
        def __init__(self,environ):
            if not environ:
                environ = {}
            if 'tiddlyweb.query' not in environ:
                environ['tiddlyweb.query'] = {}
            environ['tiddlyweb.query']['fat'] = 'y'
            self.environ=environ
            self._bag_perms_cache = {}
            self.ATOM_CONFIG_TITLE = u"AtomSettings"
            
        def load(self,tiddler,type=False):
            return tiddler
                
        def tiddler_dump(self,tiddler,baseurl,active_resource=False,atomconfig={}):
            output = u""
            quoteTitle = urllib.quote(tiddler["title"].encode("utf-8"))
            bagname = tiddler["bag"]
            logging.debug("atom-custom:: doing a tiddler dump with %s"%tiddler)
            if "excludeAtom" in tiddler["tags"]:
                return ""
            mappings = {}
            if atomconfig:    
                if bagname in atomconfig['bags']:
                    bagmappings = atomconfig['bags'][bagname]                
                    for mapping in bagmappings:
                        mappings[mapping] = bagmappings[mapping]
                if active_resource:
                    rtype,rname = active_resource.split("/")
                    if rtype == 'recipes':
                        if rname in atomconfig['recipes']:
                            for single_mapping in atomconfig['recipes'][rname]:
                                mappings[single_mapping] =atomconfig['recipes'][rname][single_mapping]

            serializer = self 
            logging.debug("atom-custom:: created mapping for tiddler %s \n\n atom-custom::as %s \n\n\n atom-custom::from config %s \n\n"%(tiddler,mappings,atomconfig))
            def mapper(atom_field_name,tiddler,default):
                logging.debug("atom-custom:: doing a mapping on field %s \n atom-custom::with tiddler %s \n atom-custom::and config %s"%(atom_field_name,tiddler,mappings))
                tid = Tiddler(tiddler['title'],tiddler['bag'])
                tid = serializer.as_tiddler(tid,tiddler)
                try:
                    tid.recipe = tiddler['recipe']
                except KeyError:
                    pass
                if atom_field_name in mappings:
                  val = mappings[atom_field_name]
                  if atom_field_name == 'link' or atom_field_name == 'id' and val.startswith("/"):
                    sh =config['server_host']
                    val = u"%s://%s%s"%(sh['scheme'],sh['host'],val)
                    wikified = "http://%s"%wikitext_to_wikklyhtml(baseurl, '', val[7:], self.environ,tiddler=tid,wikiwords=False)
                  else:
                    wikified = wikitext_to_wikklyhtml(baseurl, '', val, self.environ,tiddler=tid,wikiwords=False)
                  return cgi.escape(wikified).decode("utf-8")
                  
                else:
                  return default
            quoteBag = urllib.quote(bagname)
            url = "%s%s"%(baseurl,quoteTitle)
            mode =''
            id = mapper("id",tiddler,"%s/%s/%s"%(quoteBag,quoteTitle,tiddler['revision']))
            if 'modifier' in tiddler:
                modifier_string = u"<author><name>%s</name></author>"%mapper('author',tiddler,tiddler['modifier'])
            else:
                modifier_string = u"<author><name></name></author>"
            if "type" in tiddler:
                if tiddler["type"] != "None":
                    tidType = tiddler["type"]
                    mode = 'mode="base64" '
                else:
                    tidType = "html"
            else:
                tidType = "html"    
            if "text" in tiddler:
                content =cgi.escape(tiddler["text"])
                content = mapper('content',tiddler,content)
                #print content
                text =    u'<content %stype="%s">%s</content>'%(mode,tidType,content)
            else:
                text = u""
            if 'modified' in tiddler:
                mod = tiddler["modified"]
                mask = "200108150000000"
                if len(mod) < len(mask):
                    mod += mask[len(mod):]
                    date = '%s-%s-%sT%s:%s:%sZ'%(mod[0:4],mod[4:6],mod[6:8],mod[8:10],mod[10:12],mod[12:14])
            else:
                date = ''
            entry_title = mapper('title',tiddler,cgi.escape(tiddler["title"]))
            entry_url = mapper('link',tiddler,url)
            logging.debug("atomplus::entry %s, %s"%(entry_title,entry_url))
            output += u"""<entry>
	<title>%s</title>
	<id>%s</id>
	<link rel="alternate" type="text/html" href="%s"/>
	%s
	%s
	<updated>%s</updated>
"""%(entry_title,id,entry_url,text,modifier_string,date)
            for tag in tiddler["tags"]:
                output += u'''	<category term="%s"/>
'''%cgi.escape(tag)
            
            if "geo.long" in tiddler["fields"] and "geo.lat" in tiddler["fields"]:
                lat = tiddler["fields"]["geo.lat"]
                lon = tiddler["fields"]["geo.long"]
                output +=u"""	<georss:point>%s %s</georss:point>
	<geo:lat>%s</geo:lat>
	<geo:long>%s</geo:long>
"""%(lat,lon,lat,lon)
            output += '''
</entry>
'''
            return output



        def read_atom_settings(self,atom_setting_text,resource_uri=""):
            settings=    {"feed":{},"bags":{},"recipes":{}}
            setting_lines = atom_setting_text.split("\n")
            active_resource = False
            ignore_following = False
            for setting_line in setting_lines:
                setting_line = setting_line.lstrip("     ")
                if setting_line.startswith("!"):#bag definition
                    try:
                        resource_type,resource_name = setting_line[1:].split("/")
                        settings[resource_type][resource_name] = {}
                        active_resource= [resource_type,resource_name]
                        ignore_following = False
                    except ValueError:
                        ignore_following = True
                        active_resource = False
                        pass
                    
                if not ignore_following:
                    try:
                        name,val = setting_line.split(":")
                        name_resource_parent,name_resource_tag = name.split(".")
                        if name_resource_parent == 'feed':
                            if not active_resource or resource_uri == u"/".join(active_resource):
                                settings["feed"][name_resource_tag] = val  
                        elif active_resource and name_resource_parent == 'entry':
                            settings[active_resource[0]][active_resource[1]][name_resource_tag] = val
                    except ValueError:
                        pass
            return settings



        def get_atom_config(self,resource_type,resource_name):
            store = get_store(config)
            atomconfig = False
            if resource_type == 'bag':
                try:
                    atomconfig = store.get(Tiddler(self.ATOM_CONFIG_TITLE,resource_name))
                except NoTiddlerError,NoBagError:
                    pass
            elif resource_type == 'recipe':
                try:
                    tids = control.get_tiddlers_from_recipe(store.get(Recipe(resource_name)))
                    for tid in tids:
                        if tid.title == self.ATOM_CONFIG_TITLE:
                            atomconfig = store.get(tid)
                except NoRecipeError:
                  pass

            if atomconfig:
                settings = self.read_atom_settings(atomconfig.text,"%ss/%s"%(resource_type,resource_name))
            else:
                settings = {"feed":{},"bags":{}}
            return settings



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
                settings = self.get_atom_config(resource_type,resource_name)
                baseuri =    "%s://%s/%s"%(environ['tiddlyweb.config']['server_host']['scheme'],environ['tiddlyweb.config']['server_host']['host'],environ['tiddlyweb.config']['server_prefix'])
                
                feedsettings = settings['feed']
                if 'title' in feedsettings:
                    atom_title= feedsettings['title']
                else:
                    atom_title = u"tiddlers in %s %s"%(resource_type,resource_name)
                if 'link' in feedsettings:
                    atom_link= feedsettings['link']
                else:
                    atom_link = baseuri
                    if "SCRIPT_URI" in environ:
                        atom_link += environ['SCRIPT_URI']
                

                uri =self.environ['SCRIPT_URI']
                output ="""<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"
	xmlns:geo="http://www.w3.org/2003/01/geo/wgs84_pos#"
	xmlns:georss="http://www.georss.org/georss"
>
	<title>%s</title>
	<link rel="self" type="application/rss+xml" href="%s"/>
	<id>%s%s</id>
	<updated>%s</updated>
"""%(atom_title,atom_link,baseuri,uri,nowstr)
                resource_uri = u"%ss/%s"%(resource_type,resource_name)
                tiddlerbaseuri = u"%s/%s/tiddlers/"%(baseuri,resource_uri)
                if(type(obj) == type([])):
                    for tiddler in obj:
                        output += self.tiddler_dump(tiddler,tiddlerbaseuri,resource_uri,settings)
                else:
                    output += self.tiddler_dump(obj,tiddlerbaseuri,settings)
                    
                output += "</feed>"
                return output

