# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project

from shared.Singleton import Singleton

class RestAPI(object):
    ''' The REST API will be the main interface for participants to use to push 
        rules (eventually) down to switches. It will gather authentication 
        information from the participant and check with the 
        AuthenticationInspector if the participant is authentic. It will check 
        with the AuthorizationInspector if a particular action is available to a 
        given participant. Once authorized, rules will be pushed to the 
        RuleManager. It will draw some of its API from the RuleRegistry, 
        specifically for the libraries that register with the RuleRegistry. 
        Singleton. '''
    __metaclass__ = Singleton

    def __init__(self):
        pass

    def _setup_logger(self):
        ''' Internal fucntion for setting up the logger formats. '''
        pass
