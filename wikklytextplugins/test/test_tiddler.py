from tiddlywebplugins import wikklytextplugins
from tiddlywebplugins.wikklytextplugins.plugins import macros
from tiddlyweb.config import config
from test_common import WikiArgument,WikiContext
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.config import config
from tiddlyweb.store import Store, NoBagError,NoTiddlerError

def setup_module(module):
    module.store = Store(config['server_store'][0], config['server_store'][1],environ={'tiddlyweb.config': config})
    module.environ = {'tiddlyweb.store':module.store,'tiddlyweb.config': config}

def test_tiddler():
    #setup
    wikklytextplugins.init({})
    store.put(Bag("bar"))
    store.put(Bag("foo"))
    
    recipe = Recipe("foo")
    recipe.set_recipe([['foo',''],['bar','']])
    store.put(recipe)
    
    tid = Tiddler("jon robson","bar")
    tid.text = "My name is Jon Robson"
    store.put(tid)
    tid = Tiddler("a tiddler in foo","foo")
    tid.text = "rainbow [[title]]"
    store.put(tid)
    
    tid = Tiddler("foo","bar")
    tid.tags = ['ab', 'cd','ef gh']
    #run and verify
    out = macros.tiddler(WikiContext(tid,config),WikiArgument("jon robson"))
    assert 'My name is Jon Robson' in out
    
    out = macros.tiddler(WikiContext(tid,config),WikiArgument("a tiddler in foo"))
    assert out == "" #we are viewing from bag bar not foo.
    
    
    tid.recipe = "foo"
    out = macros.tiddler(WikiContext(tid,config),WikiArgument("a tiddler in foo"))
    assert "rainbow" in out #we are viewing from recipe now
    assert "title</a>" in out
    
    #teardown
    store.delete(Bag("foo"))
    store.delete(Bag("bar"))
    store.delete(Recipe("foo"))