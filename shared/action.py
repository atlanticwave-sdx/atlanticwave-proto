# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


from shared.ofconstants import *
from shared.offield.py import *


class OpenFlowAction(object):
    ''' This is the parent class for all OpenFlow Actions. It will include
        much of the functionality built-in that is necessary to validate
        most actions.
        Sublcasses will need to fill in certain values defined in __init__()
        which will often be enough for the existing validation routines. '''

    def __init__(self, fields):
        ''' fields is a list of Fields. '''
        self.fields = fields

    def check_validity(self):
        for field in self.fields:
            field.check_validity()
            if not field.is_optional():
                if field.value == None:
                    raise FieldValueError("Required field has no value")
                    

class action_OUTPUT(OpenFlowAction):
    ''' This action outputs packets to a specified port. '''

    def __init__(self):
        self.port = number_field('port', min=1, max=OFPP_MAX,
                                 others=[OFPP_MAX, OFPP_IN_PORT, OFPP_TABLE,
                                         OFPP_NORMAL, OFPP_FLOOD, OFPP_ALL,
                                         OFPP_CONTROLLER, OFPP_LOCAL,OFPP_ANY])
        self.max_len = number_field('max_len', min=0, max=OFPCML_MAX,
                                    others=[OFPCML_NO_BUFFER],
                                    prereq=number_field('port',
                                                        value=OFPP_CONTROLLER))
        super(action_OUTPUT, self).__init__([self.port, self.max_len])
        
        
class action_SET_FIELD(OpenFlowAction):
    ''' This action sets a field in matched flow's packets. '''

    def __init__(self):
        self.field = 
