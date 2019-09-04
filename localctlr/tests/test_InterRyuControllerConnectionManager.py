# Copyright 2019 - Sean Donovan
# AtlanticWave/SDX Project


# Unittests for localctlr/InterRyuControllerConnectionManager class

import unittest
import logging
import os
from localctlr.InterRyuControllerConnectionManager import *

class BasicTests(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.logger = logging.getLogger(cls.__name__)
        formatter = logging.Formatter('%(asctime)s %(name)-12s: %(thread)s %(levelname)-8s %(message)s')
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        console.setFormatter(formatter)
        cls.logger.setLevel(logging.DEBUG)
        cls.logger.handlers = []
        cls.logger.addHandler(console)

        cls.logger.debug("Beginning %s:%s" % (os.path.basename(__file__),
                                              cls.__name__))
        
    def test_init(self):
        self.logger.warning("BEGIN %s" % (self.id()))
        ctlr = InterRyuControllerConnectionManager()
        

        
if __name__ == '__main__':
    unittest.main()
