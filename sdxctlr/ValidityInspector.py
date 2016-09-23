# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


from shared.Singleton import SingletonMixin
from AuthorizationInspector import AuthorizationInspector 
from TopologyManager import TopologyManager

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

class ValidityInspector(SingletonMixin):
    ''' The ValidityInspector will verify that a particular rule is valid. For 
        instance, confirming that port 16 exists at a given location. To handle 
        validation, external information will be needed. As an example, 
        information about physical setup at each location may be provided by the
        LocalControllerManager. How this is done is not decided as of this 
        writing, and may introduce more links into the diagram above.
        Singleton. '''

    def __init__(self):
        pass
    
    def is_valid_rule(self, rule):
        ''' Checks to see if a rule is valid. True if valid. Raises error 
            describing problem if invalid. '''
        #FIXME: I am confused. I cannot find an object named 'rule' anywhere and doing a search in the filesystem for objects that call "check_validity" just takes me back here. I need some clarification please.
        return rule.check_validity(TopologyManager.instance().get_topology(),
                                   AuthorizationInspector.instance().is_authorized)

