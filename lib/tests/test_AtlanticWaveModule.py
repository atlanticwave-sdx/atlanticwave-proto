# Copyright 2019 - Sean Donovan
# AtlanticWave/SDX Project

# Unit test for lib.AtlanticWaveModule

import unittest
import os
from testfixtures import LogCapture
from lib.AtlanticWaveModule import *


class InitTest(unittest.TestCase):
    def test_singleton(self):
        pass
    
class DefaultLogSetupTest(unittest.TestCase):
    def setUp(self):
        self.logfilename = "logname.log"
        #Debug log file name uses the defaults

    def test_log_setup(self):
         # Initialize
        module = AtlanticWaveModule(__name__,
                                    self.logfilename)

        # Check Logfile
        with LogCapture() as l:
            module.logger.warning("Test1")
            module.dlogger.error("Test2")

            l.check((__name__, 'WARNING', "Test1"),
                    ("debug."+__name__, 'ERROR', "Test2"))       
        del module
        
class LogSetupTest(unittest.TestCase):
    def setUp(self):
        self.logfilename = "logname.log"
        self.debuglogfilename = "debuglogname.log"

        #from time import sleep
        #sleep(10)
        
        # If it exists, delete log file
        if (os.path.isfile(self.logfilename)):
            os.remove(self.logfilename)
        if (os.path.isfile(self.debuglogfilename)):
            os.remove(self.debuglogfilename)
        

    def tearDown(self):
        # If it exists, delete log file
        if (os.path.isfile(self.logfilename)):
            os.remove(self.logfilename)
        if (os.path.isfile(self.debuglogfilename)):
            os.remove(self.debuglogfilename)


    def test_log_setup(self):
        # Initialize
        module = AtlanticWaveModule(__name__,
                                    self.logfilename,
                                    self.debuglogfilename)

        # Check Logfile
        with LogCapture() as l:
            module.logger.warning("Test1")
            module.dlogger.error("Test2")

            l.check((__name__, 'WARNING', "Test1"),
                    ("debug."+__name__, 'ERROR', "Test2"))
        del module

    def test_dlogger_tb_LogCapture(self):
        try:
            self.exception_thrower()
        except Exception as e:
            
            with LogCapture() as l:
                module = AtlanticWaveModule(__name__,
                                            self.logfilename,
                                            self.debuglogfilename)

                module.dlogger_tb()
                
                self.assertEquals(("Traceback: id: " in str(l)), True)
                del module

    def test_exception_tb_LogCapture(self):
        try:
            self.exception_thrower()
        except Exception as e:
            with LogCapture() as l:
                module = AtlanticWaveModule(__name__,
                                            self.logfilename,
                                            self.debuglogfilename)

                module.exception_tb(e)

                self.assertEquals(("Exception " in str(l)), True)
                del module

    def exception_thrower(self):
        # Throw an exception to be caught.
        raise Exception("Dummy Exception, for testing")

class DBSetupTest(unittest.TestCase):
    def setUp(self):
        self.test_good_db = "good.db"
        self.test_memory_db = ":memory:"
        self.test_bad_db =  "bad.db"
        self.logfilename = os.getcwd() + "logfilename.log"
        self.debuglogfilename = os.getcwd() + "debuglogfilename.log"

        # If it exists, delete log file
        if (os.path.isfile(self.logfilename)):
            os.remove(self.logfilename)
        if (os.path.isfile(self.debuglogfilename)):
            os.remove(self.debuglogfilename)

        # If it exists, delete existing database
        if (os.path.isfile(self.test_good_db)):
            os.remove(self.test_good_db)
        if (os.path.isfile(self.test_bad_db)):
            os.remove(self.test_bad_db)

            
    def atearDown(self):
        # If it exists, delete log file
        if (os.path.isfile(self.logfilename)):
            os.remove(self.logfilename)

        # If it exists, delete existing database
        if (os.path.isfile(self.test_good_db)):
            os.remove(self.test_good_db)
        if (os.path.isfile(self.test_bad_db)):
            os.remove(self.test_bad_db)

            
    
    def test_good_db_setup_in_memory(self):
        key = 'a'
        value = 'b'
        db_location = self.test_memory_db
        module = AtlanticWaveModule(__name__,
                                    self.logfilename,
                                    self.debuglogfilename)
    
        # Create a new DB        
        module._initialize_db(db_location,
                              [('key_table','keys')],
                              True)
        keys = module.key_table.find()
        count = 0
        for k in keys:
            count += 1
        self.assertEqual(count, 0)
        
        # install new line
        module.key_table.insert({"key": key,
                                 "value": value})
        
        # Delete example module
        del module
        
        # Reconnect to DB
        module2 = AtlanticWaveModule(__name__,
                                     self.logfilename,
                                     self.debuglogfilename)
    
        module2._initialize_db(db_location,
                               [('key_table','keys')])
        keys = module2.key_table.find()
        count = 0
        for k in keys:
            count += 1
        # DB should be empty: it's in-memory and not persistant.
        self.assertEqual(count, 0)
        del module2
        
        
        
    def test_good_db_setup_static_file(self):
        key = "a"
        value = "b"
        db_location = self.test_good_db
        module = AtlanticWaveModule(__name__,
                                    self.logfilename,
                                    self.debuglogfilename)
    
        # Create a new DB        
        module._initialize_db(db_location,
                              [('key_table','keys')])
        keys = module.key_table.find()
        count = 0
        for k in keys:
            count += 1
        self.assertEqual(count, 0)
        
        # install new line
        module.key_table.insert({"key": key,
                                 "value": value})
        
        # Delete example module
        del module
        
        # Reconnect to DB
        module2 = AtlanticWaveModule(__name__,
                                     self.logfilename,
                                     self.debuglogfilename)
    
        module2._initialize_db(db_location,
                               [('key_table','keys')])
        keys = module2.key_table.find()
        count = 0
        for k in keys:
            count += 1

        # DB should have the same key:value stored. This is persistant.
        self.assertEqual(count, 1)
        
        # Check value
        entry = module2.key_table.find_one()
        self.assertNotEqual(entry, None)
        self.assertEqual(entry['key'], key)
        self.assertEqual(entry['value'], value)
        del module2


                            
        
if __name__ == '__main__':
    unittest.main()
