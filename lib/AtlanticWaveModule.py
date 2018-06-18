# Copyright 2018 - Sean Donovan
# AtlanticWave/SDX Project


# This provides a base class for many different parts of the AtlanticWave/SDX
# project. It contains Singleton functionality (since all modules are
# singletons) and logging/debugging facilities that are commonly used.

from Singleton import Singleton
import logging
import dataset
from traceback import format_stack

class AtlanticWaveModuleValueError(ValueError):
    pass

class AtlanticWaveModuleTypeError(TypeError):
    pass

class AtlanticWaveModule(object):
    __metaclass__ = Singleton

    def __init__(self, loggerid, logfilename, debuglogfilename=None):
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
        if logfilename == debuglogfilename:
            raise AtlanticWaveModuleValueError(
                "logfilename and debuglogfilename must be different: %s" %
                logfilename)
        if logfilename == None:
            raise AtlanticWaveModuleValueError(
                "logfilename must not be None: %s" % logfilename)

        # Setup logger
        self._setup_logger(loggerid, logfilename)
        
        # if debuglogfilename is None, sent to /tmp/<logfilename.debug>,
        # Setup debug logger
        if debuglogfilename == None:
            debuglogfilename = "/tmp/" + logfilename + ".debug"
        self._setup_debug_logger(loggerid, debuglogfilename)
        

    def _setup_logger(self, loggerid, logfilename):
        ''' Internal function for setting up the logger formats. '''
        # reused from https://github.com/sdonovan1985/netassay-ryu/blob/master/base/mcm.py
        formatter = logging.Formatter('%(asctime)s %(name)-12s: %(thread)s %(levelname)-8s %(message)s')
        console = logging.StreamHandler()
        console.setLevel(logging.WARNING)
        console.setFormatter(formatter)
        logfile = logging.FileHandler(logfilename)
        logfile.setLevel(logging.DEBUG)
        logfile.setFormatter(formatter)
        self.logger = logging.getLogger(loggerid)
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(console)
        self.logger.addHandler(logfile)

    def _setup_debug_logger(self, loggerid, debuglogfilename):
        ''' Internal function for setting up the logger formats. '''
        # This is from LocalController
        # reused from https://github.com/sdonovan1985/netassay-ryu/blob/master/base/mcm.py
        formatter = logging.Formatter('%(asctime)s %(name)-12s: %(thread)s %(levelname)-8s %(message)s')
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        console.setFormatter(formatter)
        logfile = logging.FileHandler(debuglogfilename)
        logfile.setLevel(logging.DEBUG)
        logfile.setFormatter(formatter)
        self.dlogger = logging.getLogger(loggerid)
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

    def _initialize_db(self, db_filename, db_tables_tuples):
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
            try:
                self.logger.info("Trying to load %s from DB" % name)
                t = self.db.load_table(table)
                setattr(self, name, t)
            except:
                # If load_table() fails, that's fine! It means that the
                # table doesn't yet exist. So, create it.
                self.logger.info("Failed to load %s from DB, creating table" %
                                 name)
                t = self.db[table]
                setattr(self, name, t)
