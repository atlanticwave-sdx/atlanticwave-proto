# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


from shared.Singleton import Singleton

class OpenFlowTranslator(object):
    ''' This translates UserRules to OpenFlowRules. There should not be any 
        inter-translation state being kept. Singleton. '''
    __metaclass__ = Singleton

    def __init__(self):
        pass

    def translate(self, user_rule):
        ''' This translate the UserRule and returns a set of OpenFlowRules. '''
        pass

    


