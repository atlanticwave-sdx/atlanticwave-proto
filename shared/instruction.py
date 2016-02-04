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

    def __init__(self):
        self.table_id = number_filed('table_id', min=0, max=2**8-1)
        super(instruction_GOTO_TABLE, self).__init__([self.table_id])        


class instruction_WRITE_METADATA(OpenFlowInstruction):
    ''' This instruction writes metadata information to matching flows. '''

    def __init__(self):
        self.metadata = number_field('metadata', min=1, max=2**64-1)
        self.metadata_mask = number_field('metadata_mask', min=1, max=2**64-1)
        super(instruction_WRITE_METADATA, self).__init__([self.metadata,
                                                          self.metadata_mask])
