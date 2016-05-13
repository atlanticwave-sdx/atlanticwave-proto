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

    def __init__(self):
        # Setup logger
        print "CONFIG PARSER CTLR"
        self._setup_logger()
        self.ip = IPADDR        # from share.SDXControllerConnectioNmanager
        self.port = PORT
        self.cxn = None

        self.config_parser = ConfigurationParser()
        
        # Setup listening connection
        self.sdx_cm = SDXControllerConnectionManager()
        self.cm_thread = threading.Thread(target=self._cm_thread)
        self.cm_thread.daemon = True
        self.cm_thread.start()
        print "CONFIG PARSER CTLR INITED"


    def _cm_thread(self):
        self.sdx_cm.new_connection_callback(self.connection_cb)
        self.sdx_cm.open_listening_port(self.ip, self.port)

    def is_connected(self):
        if self.cxn == None:
            return False
        return True


    def connection_cb(self, cxn):
        # Got a connection, send the configuration over.
        self.cxn = cxn


    def close_cxn(self):
        self.cxn.close()
        self.cxn = None

    def parse_configuration(self, value):
        self.configuration = self.config_parse.parse_configuration(value)

    def parse_configuration_file(self, filename):
        self.configuration = self.config_parser.parse_configuration_file(filename)

#        print self.configuration

    def run_configuration(self, action=SDX_NEW_RULE):
        # action could be changes to SDX_RM_RULE
        for entry in self.configuration:
            self.cxn.send_cmd(action, entry)


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
    cp = ConfigParserCtlr()
    cp.parse_configuration_file(sys.argv[1])
