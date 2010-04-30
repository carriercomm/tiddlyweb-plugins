from tiddlywebplugins.newatom import Serialization as NewAtom
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.model.recipe import Recipe

def test_as_tiddler():
  tiddler = {"title":"foobar","fields":{},"text":"I like chicken.","tags":['chicken','food','love'],"modified":"20091225102030"}
  s = NewAtom({})
  text = s.tiddler_dump(tiddler,'http://jonrobson.me.uk/myfoo/')
  
  assert "<title>foobar</title>" in text
  assert '<content type="html">I like chicken.</content>' in text
  assert '<link rel="alternate" type="text/html" href="http://jonrobson.me.uk/myfoo/foobar"/>' in text
  assert '2009-12-25T10:20:30' in text
  assert '<category term="chicken"/>' in text
  
def test_as_tiddler_geo():
  tiddler = {"title":"London & Me","fields":{"geo.lat":"50","geo.long":"0.01"},"text":"The big smoke.","tags":[],"modified":"20021025102030"}
  s = NewAtom({})
  text = s.tiddler_dump(tiddler,'http://jonrobson.me.uk/myfoo/')
  
  assert "<title>London &amp; Me</title>" in text
  assert "<georss:point>50 0.01</georss:point>" in text
  assert "<geo:lat>50</geo:lat>" in text
  assert '<link rel="alternate" type="text/html" href="http://jonrobson.me.uk/myfoo/London%20%26%20Me"/>' in text
  assert "<geo:long>0.01</geo:long>" in text
  
def test_dump_singletiddler():
  tiddler = {"title":"jon","modifier":"jon","fields":{},"modified":"","text":"The big smoke.","tags":[]}
  s = NewAtom({'selector.vars':{'bag_name':'friends'},'SCRIPT_URI':'/feeds','tiddlyweb.config':{'server_prefix':'stuff','server_host':{'scheme':'http','host':'friends.com/'}}})
  text = s.dump(tiddler,'string')
  assert "<title>jon</title>" in text
  assert "<title>tiddlers in bag friends</title>"
  assert '<link rel="alternate" type="text/html" href="http://friends.com/stuff/bags/friends/tiddlers/jon"/>' in text
  assert '<link rel="self" type="application/rss+xml" href="http://friends.com/stuff/feeds"/>' in text
  assert "<author><name>jon</name></author>" in text

def test_binarytiddler():
  tiddler = {"type":"image/jpeg","text":"data","modified":"","title":"image","tags":[],"fields":{}}
  s = NewAtom({'selector.vars':{'bag_name':'friends'},'SCRIPT_URI':'/feeds','tiddlyweb.config':{'server_prefix':'stuff','server_host':{'scheme':'http','host':'friends.com/'}}})
  text = s.dump(tiddler,'string')
  assert '<content mode="base64" type="image/jpeg">data</content>' in text