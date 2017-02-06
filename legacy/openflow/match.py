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
        ''' fields is a list of Fields. '''
        if type(fields) != type([]):
            raise OpenFlowMatchTypeError("fields must be a list")
        for entry in fields:
            if not isinstance(entry, Field):
                raise OpenFlowMatchTypeError("fields must be a list of Field objects: " + str(entry))
        self.fields = fields

    def __repr__(self):
        fieldstr = ""
        for entry in self.fields:
            fieldstr += entry.__repr__() + ",\n"
        if fieldstr != "":
            fieldstr = fieldstr[0:-2]
        return "%s : %s" % (self.__class__.__name__,
                            fieldstr)

    def __str__(self):
        fieldstr = ""
        for entry in self.fields:
            fieldstr += str(entry) + ", "
        if fieldstr != "":
            fieldstr = fieldstr[0:-2]
        return "match(%s)" % fieldstr

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        return (self.fields == other.fields)
    
    def check_validity(self):
        for field in self.fields:
            if not field.is_optional(self.fields):
                field.check_validity()
            field.check_prerequisites(self.fields)

