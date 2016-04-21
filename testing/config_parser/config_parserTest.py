# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


# Unit tests for config_parser.config_parser module

import unittest
from config_parser.config_parser import *


class ParserTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.parser = ConfigurationParser()

    def test_config_simple_1(self):
        print "test_config_simple_1"
        config = self.parser.parse_configuration_file('config_simple_1.json')
        print config
        






if __name__ == '__main__':
    unittest.main()
