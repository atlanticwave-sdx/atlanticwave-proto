# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


from shared.Singleton import Singleton

class ControllerInterface(object):
    ''' This parent class is meant to act as a standard interface between a 
        particular OpenFlow speaker and the LocalController class. It isolates
        LocalController from the specifics of the speaker that is being used. 
        It allows changes in the speaker to be much easier. 
        Singleton. '''
    __metaclass__ = Singleton
    

    def __init__(self):
        pass
    
    def send_command(self, rule):
        ''' Takes an OpenFlowRule and pushes it to the switch. '''
        raise NotImplementedError("Subclasses must implement this.")

    def remove_rule(self, cookie):
        ''' Removes a rule based on cookie number. '''
        raise NotImplementedError("Subclasses must implement this.")

