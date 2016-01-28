# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


from shared.Singleton import Singleton

class RuleManager(object):
    ''' This is the database of active rules. Storage, much like the 
        ParticipantManager. Keeps track of both the UserRule and associated 
        OpenFlowRules. Does not allow for modifying rules: only adding and 
        removing. Singleton. ''' 
    __metaclass__ = Singleton

    def __init__(self):
        pass

    def add_rule(self, rule):
        ''' Add rule to the active database. '''
        pass
    
    def remove_rule(self, rule):
        ''' Remove rule from the active database. '''
        pass
    
    def query_rule(self):
        ''' Find rules. '''
        pass
    
