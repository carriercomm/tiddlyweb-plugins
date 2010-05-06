from tiddlywebplugins.wikklytextplugins.plugins import macros
from wikklytext.base import Element
from wikklytext import WikContext

def WikiContext(tiddler=False,environ=False,setvars=False):
    context = WikContext()
    context.tiddler = tiddler
    context.environ = environ
    
    if setvars:
        for name, value in setvars.items():
            if isinstance(value, (str,unicode)):
                context.var_set_text(name, value)
            elif isinstance(value, int):
                context.var_set_int(name, value)
            else:
                raise WikError("Bad value in setvars")
    
    return context
    
def WikiArgument(val):
    arg1 = Element("text")
    arg1.text = val
    return arg1

def test_parseParams():
    result = macros.parseParams([WikiArgument("hello"),WikiArgument("world")])
    assert result == {}
    
    result = macros.parseParams([WikiArgument("hello:world"),WikiArgument("my:world")])
    assert result['hello']== "world"
    assert result['my']== "world"
    
    result = macros.parseParams([WikiArgument("hello:world"),WikiArgument("hello:jon"),WikiArgument("goodbye:ben"),WikiArgument("hello:ben")])
    assert result['goodbye'] == 'ben'
    assert result['hello'] == ['world','jon','ben']
    
    #<<view bar text withlotsargument: 'wondering how this might show' inparams: becauseihavenoidea foo:bar>> 
    new_arguments = [WikiArgument(u'bar'), WikiArgument(u'text'), WikiArgument(u'withlotsargument:'), WikiArgument(u'wondering how this might show'), WikiArgument(u'inparams:'), WikiArgument(u' becauseihavenoidea'), WikiArgument(u'foo:bar')]
    result = macros.parseParams(new_arguments)
    assert result['withlotsargument'] == 'wondering how this might show'
    assert result['inparams'] == ' becauseihavenoidea'
    assert result['foo'] == 'bar'
    