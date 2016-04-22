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
        
        
    def test_config_simple_2(self):
        print "test_config_simple_2"
        rules = []
        match = OpenFlowMatch([IP_PROTO(6), ETH_TYPE(0x0800)])
        action = action_OUTPUT(1)
        instruction =  instruction_WRITE_ACTIONS([action])
        table = 1
        priority = 123
        cookie = 1234
        switch_id = 1
        simple_1 = OpenFlowRule(match, instruction, table, priority, cookie, switch_id)
        rules.append(simple_1)

        match = OpenFlowMatch([IP_PROTO(6), ETH_TYPE(0x0800), IPV4_SRC("1.2.3.4")])
        action = action_SET_FIELD(IPV4_SRC("2.3.4.5"))
        instruction =  instruction_WRITE_ACTIONS([action])
        table = 2
        priority = 234
        cookie = 1235
        switch_id = 2
        simple_2 = OpenFlowRule(match, instruction, table, priority, cookie, switch_id)
        rules.append(simple_2)
        
        config = self.parser.parse_configuration_file('config_simple_2.json')
#        print "simple_1 : " + str(simple_1)
#        print "config[0]: " + str(config[0])
#        print "simple_2 : " + str(simple_2)
#        print "config[1]: " + str(config[1])
        self.failUnlessEqual(str(simple_1), str(config[0]))
        self.failUnlessEqual(str(simple_2), str(config[1]))
        self.failUnlessEqual(simple_1, config[0])
        self.failUnlessEqual(simple_2, config[1])
        self.failUnlessEqual(rules, config)
        






if __name__ == '__main__':
    unittest.main()
