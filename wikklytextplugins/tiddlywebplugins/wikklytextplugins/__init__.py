global config

def init(config_in):
  import tiddlywebplugins.wikklytextplugins as w
  config = config_in
  path = w.__path__
  config['wikklytext.plugin-dir'] = ["%s/plugins"%path[0],"plugins"]
  #config['wikitext.plugin-dir'] = "plugins"