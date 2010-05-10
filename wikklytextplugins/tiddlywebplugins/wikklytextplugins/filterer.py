from tiddlyweb import control
import logging
from tiddlyweb.model.bag import Bag

class Filterer:
  def __init__(self):
    self.filter = u""
    self.arg1 = ""
    self.arg2 = ""
    self.foo = "yes"
    self.and_tiddlers = []
  def reset_args(self):
    self.arg1 = ""
    self.arg2 = ""
    
    
  def write_to_arg1(self,token):
    if token and token != "[" and token != "]":
      self.arg1 += token
  def write_to_arg2(self,token):
    if token and token != "[" and token != "]":
      self.arg2 += token
  def addTiddler(self):
    logging.debug("addTiddler find %s"%self.arg1)
    
    #print "Add tiddler %s"%self.arg1
    for i in self.bag.list_tiddlers():
      if i.title == self.arg1:
        logging.debug("addTiddler added %s"%self.arg1)
        self.final_tiddlers.append(i)
    self.reset_args()
  def apply_limit(self):
    limit = int(self.arg2)
    limited_tiddlers = []
    for tiddler in self.final_tiddlers:
      if limit == 0:
        break
      limited_tiddlers.append(tiddler)
      limit -= 1
    self.final_tiddlers = limited_tiddlers
  def apply_sort(self):
    bag = Bag("tmp",tmpbag=True)
    bag.add_tiddlers(self.final_tiddlers)
    tiddlers = control.filter_tiddlers_from_bag(bag,'sort=%s'%self.arg2) 
    self.final_tiddlers = list(tiddlers)

  def saveAndFilterArg(self,token):
    #print "saveAndArg %s and %s"%(self.arg1,self.arg2)
    if self.arg1 == 'sort' or self.arg1 == 'limit':
      self.filter += "&%s=%s"%(self.arg1,self.arg2)
    else:
        self.and_tiddlers = self.match_tiddlers(self.and_tiddlers,self.arg1,self.arg2)
    
    self.reset_args()
    self.write_to_arg1(token)
    logging.debug("in saveAndFilter:%s "%self.filter)
  def applyAndFilter(self,token):
    #print "saveAndFilter %s and %s"%(self.arg1,self.arg2)      
    logging.debug("in applyAndFilter:")
    self.saveAndFilterArg(token)

    for tiddler in self.and_tiddlers:
      if tiddler not in self.final_tiddlers:
        self.final_tiddlers.append(tiddler)
    self.reset_args()
    self.and_tiddlers = self.bag.list_tiddlers()
  
  def match_tiddlers(self,tiddlers,field,val):
      if val[0] == '!':
          val = val[1:]
          negation_mode = True
      else:
          negation_mode = False
      if field == 'server.bag':
          field = "bag"
      if field == 'tag':
          field= 'tags'
      final =[]
      for tiddler in tiddlers:
        if tiddler not in final:
            try:
                fieldval = getattr(tiddler,field)
            except AttributeError:
                if field in tiddler.fields:
                    fieldval = tiddler.fields[field]
                else:
                    fieldval = ""
            result = False
            if type(fieldval) == type([]):
                if val in fieldval:
                    result = True
            else:
                if val == fieldval:
                    result = True
            if negation_mode:
                result = not result
            if result:
                final.append(tiddler)
      return final
      
  def applyORFilter(self,token):   
    logging.debug("applyORFilter: apply or filter %s"%self.arg1)
    #print "saveOR %s and %s"%(self.arg1,self.arg2)    
    try:
        try:
            index = self.arg1.index("sort")
            logging.debug("applyORFilter: found index %s"%index)
            self.apply_sort()
        except ValueError:
            index = self.arg1.index("limit")
            self.apply_limit()
    except ValueError:
        newtiddlers = self.bag.list_tiddlers()
        newtiddlers = self.match_tiddlers(newtiddlers,self.arg1,self.arg2)
        for tid in newtiddlers:
            if tid not in self.final_tiddlers:
                self.final_tiddlers.append(tid)
        
    self.reset_args()
  def get_filter_tiddlers(self,bag,filterstring):
    logging.debug("Filterer get_filter_tiddlers filter string=%s"%filterstring)
    state = "A"
    self.bag = bag
    self.final_tiddlers = []
    self.filter = u""
    self.and_tiddlers = self.bag.list_tiddlers()
    
    for token in filterstring:
      state = self.run(state,token)
      if state == 'Z':
        state = "A"
    
      #logging.debug("filter: have %s"%self.filter)
    logging.debug("filter: ended in %s"%state)
    return self.final_tiddlers
  def run(self,state,token):
    logging.debug("Filterer.run: in state %s with token %s "%(state,token))
    #logging.debug("filter:in state %s with %s"%(state,token))
    #print "in state %s with token %s"%(state,token)
    if state == 'A':
      if token =='[':
        return 'B'
      elif token == ' ' or token =='\n':
        return "A"
      else:
        self.write_to_arg1(token)
        return "Y"
    elif state == 'Y':
      self.write_to_arg1(token)
      if not token or token ==' ' or token =='\n':
        self.addTiddler()
        return 'Z'
      else:
        return "Y"
    elif state == 'B':
      self.write_to_arg1(token)
      if token =='[':
        return "C"
      else:
        return "F"
    elif state =='C':
      self.write_to_arg1(token)
      if token ==']':
        return "D"
      else:
        return "C"
    elif state =='D':
      if token ==']':
        self.addTiddler()
        return "Z"
    elif state =='F':
      self.write_to_arg1(token)
      if token =='[':
        return "G"
      else:
        return "F"
    elif state =='G':
      self.write_to_arg2(token)
      if token ==']':
        return "H"
      else:
        return "G"
    elif state =='H':
      if token ==']':
        self.applyORFilter(token)
        return "Z"
      else:
        self.saveAndFilterArg(token)
        return "I"
    elif state =='I':
      self.write_to_arg1(token)
      if token =='[':
        return "J"
      else:
        return "I"
    elif state =='J':
      self.write_to_arg2(token)
      if token ==']':
        return "K"
      else:
        return "J"
    elif state =='K':
      if token ==']':
        self.applyAndFilter(token)
        return "Z"
      else:
        self.saveAndFilterArg(token)
        return 'I'

def filter_tiddlers(bag_of_tiddlers,filter_string):
    f = Filterer()
    tiddlers = f.get_filter_tiddlers(bag_of_tiddlers,filter_string)
    return tiddlers