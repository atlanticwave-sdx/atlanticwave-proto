# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


import logging
import threading
import sys
from shared.Singleton import Singleton
from shared.SDXControllerConnectionManager import *
from config_parser.config_parser import *



class ConfigParserCtlr(object):
    ''' This is a version of the remote controller that uses only the config
        parser to populate the switches. '''
    __metaclass__ = Singleton

    def __init__(self, filename):
        # Setup logger
        self._setup_logger()
        self.ip = IPADDR        # from share.SDXControllerConnectioNmanager
        self.port = PORT

        # Read configuration
        self.config_parser = ConfigurationParser()
        self.configuration = self.config_parser.parse_configuration_file(filename)

        print self.configuration
        
        # Setup listening connection
        self.sdx_cm = SDXControllerConnectionManager()
        self.sdx_cm.new_connection_callback(self.connection_cb)
        self.sdx_cm.open_listening_port(self.ip, self.port)


    def connection_cb(self, cxn):
        # Got a connection, send the configuration over.
        for entry in self.configuration:
            cxn.send_cmd(SDX_NEW_RULE, cmd) 
        
        # Close connection
        cxn.close


    def _setup_logger(self):
        ''' Internal function for setting up the logger formats. '''
        # reused from https://github.com/sdonovan1985/netassay-ryu/blob/master/base/mcm.py
        formatter = logging.Formatter('%(asctime)s %(name)-12s: %(levelname)-8s %(message)s')
        console = logging.StreamHandler()
        console.setLevel(logging.WARNING)
        console.setFormatter(formatter)
        logfile = logging.FileHandler('config_parser_ctlr.log')
        logfile.setLevel(logging.DEBUG)
        logfile.setFormatter(formatter)
        self.logger = logging.getLogger('config_parser_ctlr')
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(console)
        self.logger.addHandler(logfile) 

if __name__ == '__main__':
    ConfigParserCtlr(sys.argv[1])
