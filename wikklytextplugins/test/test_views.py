from tiddlywebplugins.wikklytextplugins.plugins import macros
from tiddlyweb.model.tiddler import Tiddler
from tiddlywebplugins import wikklytextplugins
from tiddlywebplugins import wikklytextrender
from tiddlyweb.config import config
from test_common import WikiArgument,WikiContext

test_tiddler=  Tiddler("Test Tiddler","bag")
test_tiddler.modified = "20071003201000"
test_tiddler.revision = 2

def test_view_date():
    out = macros.view(WikiContext(test_tiddler,{}), WikiArgument("modified"),WikiArgument("date"))
    assert '03 October 2007' in out
    
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
    assert 'bag' in out 
    
    out = macros.view(WikiContext(test_tiddler,{}), WikiArgument("server.page.revision"),WikiArgument("text"))
    assert '2' in out
    
    out = macros.view(WikiContext(test_tiddler,{}), WikiArgument("tags"),WikiArgument("text"))
    assert 'jon ben [[jeremy ruston]]' in out
    
    
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
    config['wikklytext.safe_mode'] = False
    wikklytextplugins.init(config)
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
    text = wikklytextrender.render(test_tiddler,{'tiddlyweb.config':config})
    assert 'around the world in/80%20days' in text

def test_view_wikiwords_link():
    wikklytextplugins.init(config)
    test_tiddler = Tiddler("Email, Notifications, Atom Feeds and WikklyText")
    test_tiddler.text = "<<view title linkexternal prefix:/posts/>>"
    
    link_context = {
            '$BASE_URL': '/test',
            '$REFLOW': 0
    }
    out = macros.view(WikiContext(test_tiddler,{},link_context), WikiArgument("title"),WikiArgument("linkexternal"),WikiArgument("prefix:/posts/"))
    assert 'a href=' in out
    assert '/test' not in out
    assert '/posts/Email%2C%20Notifications%2C%20Atom%20Feeds%20and%20WikklyText' in out
    
