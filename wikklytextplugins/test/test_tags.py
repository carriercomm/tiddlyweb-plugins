from tiddlywebplugins import wikklytextplugins
from tiddlywebplugins.wikklytextplugins.plugins import macros
from tiddlyweb.config import config
from test_common import WikiArgument,WikiContext
from tiddlyweb.model.tiddler import Tiddler

def test_tags():
    tid = Tiddler("foo","bar")
    tid.tags = ['ab', 'cd','ef gh']
    env = {}
    out = macros.tags(WikiContext(tid,env))
    assert '</li>' in out
    assert 'ab</li>' in out
    assert 'cd</li>' in out
    assert '</ul>' in out