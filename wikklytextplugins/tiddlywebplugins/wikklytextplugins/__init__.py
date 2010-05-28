global config
from tiddlywebplugins.wikklytextrender import wikitext_to_wikklyhtml
import re

def applyHtmlMacros(environ,html,tiddler):
    twconfig =environ.get('tiddlyweb.config',{})
    base_url= "%s/"%twconfig.get('server_prefix', '')
    if tiddler.recipe:
        path_url = "recipes/%s/tiddlers"%(tiddler.recipe)
    else:
        path_url = "bags/%s/tiddlers"%(tiddler.bag)
        
    base_url= twconfig.get('wikklytextplugins.base_url',base_url)
    path_url= twconfig.get('wikklytextplugins.path_url',base_url)
    
    def matcher(g):
        macro = g.group(1)
        wikitext = u"<<%s>>"%macro
        splash = u"%s"%wikitext_to_wikklyhtml(base_url, path_url, wikitext, environ,wikiwords=False,tiddler=tiddler).decode('utf-8','ignore')
        
        splash= re.sub('\&lt\;','<',splash)
        splash = re.sub('\&gt\;','>',splash)
        result = u"%s%s"%(g.group(0),splash)
        return result
        
    html = re.sub("macro=[\"\']([^\"\']+)[\"\']([^\>]*\>)",matcher,html)
    return html
    
def init(config_in):
  import tiddlywebplugins.wikklytextplugins as w
  config = config_in
  path = w.__path__
  config['wikklytext.plugin-dir'] = ["%s/plugins"%path[0],"plugins"]
  #config['wikitext.plugin-dir'] = "plugins"