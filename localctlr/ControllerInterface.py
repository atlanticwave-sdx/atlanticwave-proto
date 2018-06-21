# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


from lib.AtlanticWaveModule import *

class ControllerInterfaceTypeError(TypeError):
    pass

class ControllerInterfaceValueError(ValueError):
    pass

class ControllerInterface(AtlanticWaveModule):
    ''' This parent class is meant to act as a standard interface between a 
        particular OpenFlow speaker and the LocalController class. It isolates
        LocalController from the specifics of the speaker that is being used. 
        It allows changes in the speaker to be much easier. 
        Singleton. '''
    

    def __init__(self, loggerid):
        super(ControllerInterface, self).__init__(loggerid)
        pass
    
    def send_command(self, switch_id, rule):
        ''' Takes an OpenFlowRule and pushes it to the switch. '''
        raise NotImplementedError("Subclasses must implement this.")

    def remove_rule(self, switch_id, rule):
        ''' Removes a rule based on cookie number. '''
        raise NotImplementedError("Subclasses must implement this.")

