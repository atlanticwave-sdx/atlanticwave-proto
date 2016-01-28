# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


from shared.Singleton import Singleton

class LocalController(object):
    ''' The Local Controller is responsible for passing messages from the SDX 
        Controller to the switch. It needs two connections to both the SDX 
        controller and switch(es). ''' 
    __metaclass__ = Singleton

    def __init__(self):
        pass

    def _setup_logger(self):
        ''' Internal function for setting up the logger formats. '''
        pass

    def start_sdx_controller_connection(self):
        pass

    def start_switch_connection(self):
        pass

    def sdx_message_callback(self):
        pass
