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
        #cls.parser = ConfigurationParser() # How it was once done. Fcns now.
        pass

    def test_config_simple_1(self):
        # Basic, single item test
        print "test_config_simple_1"
        match = OpenFlowMatch([IP_PROTO(6), ETH_TYPE(0x0800)])
        action = action_OUTPUT(1)
        instruction =  instruction_WRITE_ACTIONS([action])
        table = 1
        priority = 123
        cookie = 1234
        simple_1 = OpenFlowRule(match, instruction, table, priority, cookie)
        config = parse_configuration_file('config_simple_1.json')
#        print "simple_1: " + str(simple_1)
#        print "config  : " + str(config[0])
        self.failUnlessEqual(str(simple_1), str(config[0]))
        self.failUnlessEqual(simple_1, config[0])
        
        
    def test_config_simple_2(self):
        # Two item test, with IP Addresses and Set
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
        
        config = parse_configuration_file('config_simple_2.json')
#        print "simple_1 : " + str(simple_1)
#        print "config[0]: " + str(config[0])
#        print "simple_2 : " + str(simple_2)
#        print "config[1]: " + str(config[1])
        self.failUnlessEqual(str(simple_1), str(config[0]))
        self.failUnlessEqual(str(simple_2), str(config[1]))
        self.failUnlessEqual(simple_1, config[0])
        self.failUnlessEqual(simple_2, config[1])
        self.failUnlessEqual(rules, config)
        

    def test_config_simple_3(self):
        # Two item test with multiple actions
        print "test_config_simple_3"
        rules = []
        match = OpenFlowMatch([IP_PROTO(6), ETH_TYPE(0x0800)])
        actions = [action_OUTPUT(1), action_OUTPUT(2)]
        instruction =  instruction_WRITE_ACTIONS(actions)
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
        
        config = parse_configuration_file('config_simple_3.json')
#        print "simple_1 : " + str(simple_1)
#        print "config[0]: " + str(config[0])
#        print "simple_2 : " + str(simple_2)
#        print "config[1]: " + str(config[1])
        self.failUnlessEqual(str(simple_1), str(config[0]))
        self.failUnlessEqual(str(simple_2), str(config[1]))
        self.failUnlessEqual(simple_1, config[0])
        self.failUnlessEqual(simple_2, config[1])
        self.failUnlessEqual(rules, config)


    def test_config_simple_4(self):
        # test clear_actions and write_metadata
        print "test_config_simple_4"
        rules = []
        instruction =  instruction_CLEAR_ACTIONS()
        table = 1 # Should this be necessary? I dont' think so
        priority = 123
        cookie = 1234
        switch_id = 1
        simple_1 = OpenFlowRule(instruction=instruction,
                                table=table, priority=priority,
                                cookie=cookie, switch_id=switch_id)
        rules.append(simple_1)

        match = OpenFlowMatch([IP_PROTO(6), ETH_TYPE(0x0800)])
        instruction =  instruction_WRITE_METADATA(1999, 8191)
        table = 2
        priority = 234
        cookie = 1235
        switch_id = 2
        simple_2 = OpenFlowRule(match, instruction, table, priority, cookie, switch_id)
        rules.append(simple_2)
        
        config = parse_configuration_file('config_simple_4.json')
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
