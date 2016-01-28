# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


from ControllerInterface import ControllerInterface

class RyuControllerInterface(ControllerInterface):
    ''' This is a particular implementation of the ControllerInterface class
        that connects using Ryu. It inherits its interface from its parent 
        class. '''


    def __init__(self, *args, **kwargs):
        super(RyuControllerInterface, self).__init__(*args, **kwargs)
        pass

    def add_rule(self, rule):
        pass

    def remove_rule(self, rule):
        pass
