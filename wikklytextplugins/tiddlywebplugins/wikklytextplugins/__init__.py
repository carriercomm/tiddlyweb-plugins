global config

'''
START overriding
This should be implemented in the core
'''
import wikklytext
import urllib
from tiddlyweb.web.util import encode_name
from tiddlywebplugins import wikklytextrender
def new_render(tiddler, environ):
    """
    Render TiddlyWiki wikitext in the provided
    tiddler to HTML. The provided path helps
    set paths in wikilinks correctly.
    """
    server_prefix = environ.get('tiddlyweb.config',
            {}).get('server_prefix', '')
    if tiddler.recipe:
        path = 'recipes/%s/tiddlers' % encode_name(tiddler.recipe)
    elif tiddler.bag:
        path = 'bags/%s/tiddlers' % encode_name(tiddler.bag)
    else:
        path = ''
    html = new_wikitext_to_wikklyhtml('%s/' % server_prefix,
            path, tiddler.text, environ,tiddler=tiddler,bag=tiddler.bag)
    return unicode(html, 'utf-8')


def new_wikitext_to_wikklyhtml(base_url, path_url, wikitext, environ,tiddler=False,bag=False,wikiwords=False):
    """
    Turn a wikitext into HTML.
    base_url: starting url for links in the wikitext (e.g. '/')
    path_url: path from base to wikitext (e.g. 'recipes/foorecipe/tiddlers')
    """

    def our_resolver(url_fragment, base_url, site_url):
        """
        Turn url information for a wikiword into a link.
        """
        if '://' in url_fragment or url_fragment.startswith('/'):
            return url_fragment, True
        return '%s%s' % (base_url, urllib.quote(url_fragment, safe='')), False

    posthook = wikklytextrender.PostHook()

    safe_mode_setting = environ.get('tiddlyweb.config', {}).get(
            'wikklytext.safe_mode', True)

    link_context = {
            '$BASE_URL': '%s%s' % (base_url, path_url),
            '$REFLOW': 0}
    plugindir = environ.get('tiddlyweb.config', {}).get('wikklytext.plugin-dir','')
    try:
        context = wikklytext.WikContext(plugin_dirs=plugindir,url_resolver=our_resolver)
        context.environ = environ
        context.bag = bag
        context.tiddler = tiddler
        context.wikiwords = wikiwords
        html,newcontext = wikklytext.WikklyText_to_InnerHTML(
                text=wikitext,
                context = context,
                plugin_dirs=plugindir,
                setvars=link_context,
                encoding='utf-8',
                safe_mode=safe_mode_setting,
                url_resolver=our_resolver,
                tree_posthook=posthook.treehook)
    except wikklytext.WikError, exc:
        html = '<pre>Unable to render wikitext: %s</pre>' % exc
    
    return html
wikklytext.render = new_render
wikklytext.wikitext_to_wikklyhtml = new_wikitext_to_wikklyhtml
'''
finish overriding
'''
def init(config_in):
  import tiddlywebplugins.wikklytextplugins as w
  config = config_in
  path = w.__path__
  config['wikklytext.plugin-dir'] = ["%s/plugins"%path[0],"plugins"]
  #config['wikitext.plugin-dir'] = "plugins"