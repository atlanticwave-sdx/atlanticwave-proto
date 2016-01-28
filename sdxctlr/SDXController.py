# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


from shared.Singleton import Singleton

class SDXController(object):
    ''' This is the core of the SDX controller. It is primarily an orchestration
        engine, stitching together all the pieces above to properly process 
        participant requests. Singleton. ''' 
    __metaclass__ = Singleton

    def __init__(self):
        pass

    def _setup_logger(self):
        ''' Internal function for setting up the logger formats. '''
        pass

    def new_participant_connection(self):
        ''' This is the handler for new connections from participants. It will
            check with the AuthorizationInspector to see if the participant is 
            authorized. '''
        pass
    
    def new_local_controller_connection(self):
        ''' This is the handler for new connections from local controllers. It 
            will check with the AuthorizationInspector to see if the participant
            is authorized. '''
        pass

    def new_participant_rule(self):
        ''' This is the handler for new rules from participants. First, checks 
            with the AuthorizationInspector to see if the participant is 
            authorized. Next sends it to the OpenFlowTranslator to get an 
            OpenFlowRule. Then sends to ValidityInspector to verify that it is, 
            in fact, a valid rule, then sends it to the appropriate local 
            controller for implementation. '''
        pass
