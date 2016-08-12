# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


from shared.Singleton import Singleton
from AuthorizationInspector import AuthorizationInspector 
from TopologyManager import TopologyManager
from RuleRegistry import RuleRegistry

class ValidityInspectorError(Exception):
    ''' Parent class, can be used as a catch-all for the other errors '''
    pass

class ValidityInspectorNotValidRule(ValidityInspectorError):
    ''' Raised when a rule is not valid. Rule cannot be installed. '''
    pass

class ValidityInspectorOverlappingRule(ValidityInspectorError):
    ''' Raised when a rule overlaps another rule, but is of different priority.
        Rule can be installed, but may not have the indented effect. '''
    pass

class ValidityInspector(object):
    ''' The ValidityInspector will verify that a particular rule is valid. For 
        instance, confirming that port 16 exists at a given location. To handle 
        validation, external information will be needed. As an example, 
        information about physical setup at each location may be provided by the
        LocalControllerManager. How this is done is not decided as of this 
        writing, and may introduce more links into the diagram above.
        Singleton. '''
    __metaclass__ = Singleton

    def __init__(self):
        pass
    
    def is_valid_rule(self, rule, user):
        ''' Checks to see if a rule is valid. True if valid, False if not. Raises
            error if user does not exist. 
            Needs user to see if user is authorized to make such a rule. ''' 
        pass
