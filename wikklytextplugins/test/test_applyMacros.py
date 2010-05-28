from tiddlyweb.model.tiddler import Tiddler
from tiddlywebplugins.wikklytextplugins import applyHtmlMacros

def test_applyMacros():
    tiddler = Tiddler("foo","test")
    tiddler.text = "''hello'' world"
    html = "<!--{{{--><div class='toolbar' macro='toolbar [[ToolbarCommands::ViewToolbar]]'></div><div class='hello' macro='echo test'></div><span macro='echo foo' id='zyzx'>bar</span></div></div><!--;}}}-->"
    result = applyHtmlMacros({},html,tiddler)

    assert "<div class='toolbar'" in result
    assert "<div class='hello' macro='echo test'>test</div>" in result
    assert "<span macro='echo foo' id='zyzx'>foobar" in result
    
    html = '''
    <div id='foo' macro="echo hello"> my name is jon</div>
    '''
    result = applyHtmlMacros({},html,tiddler)

    assert "hello my name is jon" in result