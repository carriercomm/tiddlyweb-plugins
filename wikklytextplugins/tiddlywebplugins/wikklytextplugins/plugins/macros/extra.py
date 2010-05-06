def url(context,*args):
  
  try:
    url = context.environ['SCRIPT_URL']
  except KeyError:
    url = context.environ['REQUEST_URI']
  
  if len(args) > 0:
    if url[:1] == '/':
      url = url[1:]
    url_parts = url.split("/")
    where =args[0].text

    url=url_parts[int(where)]
  return urllib.unquote(url)
  
  
def tiddlyWebComments(context,*args):
    ctiddler = context.tiddler
    if ctiddler:
      comments = control.filter_tiddlers_from_bag(context.bag,"select=root:%s&sort=-created"%ctiddler.title)
      res = ""
      for comment in comments:
        res += "<div class='comment'><div class='heading'><div class='commentTitle'>comment</div></div><div class='commentText'>%s</div></div>"%comment.text
    return res
    
def message(context,*args):

  params = []
  for p in args:
    params.append(p.text)

  config_location = args[0].text
  try:
    viewtype = args[1].text
  except IndexError,KeyError:
    viewtype = ""

  logging.debug("in message macro %s show as %s"%(config_location,viewtype))
  logging.debug("msg macro %s"%config_location)
  if 'tiddlywebwiki_plus' in context.environ:
    twpctx = context.environ['tiddlywebwiki_plus']
    if "slices" in twpctx:
      slices = twpctx['slices']
      logging.debug("msg macro got slices")
      if "Config" in slices:
        val_location = slices["Config"]

        try:
          val = val_location[config_location]
        except KeyError:
          val = ""
        val = val.encode('utf-8')
        logging.debug("msg lastnamed args %s"%params)
        p = params[2:]
        logging.debug("lastnamed p has len %s"%len(p))
        return _view_transform(context,val,viewtype,p)
  return ""
  
global TIDDLER_MACRO
TIDDLER_MACRO = tiddler
def tiddlers(context, *args):
logging.debug("in tiddlers macro")
environ = context.environ
params = []
template = args[0]

named_args = parseParams(args)
tw_filter = named_args["filter"]
if context.bag:
  logging.debug("in tiddlers with tw filter %s"%(tw_filter))
  f = FilterThingy() #finding an old version of Filterer but not sure where!
  filtered_tiddler_list = f.get_filter_tiddlers(context.bag,tw_filter)
  logging.debug("in tiddlers with result %s"%filtered_tiddler_list)
  result = u""
  listlen = 0
  for newtiddler in filtered_tiddler_list:
    listlen +=1
    newcontext = context.clone()
    newcontext.environ = environ
    newcontext.tiddler = newtiddler
    newcontext.bag= context.bag
    tiddler_result = TIDDLER_MACRO(newcontext,template)
    result += tiddler_result    
  if listlen > 0:
    return result
  else:
    if "ifEmpty" in named_args:
      template_arg = Text(named_args["ifEmpty"])
      return TIDDLER_MACRO(context,template_arg)
    elif "ifEmptyString" in named_args:
      return named_args["ifEmptyString"]
    else:
      return ""
else:
  return "no bag"