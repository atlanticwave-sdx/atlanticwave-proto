# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


from shared.Singleton import Singleton

class RuleRegistry(object):
    ''' The RuleRegistry is, in effect, a callback repository. Outside libraries
        that create participant-level rules are able to register callbacks here 
        that the ValidityInspector, the BreakdownEngine, and the REST API can use
        to perform their actions. This allows for a standardized interface that 
        outside developers can use to create new types of rules. 
        Singleton. '''
    __metaclass__ = Singleton


    #FIXME: what do rules look like? Dictionaries as they are right now?

    def __init__(self):
        pass

def register_rule_type(self, ruletype, callback_for_syntax_check,
                       callback_for_validity, callback_for_breakdown):
    ''' This registers a new type of rule, along with all the functions used for
        validation and breakdown.
        - ruletype is a string.
        - callback_for_syntax_check passes the whole rule for a syntax check 
          (i.e., if the rule requires a port number, this makes sure there is a 
          port number as one of the fields).
        - callback_for_validity checks the rule against the topology and if the 
          participant is allowed to perform a particular action (e.g., can write 
          rules for a particular port).
        - callback_for_breakdown is used to breakdown a rule into smaller, 
          per-local-controller pieces for implementation. '''
    pass

def syntax_check(self, rule):
    ''' Used by the REST API to perform a syntax check on a particular rule. To 
        do this, it looks at its registered callbacks for a particular type of 
        rule. Returns true if syntax is valid, false otherwise. '''
    pass

def get_validation_functions(self):
    ''' Get a list of all registered validation functions. Each entry in the list
        will be a tuple (ruletype, function). '''
    pass


def register_for_validation_functions(self, callback):
    ''' Get new validation functions as they come in. callback will take a tuple 
        (ruletype, function). '''
    pass

def get_breakdown_functions(self):
    ''' Get a list of all breakdown functions. Each entry in the list will be a 
        tuple (ruletype, function). '''
    pass

def register_for_breakdown_functions(self, callback):
    ''' Get new breakdown functions as they come in. callback will take a tuple 
        (ruletype, function). '''
    pass

