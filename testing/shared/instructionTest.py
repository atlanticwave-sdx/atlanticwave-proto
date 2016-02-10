# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


# Unit tests for shared.instruction module

import unittest
from shared.instruction import *
from shared.action import *


class BasicInstructionTest(unittest.TestCase):
    def test_basic_init(self):
        fields = [Field('field')]
        actions = [OpenFlowAction(fields), OpenFlowAction(fields)]
        instruction = OpenFlowInstruction(actions)

    def test_empty_init(self):
        try:
            action = OpenFlowInstruction()
        except TypeError:
            pass
        else:
            self.fail("did not see error")
        
    def test_invalid_init1(self):
        # incorrect fields type
        fields = Field('field')
        try:
            action = OpenFlowInstruction(fields)
        except TypeError:
            pass
        else:
            self.fail("did not see error")

    def test_invalid_init2(self):
        # incorrect fields type
        fields = ['a', 'b', 'c']
        try:
            action = OpenFlowInstruction(fields)
        except TypeError:
            pass
        else:
            self.fail("did not see error")
            
    def test_invalid_init3(self):
        # incorrect fields type
        fields = [Field('field'), Field('field')]
        action = OpenFlowAction(fields)
        try:
            instruction = OpenFlowInstruction(action)
        except TypeError:
            pass
        else:
            self.fail("did not see error")

    def test_invalid_init4(self):
        # incorrect fields type 
        fields = [Field('field'), Field('field')]
        actions = OpenFlowAction(fields)
        try:
            instruction = OpenFlowInstruction([actions, 'a'])
        except TypeError:
            pass
        else:
            self.fail("did not see error")
            

class ChildrenInstructionTest(unittest.TestCase):
    def test_goto(self):
        goto1 = instruction_GOTO_TABLE()
        goto2 = instruction_GOTO_TABLE(1)

    def test_write_metadata(self):
        write = instruction_WRITE_METADATA(1)
        write = instruction_WRITE_METADATA(1, 0xffff)

    def test_write_actions(self):
        fields = [Field('field'), Field('field')]
        actions = OpenFlowAction(fields)
        write = instruction_WRITE_ACTIONS([actions])
        
    def test_apply(self):
        fields = [Field('field'), Field('field')]
        actions = OpenFlowAction(fields)
        write = instruction_WRITE_ACTIONS([actions])

    def test_clear(self):
        clear = instruction_CLEAR_ACTIONS()


        
if __name__ == '__main__':
    unittest.main()
