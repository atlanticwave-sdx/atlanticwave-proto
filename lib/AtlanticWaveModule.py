from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals
# Copyright 2018 - Sean Donovan
# AtlanticWave/SDX Project


# This provides a base class for many different parts of the AtlanticWave/SDX
# project. It contains Singleton functionality (since all modules are
# singletons) and logging/debugging facilities that are commonly used.

from builtins import hex
from builtins import str
from builtins import object
from lib.Singleton import Singleton
import logging
import dataset
import os
import sys
from traceback import format_stack
from future.utils import with_metaclass

class AtlanticWaveModuleValueError(ValueError):
    pass

class AtlanticWaveModuleTypeError(TypeError):
    pass

class AtlanticWaveModule(with_metaclass(Singleton, object)):
    def __init__(self, loggerid, logfilename=None, debuglogfilename=None):
        ''' Takes two mandatory parameters to properly setup logging, with one
            optional parameter for secondary logging:
              loggerid - name to log under.
              logfilename - filename of the logfile to be contributing to. 
                This will likely be an application level log file.
              debuglogfilename - If debug logs are wanted, this optional 
                parameter should be set. If debug logs are not desired, 
                leave as None.
        '''

        super(AtlanticWaveModule, self).__init__()
        
        # Check inputs
        if (logfilename != None):
            if (logfilename == debuglogfilename):
                raise AtlanticWaveModuleValueError(
                    "logfilename and debuglogfilename must be different: %s" %
                    logfilename)
            if debuglogfilename == None:
                debuglogfilename = "debug" + logfilename

        # Setup loggers
        self._setup_loggers(loggerid, logfilename, debuglogfilename)
        

    def _setup_loggers(self, loggerid, logfilename=None, debuglogfilename=None):
        ''' Internal function for setting up the logger formats. '''
        # reused from https://github.com/sdonovan1985/netassay-ryu/blob/master/base/mcm.py
        # Modified based on https://stackoverflow.com/questions/7173033/
        logging.basicConfig()
        self.logger = logging.getLogger(loggerid)
        self.dlogger = logging.getLogger("debug." + loggerid)
        if logfilename != None:
            formatter = logging.Formatter('%(asctime)s %(name)-12s: %(thread)s %(levelname)-8s %(message)s')
            console = logging.StreamHandler()
            console.setLevel(logging.DEBUG)
            console.setFormatter(formatter)
            logfile = logging.FileHandler(logfilename)
            logfile.setLevel(logging.DEBUG)
            logfile.setFormatter(formatter)
            self.logger.setLevel(logging.DEBUG)
            self.logger.addHandler(console)
            self.logger.addHandler(logfile)

        if debuglogfilename != None:
            formatter = logging.Formatter('%(asctime)s %(name)-12s: %(thread)s %(levelname)-8s %(message)s')
            console = logging.StreamHandler()
            console.setLevel(logging.DEBUG)
            console.setFormatter(formatter)
            logfile = logging.FileHandler(debuglogfilename)
            logfile.setLevel(logging.DEBUG)
            logfile.setFormatter(formatter)
            self.dlogger.setLevel(logging.DEBUG)
            self.dlogger.addHandler(console)
            self.dlogger.addHandler(logfile)

    def dlogger_tb(self):
        ''' Print out the current traceback. '''
        tbs = format_stack()
        all_tb = "Traceback: id: %s\n" % str(hex(id(self)))
        for line in tbs:
            all_tb = all_tb + line
        self.dlogger.warning(all_tb)

    def exception_tb(self, e):
        ''' Print out current error. '''
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        lineno = exc_tb.tb_lineno
        self.dlogger.warning("Exception %s at %s:%d" % (str(e), filename,
                                                        lineno))

    def _initialize_db(self, db_filename, db_tables_tuples,
                       print_table_on_load=False):
        # A lot of modules will need DB access for storing data, but some use a
        # DB for storing configuration information as well. This is *optional*
        # to use, which is why it's not part of __init__()
        # Details on the setup:
        # https://dataset.readthedocs.io/en/latest/api.html
        # https://github.com/g2p/bedup/issues/38#issuecomment-43703630
        self.logger.critical("Connection to DB: %s" % db_filename)
        self.db = dataset.connect('sqlite:///' + db_filename, 
                                  engine_kwargs={'connect_args':
                                                 {'check_same_thread':False}})

        #Try loading the tables, if they don't exist, create them.
        for (name, table) in db_tables_tuples:
            if table in self.db: #https://github.com/pudo/dataset/issues/281
                self.logger.info("Trying to load %s from DB" % name)
                t = self.db.load_table(table)
                if print_table_on_load:
                    entries = t.find()
                    print("\n\n&&&&& ENTRIES in %s &&&&&" % name)
                    for e in entries:
                        print("\n%s" % str(e))
                    print("&&&&& END ENTRIES &&&&&\n\n")
                    
                setattr(self, name, t)
                
            else:
                # If load_table() fails, that's fine! It means that the
                # table doesn't yet exist. So, create it.
                self.logger.info("Failed to load %s from DB, creating table" %
                                 name)
                t = self.db[table]
                setattr(self, name, t)
