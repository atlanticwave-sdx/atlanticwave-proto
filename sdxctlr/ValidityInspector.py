# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


from shared.Singleton import Singleton

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
    ''' Decides if it is possible for this rule to fit in with existing rules. 
        Singleton. '''

    __metaclass__ = Singleton

    def __init__(self):
        pass
    
    def is_valid_rule(self, participant):
        ''' Returns True if rule is valid.
            Raises above errors otherwise. '''
        pass
