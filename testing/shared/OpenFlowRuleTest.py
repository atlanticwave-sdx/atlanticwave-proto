# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


# Unit tests for shared.OpenFlowRule module


import unittest
from shared.OpenFlowRule import *
from shared.match import *
from shared.instruction import *
from shared.action import *

class OpenFlowRuleTest(unittest.TestCase):
    def test_basic_init(self):
        fields = [Field("field"), Field("field")]
        match = OpenFlowMatch(fields)
        instruction = instruction_GOTO_TABLE(3)
        table = 1
        priority = 100
        cookie = 1234

        OpenFlowRule(match, instruction, table, priority, cookie)
        OpenFlowRule(match, instruction, table)
        OpenFlowRule(match, instruction, priority=priority)
        OpenFlowRule(match)

    def test_empty_init(self):
        # This is valid for OpenFlowRules
        rule = OpenFlowRule()

    def test_invalid_init1(self):
        fields = [Field("field"), Field("field")]
        match = [OpenFlowMatch(fields)] #invalid
        instruction = instruction_GOTO_TABLE(3)
        table = 1
        priority = 100
        cookie = 1234
        try:
            OpenFlowRule(match, instruction, table, priority, cookie)
        except TypeError:
            pass
        else:
            self.fail("did not see error")

    def test_invalid_init2(self):
        fields = [Field("field"), Field("field")]
        match = OpenFlowMatch(fields)
        instruction = [instruction_GOTO_TABLE(3)] #invalid
        table = 1
        priority = 100
        cookie = 1234
        try:
            OpenFlowRule(match, instruction, table, priority, cookie)
        except TypeError:
            pass
        else:
            self.fail("did not see error")
          
    def test_invalid_init3(self):
        fields = [Field("field"), Field("field")]
        match = OpenFlowMatch(fields)
        instruction = instruction_GOTO_TABLE(3)
        table = -1 #invalid
        priority = 100
        cookie = 1234
        try:
            OpenFlowRule(match, instruction, table, priority, cookie)
        except ValueError:
            pass
        else:
            self.fail("did not see error")
            
    def test_invalid_init4(self):
        fields = [number_field("field",3,100), number_field("field",3,100)]
        match = OpenFlowMatch(fields)
        instruction = instruction_GOTO_TABLE(3)
        table = 1
        priority = -100 #invalid
        cookie = 1234
        try:
            OpenFlowRule(match, instruction, table, priority, cookie)
        except ValueError:
            pass
        else:
            self.fail("did not see error")
            
    def test_invalid_init5(self):
        fields = [Field("field"), Field("field")]
        match = OpenFlowMatch(fields)
        instruction = instruction_GOTO_TABLE(3)
        table = 1
        priority = 100 
        cookie = 123456789012345678 #invalid
        try:
            OpenFlowRule(match, instruction, table, priority, cookie)
        except ValueError:
            pass
        else:
            self.fail("did not see error")
            
    def test_setMatch_valid(self):
        fields = [number_field("field",3,100,7), number_field("field",3,100,8)]        
        match = OpenFlowMatch(fields)
        rule = OpenFlowRule()
        rule.setMatch(match)

    def test_setMatch_invalid(self):
        match = "blah"
        rule = OpenFlowRule()
        try:
            rule.setMatch(match)
        except TypeError:
            pass
        else:
            self.fail("did not see error")        

    def test_setInstruction_valid(self):
        instruction = instruction_GOTO_TABLE(3)
        rule = OpenFlowRule()
        rule.setInstruction(instruction)
        pass

    def test_setInstruction_invalid1(self):
        instruction = "blah"
        rule = OpenFlowRule()
        try:
            rule.setInstruction(instruction)
        except TypeError:
            pass
        else:
            self.fail("did not see error")        

    def test_setCookie_valid(self):
        cookie = 1234
        rule = OpenFlowRule()
        rule.setCookie(cookie)        

    def test_setCookie_invalid1(self):
        cookie = "blah"
        rule = OpenFlowRule()
        try:
            rule.setCookie(cookie)
        except TypeError:
            pass
        else:
            self.fail("did not see error")

        cookie = -1
        try:
            rule.setCookie(cookie)
        except ValueError:
            pass
        else:
            self.fail("did not see error")

    def test_setTable_valid(self):
        table = 1
        rule = OpenFlowRule()
        rule.setTable(table)

    def test_setTable_invalid1(self):
        table = "blah"
        rule = OpenFlowRule()
        try:
            rule.setTable(table)
        except TypeError:
            pass
        else:
            self.fail("did not see error")

        table = -1
        try:
            rule.setTable(table)
        except ValueError:
            pass
        else:
            self.fail("did not see error")

    def test_setPriority_valid(self):
        priority = 100
        rule = OpenFlowRule()
        rule.setPriority(priority)

    def test_setPriority_invalid1(self):
        priority = "blah"
        rule = OpenFlowRule()
        try:
            rule.setPriority(priority)
        except TypeError:
            pass
        else:
            self.fail("did not see error")

        priority = -1
        try:
            rule.setPriority(priority)
        except ValueError:
            pass
        else:
            self.fail("did not see error")

    
if __name__ == '__main__':
    unittest.main()






