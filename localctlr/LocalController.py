# Copyrightg 2016 - Sean Donovan
# AtlanticWave/SDX Project


import logging
import threading
import sys
import json

from lib.Singleton import SingletonMixin
from lib.Connection import select as cxnselect
from RyuControllerInterface import *
from shared.SDXControllerConnectionManager import *

LOCALHOST = "127.0.0.1"
DEFAULT_RYU_CXN_PORT = 55767
DEFAULT_OPENFLOW_PORT = 6633


class LocalController(SingletonMixin):
    ''' The Local Controller is responsible for passing messages from the SDX 
        Controller to the switch. It needs two connections to both the SDX 
        controller and switch(es).
        Singleton. ''' 

    def __init__(self, runloop=False, options=None):
        # Setup logger
        self._setup_logger()
        self.name = options.name
        self.logger.info("LocalController %s starting", self.name)

        # Parse out the options
        # Import configuration information
        self.manifest = options.manifest
        self.sdxip = options.host
        self.sdxport = options.sdxport

        self.lcip = LOCALHOST
        self.ryu_cxn_port = DEFAULT_RYU_CXN_PORT
        self.openflow_port = DEFAULT_OPENFLOW_PORT
        if self.manifest != None:
            self._import_configuration()

        # Setup switch
        self.switch_connection = RyuControllerInterface(self.lcip,
                                                        self.ryu_cxn_port,
                                                        self.openflow_port)
        self.logger.info("RyuControllerInterface setup finish.")

        # Setup connection manager
        self.sdx_cm = SDXControllerConnectionManager()
        self.sdx_connection = None
        self.logger.info("SDXControllerConnectionManager setup finish.")
        self.logger.debug("SDXControllerConnectionManager - %s" % (self.sdx_cm))

        # Start connections:
        self.start_switch_connection()
        self.start_sdx_controller_connection() # Blocking call
        self.logger.info("SDX Controller Connection established.")

        # Start main loop
        if runloop:
            self.start_main_loop()
            self.logger.info("Main Loop started.")

    def start_main_loop(self):
        self.main_loop_thread = threading.Thread(target=self._main_loop)
        self.main_loop_thread.daemon = True
        self.main_loop_thread.start()
        self.logger.debug("Main Loop - %s" % (self.main_loop_thread))
        
    def _main_loop(self):
        ''' This is the main loop for the Local Controller. User should call 
            start_main_loop() to start it. ''' 
        rlist = [self.sdx_connection]
        wlist = []
        xlist = rlist

        self.logger.debug("Inside Main Loop, SDX connection: %s" % (self.sdx_connection))

        while(True):
            # Based, in part, on https://pymotw.com/2/select/
            try:
                readable, writable, exceptional = cxnselect(rlist,
                                                         wlist,
                                                         xlist)
            except Exception as e:
                self.logger.error("Error in select - %s" % (e))
                

            # Loop through readable
            for entry in readable:
                if entry == self.sdx_connection:
                    self.logger.debug("Receiving Command on sdx_connection")
                    cmd, data = self.sdx_connection.recv_cmd()
                    (switch_id, cmddata) = data
                    self.logger.debug("Received : %s:%s" % (cmd, data))
                    if cmd == SDX_NEW_RULE:
                        self.switch_connection.send_command(switch_id, cmddata)
                    elif cmd == SDX_RM_RULE:
                        self.switch_connection.remove_rule(switch_id, cmddata)
                    self.logger.debug("Sent     : %s:%s" % (cmd, data))

                #elif?

            # Loop through writable
            for entry in writable:
                # Anything to do here?
                pass

            # Loop through exceptional
            for entry in exceptional:
                # FIXME: Handle connection failures
                pass
        

        
    def _setup_logger(self):
        ''' Internal function for setting up the logger formats. '''
        # reused from https://github.com/sdonovan1985/netassay-ryu/blob/master/base/mcm.py
        formatter = logging.Formatter('%(asctime)s %(name)-12s: %(levelname)-8s %(message)s')
        console = logging.StreamHandler()
        console.setLevel(logging.WARNING)
        console.setFormatter(formatter)
        logfile = logging.FileHandler('localcontroller.log')
        logfile.setLevel(logging.DEBUG)
        logfile.setFormatter(formatter)
        self.logger = logging.getLogger('localcontroller')
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(console)
        self.logger.addHandler(logfile) 

    def _import_configuration(self):
        with open(self.manifest) as data_file:
            data = json.load(data_file)

        # Look at information under the self.name entry
        lcdata = data['localcontrollers'][self.name]
        self.lcip = lcdata['lcip']
        self.ryu_cxn_port = lcdata['internalconfig']['ryucxninternalport']
        self.openflow_port = lcdata['internalconfig']['openflowport']

    def start_sdx_controller_connection(self):
        self.logger.debug("About to open SDX Controller Connection to %s:%s" % 
                          (self.sdxip, self.sdxport))
        self.sdx_connection = self.sdx_cm.open_outbound_connection(self.sdxip, 
                                                                   self.sdxport)
        self.logger.debug("SDX Controller Connection - %s" % 
                          (self.sdx_connection))
        # Send name
        self.sdx_connection.send_cmd(SDX_IDENTIFY, self.name)

        # FIXME: Credentials exchange

    def start_switch_connection(self):
        pass

    def sdx_message_callback(self):
        pass
    # Is this necessary?

if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("-m", "--manifest", dest="manifest", type=str,
                        action="store", help="specifies the manifest")
    parser.add_argument("-n", "--name", dest="name", type=str,
                        action="store", help="Specify the name of the LC")
    parser.add_argument("-H", "--host", dest="host", default=IPADDR,
                        action="store", type=str, 
                        help="IP address of SDX Controller")
    parser.add_argument("-p", "--port", dest="sdxport", default=PORT, 
                        action="store", type=int, 
                        help="Port number of SDX Controller")

    options = parser.parse_args()
    print options

    if not options.manifest or not options.name:
        parser.print_help()
        exit()

    lc = LocalController(False, options)
    lc._main_loop()

