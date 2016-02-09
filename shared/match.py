# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


from shared.offield import *

class OpenFlowMatchTypeError(TypeError):
    pass

class OpenFlowMatchValueError(ValueError):
    pass

class OpenFlowMatchPrereqError(ValueError):
    pass



class OpenFlowMatch(object):
    ''' This class represents all the fields that are being matched at once.
        Its primary purpose is to hang on to the individual match elements and
        provide an easy way to verify if everything is valid and all 
        prerequisites are met. '''

    def __init__(self, fields):
        self.fields = field

    def check_validity(self):
        for field in self.fields:
            field.check_validity()

    def check_prerequisites(self):
        for field in self.fields:
            field.check_prerequisites(self.fields)


