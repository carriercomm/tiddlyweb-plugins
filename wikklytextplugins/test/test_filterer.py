from tiddlywebplugins.wikklytextplugins import filterer
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.model.tiddler import Tiddler

def add_tiddlers(bag,tiddlers):
    for tid in tiddlers:
        tiddler = Tiddler(tid['title'])
        for key in ['text','modified','fields','tags','modifier','recipe','bag']:
            if key in tid:
                if tid[key]:
                    setattr(tiddler,key,tid[key])
        bag.add_tiddler(tiddler)
    return bag
        
def test_filter_tiddlers():
    #setup
    bag = Bag("test",tmpbag=True)
    tiddlers = [
        {'title':'foo12','tags':[]},
        {'title':'foo2','tags':['foo']},
        {'title':'foo3','bag':'jon','tags':['bart','foo']},
        {'title':'foo4','tags':[],'fields':{}},
        {'title':'foo5','tags':[],'fields':{'new':'yes'}},
        {'title':'foo6','tags':[],'fields':{}},
        {'title':'foo7','tags':[],'fields':{'new':'maybe'}},
        {'title':'foo8','tags':[],'fields':{}},
        {'title':'foo9','tags':[],'fields':{'new':'yes'}},
        {'title':'foo10','tags':[],'fields':{'new':'yes'}},
        {'title':'foo11','tags':[],'fields':{}},
        {'title':'foo1','bag':'jon','tags':[],'fields':{}},
        {'title':'foo13','bag':'jon','tags':[],'fields':{'new':'no'}}
    ]#13 tiddlers
    add_tiddlers(bag,tiddlers)
    tiddlers = filterer.filter_tiddlers(bag,"[tag[foo]]")
    assert len(tiddlers) == 2
    
    tiddlers = filterer.filter_tiddlers(bag,"[server.bag[jon]]")
    assert len(tiddlers) == 3
    
    tiddlers = filterer.filter_tiddlers(bag,"[server.bag[jon]tag[foo]]")
    assert len(tiddlers) == 1
   
    tiddlers = filterer.filter_tiddlers(bag,"[[foo5]][[foo4]]")
    assert len(tiddlers) == 2
     
    tiddlers = filterer.filter_tiddlers(bag,"[[foo5]] [[foo4]]")
    assert len(tiddlers) == 2
    
    tiddlers = filterer.filter_tiddlers(bag,"[[foo50]] [[foo4]]")
    assert len(tiddlers) == 1 #foo 50 doesn't exist
    
    tiddlers = filterer.filter_tiddlers(bag,"[new[yes]] [new[maybe]]")
    assert len(tiddlers) == 4 
    
    tiddlers = filterer.filter_tiddlers(bag,"[new[!yes]] [new[!maybe]]")
    #!yes matches all 13 except the 3 with yes
    #!maybe matches all 13 except the 1 with maybe.
    #all match one of these values.
    assert len(tiddlers) == 13
    
    tiddlers = filterer.filter_tiddlers(bag,"[new[!yes]new[!maybe]]")
    #this matches all that are not yes and not maybe (so all the nos and blanks)
    assert len(tiddlers) == 9
    
    tiddlers = filterer.filter_tiddlers(bag,"[new[!yes]new[!maybe]] [limit[2]]")
    assert len(tiddlers) == 2
    
    tiddlers = filterer.filter_tiddlers(bag,"[new[!yes]new[!maybe]] [sort[title]]")
    assert len(tiddlers) == 9
    assert tiddlers[2].title=='foo12'
    
    
    tiddlers = filterer.filter_tiddlers(bag,"[new[!yes]new[!maybe]] [sort[title]] [limit[1]]")
    assert len(tiddlers) == 1
    assert tiddlers[0].title=='foo1'