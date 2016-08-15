# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


from shared.Singleton import Singleton
from AuthorizationInspector import AuthorizationInspector
from TopologyManager import TopologyManager
from RuleRegistry import RuleRegistry

class BreakdownEngine(object):
    ''' The BreakdownEngine is one of the more complex pieces of the SDX 
        controller. It takes participant-level rules and breaks them down into 
        per-local controller rules. In the future, failover considerations will
        be added, in particular automatically creating backup paths will be added
        as a standard feature.
        Singleton. '''
    __metaclass__ = Singleton
    
    def __init__(self):
        pass

    def get_breakdown(self, rule, user):
        ''' Breaks down the given rule to rules that each local controller can 
            handle. Requires a user to verify that the user had the correct 
            permissions determined by the AuthorizationInspector for proposed 
            rules (e.g., if a user cannot create paths through a particular LC, 
            reroute around that LC). '''
        pass
    
