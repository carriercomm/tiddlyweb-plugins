# -*- coding: utf-8 -*-
__safe__ = ['tiddler','tags','view','tiddlers']
import re,urllib,logging
from tiddlywebplugins.wikklytextrender import wikitext_to_wikklyhtml
from wikklytext.base import Text
from tiddlyweb.model.bag import Bag
from tiddlywebplugins.utils import get_store
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.store import Store, NoBagError,NoTiddlerError
from tiddlywebplugins.wikklytextplugins.filterer import filter_tiddlers
from tiddlyweb import control
from tiddlyweb.web.util import encode_name
from datetime import date
from wikklytext.plugapi import SPAN, Text, eval_wiki_text
from wikklytext.base import Element
from tiddlyweb.config import config

def WikiArgument(val):
    arg1 = Element("text")
    arg1.text = val
    return arg1
    
def _throw_error():
    return "<span class='wikkly-error-container'>running old version of TiddlyWeb</span>"  
    
def tiddlers(context, *args):
    base = context.var_get_text("$BASE_URL")
    path = ""
    
    if not context.environ:
        return ""
    else:
      environ = context.environ
    
    store = get_store(config)
    
    tid = context.tiddler
    if tid.recipe:
        tids = control.get_tiddlers_from_recipe(store.get(Recipe(tid.recipe)))
    elif tid.bag:
        bag = store.get(Bag(tid.bag))
        tids = list(bag.list_tiddlers())
    else:
        return u""
    
    tiddlerTemplate = args[0].text
    templateText = ""  
    for tid in tids:
        tid = store.get(tid)
        if tid.title == tiddlerTemplate:
            templateText = tid.text
    p = parseParams(args)
    if "filter" in p:
        filterBag = Bag("filter",tmpbag=True)
        filterBag.add_tiddlers(tids)
        filtered_tiddlers = filter_tiddlers(filterBag,p["filter"])
        output = u""
        for filtered_tiddler in filtered_tiddlers:
            output += u"%s"%wikitext_to_wikklyhtml(base,path, templateText, environ,tiddler=filtered_tiddler)
        return "<html>%s</html>"%output
    else:
        return u""
      
def tiddler(context, *args):
    base = context.var_get_text("$BASE_URL")
    path =""
    if not context.environ:
      return ""
    
    store = get_store(config)
    logging.debug("in tiddler macro")
    try:
        environ = context.environ
    except NoAttributeError:
        return _throw_error()
    try:
        tid = context.tiddler
    except NoAttributeError:
        return ""
    if tid.recipe:
        tids = control.get_tiddlers_from_recipe(store.get(Recipe(tid.recipe)))
    elif tid.bag:
        bag = store.get(Bag(tid.bag))
        tids = bag.list_tiddlers()
    else:
        return ""
    try:
        tiddler_requested = args[0].text
        for tiddler in tids:
            if tiddler.title == tiddler_requested:
                tiddler = store.get(tiddler)
    except Exception:
        tiddler = context.tiddler
    if tiddler:
        text = wikitext_to_wikklyhtml(base,path, tiddler.text, environ,tiddler=context.tiddler)
        return "%s"%text
    else:
        return ""#no tiddler with that name

def parseParams(params):
    newargs = []
    named = {}
    for i in params:
        newargs.append(i.text)    
    matchWithPrevious = False
    for p in newargs:
        try:
            i = p.index(":") #see if colon present
            matchWithPrevious = False #we have a colon present
            name = p[:i]#name is everything up to
            val = p[i+1:]
            
            if len(val) == 0:
                matchWithPrevious = name
            if name in named:
                existing = named[name]
                if type(existing) == type([]):          
                    named[name].append(val)
                else:      
                    named[name] = [existing,val]
            else:
                named[name]=val
        except ValueError:
            if matchWithPrevious:
                named[matchWithPrevious] =p
                matchWithPrevious = False
            pass
    return named
    
def _do_transclusion(str,tiddler):
    if not tiddler:
        return str
    else:
        def matcher(match):
            field = match.group(0)[1:]
            try:
                val= getattr(tiddler,field)
            except AttributeError:
                try:
                    val = tiddler.fields[field]
                except KeyError:
                    val = ""
            return val
        return re.sub("(\$.*)$|(\$[^ ]*) ",matcher,str)
    
def _view_transform(context,value,vtype,named_args={}):
    base = context.var_get_text("$BASE_URL")
    path =""
    environ = context.environ
    try:
        prefix = named_args["prefix"]
        prefix =_do_transclusion(prefix,context.tiddler)
    except KeyError:
        prefix = ""
    try:
        suffix =named_args["suffix"]
        suffix =_do_transclusion(suffix,context.tiddler)
    except KeyError:
        suffix = ""
    try:
        label = named_args["label"]
        label = _do_transclusion(label,context.tiddler)
    except KeyError:
        label = value
    #logging.debug("view_transform %s %s %s"%(value,vtype,params))
    if type(value) != type([]):
        values = [u"%s"%value] 
    else:
        values = []
        for val in value:
            if " " in val:
                values.append("[[%s]]"%val)
            else:
                values.append(val)
    out = ""
    for value in values:
        if not vtype or vtype =='text':
            transformed = value
            out += transformed
        elif vtype == 'wikified':
            out += wikitext_to_wikklyhtml(base,path, value, environ,wikiwords=False,tiddler=context.tiddler)
        elif vtype =='link':
            value = "[[%s]]"%(value)
            out += wikitext_to_wikklyhtml(base,path, value, environ,wikiwords=False,tiddler=context.tiddler)
        elif vtype=='date':
            YYYY = int(value[0:4])
            MM = int(value[4:6])
            DD = int(value[6:8])
            h = value[8:10]
            m = value[10:12]
            s = value[12:14]
            d = date(YYYY,MM,DD)
            out += d.strftime("%d %B %Y")
        elif vtype == 'linkexternal':
            out +=  u'<a href="%s%s%s">%s</a>'%(prefix,urllib.quote(value),suffix,label)
        else:
            logging.debug("unknown view type %s"%vtype)
        out += " "
    out = out[:-1]
    return out
    
def tags(context,*args):
    base = context.var_get_text("$BASE_URL")
    path =""
    try:
        tiddler = context.tiddler
    except NoAttributeError:
        return _throw_error()
    tagresult = "<ul>"
  
    if len(tiddler.tags) == 0:
        tagresult += "<li>no tags</li>"
    else:
        tagresult +=u"<li class=\"listTitle\">tags: </li>"
        for tag in tiddler.tags:
            taglink = "%s"%wikitext_to_wikklyhtml(base,path, "[[%s]]"%tag, context.environ,wikiwords=False,tiddler=context.tiddler)
            tagresult += "<li>%s</li>"%(taglink)
  
    tagresult += "</ul>"
    return "<html>%s</html>"%tagresult
  
def view(context, *args):
    params = []
    try:
        environ = context.environ
    except NoAttributeError:
        return _throw_error()
        
    for p in args:
        params.append(p.text)
    try:
        field = params[0]
    except IndexError:
        pass
    if field == 'server.bag':
        field = 'bag'
    elif field == 'server.page.revision':
        field = 'revision'
    try:
        viewtype = params[1]
    except IndexError:
        viewtype = False
    try:
        tiddler = context.tiddler
    except AttributeError:
        tiddler = False
    val = ""
    if tiddler and field:  
        if field in tiddler.fields:
            val = tiddler.fields[field]
        else:
            val = getattr(tiddler,field,"")
    #logging.debug("view lastnamed args %s"%params)
    p = params[2:]
    res = _view_transform(context,val,viewtype,named_args=parseParams(args))
    
  
    return u"<html>%s</html>"%res
    