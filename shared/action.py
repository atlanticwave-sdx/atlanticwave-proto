# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


from shared.ofconstants import *
from shared.offield import *
from shared.match import *

class OpenFlowActionTypeError(TypeError):
    pass

class OpenFlowActionValueError(ValueError):
    pass

class OpenFlowAction(object):
    ''' This is the parent class for all OpenFlow Actions. It will include
        much of the functionality built-in that is necessary to validate
        most actions.
        Sublcasses will need to fill in certain values defined in __init__()
        which will often be enough for the existing validation routines. '''

    def __init__(self, fields, name="OpenFlowAction"):
        ''' fields is a list of Fields. '''
        if type(fields) != type([]):
            raise OpenFlowActionTypeError("fields must be a list")
        for entry in fields:
            if not isinstance(entry, Field):
                raise OpenFlowActionTypeError("fields must be a list of Field objects")
        self.fields = fields
        self._name = name

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
        return "%s(%s)" % (self._name, fieldstr)
    
    def check_validity(self):
        for field in self.fields:
            if not field.is_optional(self.fields):
                field.check_validity()
            field.check_prerequisites(self.fields)
                    

class action_OUTPUT(OpenFlowAction):
    ''' This action outputs packets to a specified port. '''

    def __init__(self, port, max_len=None):
        self.port = number_field('port', minval=1, maxval=OFPP_MAX,
                                 value=port,
                                 others=[OFPP_MAX, OFPP_IN_PORT, OFPP_TABLE,
                                         OFPP_NORMAL, OFPP_FLOOD, OFPP_ALL,
                                         OFPP_CONTROLLER, OFPP_LOCAL,OFPP_ANY])
        self.max_len = number_field('max_len', minval=0, maxval=OFPCML_MAX,
                                    value=max_len,
                                    others=[OFPCML_NO_BUFFER],
                                    optional_without=number_field('port',
                                                                  minval=1,
                                                                  maxval=OFPP_MAX,
                                                                  value=OFPP_CONTROLLER))
        super(action_OUTPUT, self).__init__([self.port, self.max_len], "output")
        
        
class action_SET_FIELD(OpenFlowAction):
    ''' This action sets a field in matched flow's packets. '''

    def __init__(self, field):
        if type(field) not in VALID_MATCH_FIELDS:
            raise OpenFlowActionTypeError(str(type(field)) + " is not a VALID_MATCH_FIELDS")
        if field.value == None:
            raise OpenFlowActionValueError("Passed in field does not have its value set.")
        self.field = field
        super(action_SET_FIELD, self).__init__([self.field], "set_field")

#TODO - There are a bunch more OFPAT that need to be incorperated here.
# OF Spec 1.3.2, page 58

# This is a translation mechanism for mapping a name to a class
# Value is assumed
# Can be used for aliases!
ACTION_NAME_TO_CLASS = { 'fwd': {'type':action_OUTPUT,'fields':False},
                         'output':{'type':action_OUTPUT, 'fields':False},
                         'set': {'type':action_SET_FIELD, 'fields':True},
                       }
