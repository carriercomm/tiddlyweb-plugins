# coding=utf-8
from tiddlywebplugins.atomcustom import Serialization as NewAtom
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.config import config
from tiddlyweb.store import Store, NoBagError,NoTiddlerError
def setup_module(module):
  module.store = Store(config['server_store'][0], config['server_store'][1],environ={'tiddlyweb.config': config})
  module.environ = {'tiddlyweb.store':module.store,'tiddlyweb.config': config}

def clear_store():
  try:
    store.delete(Bag("notfoo"))
  except NoBagError:
    pass
  try:
    store.delete(Bag("foo"))
  except NoBagError:
    pass
  

def test_read_atomsettings():
  tid = {"bag":"notfoo","revision":1,"title":"AtomSettings","fields":{},"tags":['excludeAtom'],"text":'''!bags/foo
entry.title:<<echo title>>
entry.link:/posts/file.html
'''}
  s = NewAtom({})
  settings = s.read_atom_settings(tid['text'])
  print settings
  assert settings['feed'] == {}
  assert settings['bags']['foo']['title'] == u"<<echo title>>"
  assert settings['bags']['foo']['link'] == u"/posts/file.html"
  
  tid['text'] = '''feed.title:jon
!recipes/jon
feed.title:jon overridden

  !bags/bar
!bags/foo
feed.title:xyz
entry.title:x
entry.ignoreline;z
!badline
'''
  settings = s.read_atom_settings(tid['text'],"recipes/jon")
  assert settings['feed']['title'] == "jon overridden"  
  assert settings["bags"]["bar"] == {}
  assert settings["bags"]["foo"] == {u"title":u"x"}
  assert "ignoreline" not in settings["bags"]["foo"]
  
  
  settings = s.read_atom_settings(tid['text'],"recipes/ben")
  assert settings['feed']['title'] == "jon"
  
  tid['text'] = '''!notfoo
!bags/dumbar
entry.title:dumbar tiddler
!published_articles_en
entry.title:<<view heading>>
feed.title:broken title
entry.text:<<view summary>>  
!/bags/test
feed.title:wont work
'''
  settings = s.read_atom_settings(tid['text'],"recipes/ben")
  assert 'notfoo' not in settings['bags']
  assert 'test' not in settings['bags']
  assert settings['feed'] == {}
  assert settings['bags']['dumbar']['title'] == u"dumbar tiddler"
  
def test_with_customisations():
  clear_store()
  atoms = {"bag":"notfoo","revision":1,"title":"AtomSettings","fields":{},"tags":['excludeAtom'],"text":u'''!recipes/friends
feed.title:Jons Wacky Atom Feed
feed.link:http://tiddlyweb.com/foo

!bags/foo
entry.title:<<echo gtitle>>
entry.link:/posts/<<echo "file.html">>
entry.id:bar

!bags/pooh
entry.title:a tiddler from pooh
entry.content:winnie the pooh

!recipes/friends
entry.content:hello world content Cà Phê VN
'''}
  tid1 = {"bag":"foo","revision":1,"title":"Tiddler1","fields":{},"tags":[],"text":"Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."}
  tid2 = {"bag":"notfoo","revision":1,"title":"Tiddler2","fields":{},"tags":[],"text":"Magic"}
  tid3 = {"bag":"foo","revision":1,"title":"Tiddler3","fields":{},"tags":[],"text":"Hello"}
  tid4 = {"bag":"pooh","revision":1,"title":"Tigger","fields":{},"tags":[],"text":"Rabbit"} 
  store.put(Bag("notfoo"))
  store.put(Bag("foo"))
  r =Recipe("friends")
  r.set_recipe([['foo',''],['notfoo','']])
  store.put(r)
  atid =Tiddler(atoms['title'],atoms['bag'])
  atid.text = atoms['text']
  store.put(atid)
  newconfig = config
  newconfig['server_prefix']='stuff'
  newconfig['server_host']={'scheme':'http','host':'friends.com'}
  s = NewAtom({'tiddlyweb.store':store,'selector.vars':{'recipe_name':'friends'},'SCRIPT_URI':'/feeds','tiddlyweb.config':newconfig})
  text = s.dump([tid1,tid2,tid3,tid4,atoms],'list')
  
  print "#############"
  print text
  print "#############"
  assert '<title>Jons Wacky Atom Feed</title>' in text
  assert '<title>Tiddler2' in text
  assert '<link rel="alternate" type="text/html" href="http://friends.com/stuff/recipes/friends/tiddlers/Tiddler2"/>' in text
  assert '<title>gtitle</title>' in text
  assert '<link rel="alternate" type="text/html" href="http://friends.com/posts/file.html"/>' in text
  assert '<title>AtomSettings</title>' not in text
  assert u'hello world content Cà Phê VN' in text
  assert '<id>bar</id>' in text
  assert 'a tiddler from pooh</title>' in text
  assert 'Rabbit' not in text
  assert 'Tigger</title>' not in text
  assert 'winnie the pooh' not in text
  
  s.environ['selector.vars'] = {'bag_name':'notfoo'}
  newtext = s.dump([tid2,atoms],'list')
  assert 'hello world content' not in newtext

  

def test_as_tiddler():
  tiddler = {"bag":"bag","revision":1,"title":"foobar","fields":{},"text":"I like chicken.","tags":['chicken','food','love'],"modified":"20091225102030"}
  s = NewAtom({})
  text = s.tiddler_dump(tiddler,'http://jonrobson.me.uk/myfoo/')
  
  assert "<title>foobar</title>" in text
  assert '<content type="html">I like chicken.</content>' in text
  assert '<link rel="alternate" type="text/html" href="http://jonrobson.me.uk/myfoo/foobar"/>' in text
  assert '2009-12-25T10:20:30' in text
  assert '<category term="chicken"/>' in text
  
  tiddler['title']= u"Cà Phê VN"
  tiddler['tags'] = [u'à']
  tiddler['text']=  u"àààààà"
  text = s.tiddler_dump(tiddler,'http://jonrobson.me.uk/myfoo/')
  
def test_as_tiddler_geo():
  tiddler = {"bag":"geo","revision":2,"title":"London & Me","fields":{"geo.lat":"50","geo.long":"0.01"},"text":"The big smoke.","tags":[],"modified":"20021025102030"}
  s = NewAtom({})
  text = s.tiddler_dump(tiddler,'http://jonrobson.me.uk/myfoo/')

  assert "<title>London &amp; Me</title>" in text
  assert "<georss:point>50 0.01</georss:point>" in text
  assert "<geo:lat>50</geo:lat>" in text
  assert "<id>geo/London%20%26%20Me/2</id>" in text
  assert '<link rel="alternate" type="text/html" href="http://jonrobson.me.uk/myfoo/London%20%26%20Me"/>' in text
  assert "<geo:long>0.01</geo:long>" in text
  
def test_dump_singletiddler():
  tiddler = {"bag":"bag","revision":1,"title":"jon","modifier":"jon","fields":{},"modified":"","text":"The big smoke.","tags":[]}
  s = NewAtom({'selector.vars':{'bag_name':'friends'},'SCRIPT_URI':'/feeds','tiddlyweb.config':{'server_prefix':'stuff','server_host':{'scheme':'http','host':'friends.com'}}})
  text = s.dump(tiddler,'string')
  print text
  assert "<title>jon</title>" in text
  assert "<title>tiddlers in bag friends</title>"
  assert '<link rel="alternate" type="text/html" href="http://friends.com/stuff/bags/friends/tiddlers/jon"/>' in text
  assert '<link rel="self" type="application/rss+xml" href="http://friends.com/stuff/feeds"/>' in text
  assert "<author><name>jon</name></author>" in text

def test_binarytiddler():
  tiddler = {"bag":"bag","revision":1,"type":"image/jpeg","text":"data","modified":"","title":"image","tags":[],"fields":{}}
  s = NewAtom({'selector.vars':{'bag_name':'friends'},'SCRIPT_URI':'/feeds','tiddlyweb.config':{'server_prefix':'stuff','server_host':{'scheme':'http','host':'friends.com'}}})
  text = s.dump(tiddler,'string')
  assert '<content mode="base64" type="image/jpeg">data</content>' in text