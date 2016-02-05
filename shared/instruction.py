# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


from shared.ofconstant import *
from shared.offield import *
from shared.action import OpenFlowAction

class OpenFlowInstruction(OpenFlowAction):
    ''' This is the parent class for all OpenFlow Instructions. It will include
        much of the functionali9ty built-in that is necessary to validate most
        instructions.
        Subclasses will need to fill in certain values defined in __init__()
        which will often be enough for the existing validation routines. '''
    pass

class instruction_GOTO_TABLE(OpenFlowInstruction):
    ''' This instruction pushes matching flows to a specified table. '''

    def __init__(self, tableid=None):
        self.table_id = number_filed('table_id', min=0, max=2**8-1, value=tableid)
        super(instruction_GOTO_TABLE, self).__init__([self.table_id])        


class instruction_WRITE_METADATA(OpenFlowInstruction):
    ''' This instruction writes metadata information to matching flows. '''

    def __init__(self, metadata=None, metadata_mask=None):
        self.metadata = number_field('metadata', min=1, max=2**64-1,
                                     value=metadata)
        self.metadata_mask = number_field('metadata_mask', min=1, max=2**64-1,
                                          value=metadata_mask)
        super(instruction_WRITE_METADATA, self).__init__([self.metadata,
                                                          self.metadata_mask])

class instruction_WRITE_ACTIONS(OpenFlowInstruction):
    ''' This instruction writes actions. '''

    def __init__(self, actionlist):
        self.actions = actionlist
        super(instruction_WRITE_ACTIONS, self).__init__(actionlist)


class instruction_APPLY_ACTIONS(OpenFlowInstruction):
    ''' This instruction applies actions. '''

    def __init__(self, actionlist):
        self.actions = actionlist
        super(instruction_APPLY_ACTIONS, self).__init__(actionlist)
        
class instruction_CLEAR_ACTIONS(OpenFlowInstruction):
    ''' This instruction clears actions. '''

    def __init__(self):
        super(instruction_CLEAR_ACTIONS, self).__init__([])


# TODO - OFPIT_METER, page 55,57 of OF 1.3.2 spec.
