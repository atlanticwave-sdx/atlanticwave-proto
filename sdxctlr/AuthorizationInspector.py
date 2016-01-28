# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


from shared.Singleton import Singleton

class AuthorizationInspectorError(Exception):
    ''' Parent class, can be used as a catch-all for the other errors '''
    pass

class AuthorizationInspectorLoginNotAuthorized(AuthorizationInspectorError):
    ''' Raised when a login is disallowed. '''
    pass

class AuthorizationInspectorRuleNotAuthorized(AuthorizationInspectorError):
    ''' Raised when a rule installation is not authorized. '''
    pass

class AuthorizationInspector(object):
    ''' Decides if participant or controller can log in. Decides if an incoming 
        UserRule is allowed based on the participant’s rights. Connects to the 
        ParticipantManager and LocalControllerManager. Singleton. '''
    __metaclass__ = Singleton

    def __init__(self):
        pass
    
    def is_authorized_login(self, participant):
        ''' Returns True if participant or controller can log in. 
            Returns False otherwise. '''
        pass

    def is_authorized_rule(self, rule):
        ''' Returns True if rule is authorized from the participant. 
            Returns False otherwise. '''
        pass
