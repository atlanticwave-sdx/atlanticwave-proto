# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


# Unit tests for RyuTranslateInterfaace

import unittest
import mock
from localctlr.RyuTranslateInterface import *
from shared.match import *
from shared.offield import *
from time import sleep


class RyuTranslateInit(unittest.TestCase):
    

    def atest_basic_init(self):
        translate = RyuTranslateInterface()


class RyuTranslateMatchTests(unittest.TestCase):

    def setUp(self):
        self.trans = RyuTranslateInterface()  # TODO _ THIS WON"T WORK RIGHT NOW, NEEDS TO BE SPAWNED FROM RYUCONTROLLERINTERFACE
        sleep(100)
        print "Datapaths: " + str(self.trans.datapaths.keys())
        self.datapath = self.trans.datapaths[self.trans.datapaths.keys()[0]]

    def test_trans_match_single(self):
        match_to_translate = OpenFlowMatch([IPV4_SRC("1.2.3.4")])
        translated_match = self.translate_match(match_to_translate)
        






if __name__ == '__main__':
    unittest.main()
