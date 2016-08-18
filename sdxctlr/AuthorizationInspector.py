# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


import logging
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
    ''' The AuthorizationInspector is responsible for authorizing actions. 
        Actions include viewing status of the network, viewing rules of the
        network, pushing rules to network, removing own rules from network, and 
        removing any rules from network. Most users will be authorized for a 
        subset of these actions, with only administrators able to remove rules 
        from other participants. In the future, more granularity will be added 
        (i.e., Alice will be able to install rule types X, Y, and Z, while Bob 
        can only install rule type X). The actions will likely evolve 
        significantly.
        Singleton. '''
    __metaclass__ = Singleton

    def __init__(self):
        pass


    def is_authorized(self, username, action, **kwargs):
        ''' Returns true if user is allowed to take a particular action, false 
            otherwise. If a user is not in the database, raise and error. '''
        #FIXME: Actions need to be defined.
        #FIXME: This will always return true for the time being.
        return True

    def set_user_authrorization(self, username, list_of_permitted_actions):
        ''' Adds authorization information for a particular user. Replaces 
            previous authorization record for that particular user. Must only be
            called by the ParticipantManager. '''
        pass
    
