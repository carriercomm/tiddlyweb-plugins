from tiddlywebplugins.wikklytextplugins.plugins import macros
from tiddlyweb.model.tiddler import Tiddler
from tiddlywebplugins import wikklytextplugins
from tiddlyweb.config import config
from test_common import WikiArgument,WikiContext

test_tiddler=  Tiddler("Test Tiddler","bag")
test_tiddler.modified = "20071003201000"
test_tiddler.revision = 2

def test_view_date():
    out = macros.view(WikiContext(test_tiddler,{}), WikiArgument("modified"),WikiArgument("date"))
    assert '03 October 2007' == out
    
def test_view_text():
    text ="My name is the test tiddler!"
    test_tiddler.text = text
    test_tiddler.tags = ["jon","ben","jeremy ruston"]
    out = macros.view(WikiContext(test_tiddler,{}), WikiArgument("text"))
    assert text in out
    out = macros.view(WikiContext(test_tiddler,{}), WikiArgument("text"),WikiArgument("text"))
    assert text in out
    out = macros.view(WikiContext(test_tiddler,{}), WikiArgument("title"),WikiArgument("text"))
    assert 'Test Tiddler' in out
    
    out = macros.view(WikiContext(test_tiddler,{}), WikiArgument("server.bag"),WikiArgument("text"))
    assert out == 'bag'
    
    out = macros.view(WikiContext(test_tiddler,{}), WikiArgument("server.page.revision"),WikiArgument("text"))
    assert out == '2'
    
    out = macros.view(WikiContext(test_tiddler,{}), WikiArgument("tags"),WikiArgument("text"))
    assert out == 'jon ben [[jeremy ruston]]'
    
    
def test_view_wikified():
    wikklytextplugins.init(config)
    text ="''testing bold''"
    test_tiddler.fields['foo'] = 'ok computer'
    test_tiddler.text = text
    out = macros.view(WikiContext(test_tiddler,{}), WikiArgument("text"), WikiArgument("wikified"))
    assert '</b>' in out
    assert 'testing bold' in out
    
    test_tiddler.text = "<<view foo text>>"
    '''following test needs a working wikklytext/up to date tiddlyweb'''
    #out = macros.view(WikiContext(test_tiddler,{}), WikiArgument("text"),WikiArgument("wikified"))
    #assert 'ok computer' in out

    test_tiddler.text = '[[out]]'
    out = macros.view(WikiContext(test_tiddler,{}), WikiArgument("text"), WikiArgument("wikified"))
    assert "</a>" in out
    
def test_view_link():
    link_context = {
            '$BASE_URL': '/test/bags/foo/tiddlers',
            '$REFLOW': 0
    }
    
    out = macros.view(WikiContext(test_tiddler,{},link_context), WikiArgument("title"),WikiArgument("link"))
    assert 'Test Tiddler' in out
    assert '</a>' in out
    assert 'href="/test/bags/foo/tiddlers/Test%20Tiddler"' in out
    test_tiddler.fields['bar'] = "80 days"
    test_tiddler.text = "<<view bar linkexternal withlotsargument: 'wondering how this might show' inparams: becauseihavenoidea foo:bar prefix:'around the world in/'>>"
    wikklytextplugins.init(config)
    text = wikklytextplugins.new_render(test_tiddler,{'tiddlyweb.config':config})
    assert 'around the world in/80%20days' in text