# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


# Unit tests for config_parser.config_parser module

import unittest
from config_parser.config_parser import *
from shared.offield import *
from shared.match import *
from shared.action import *
from shared.OpenFlowRule import *


class ParserTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.parser = ConfigurationParser()

    def test_config_simple_1(self):
        print "test_config_simple_1"
        match = OpenFlowMatch([IP_PROTO(6), ETH_TYPE(0x0800)])
        action = action_OUTPUT(1)
        instruction =  instruction_WRITE_ACTIONS([action])
        table = 1
        priority = 123
        cookie = 1234
        simple_1 = OpenFlowRule(match, instruction, table, priority, cookie)
        config = self.parser.parse_configuration_file('config_simple_1.json')
#        print "simple_1: " + str(simple_1)
#        print "config  : " + str(config[0])
        self.failUnlessEqual(str(simple_1), str(config[0]))
        self.failUnlessEqual(simple_1, config[0])
        
        






if __name__ == '__main__':
    unittest.main()
