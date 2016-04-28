# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


import logging
import threading
from shared.Singleton import Singleton
from RyuControllerInterface import *
from shared.SDXControllerConnectionManager import *
from shared.Connection import select


class LocalController(object):
    ''' The Local Controller is responsible for passing messages from the SDX 
        Controller to the switch. It needs two connections to both the SDX 
        controller and switch(es). ''' 
    __metaclass__ = Singleton

    def __init__(self):
        # Setup logger
        self._setup_logger()

        # Setup switch
        self.switch_connection = RyuControllerInterface()
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
                readable, writable, exceptional = select(rlist,
                                                         wlist,
                                                         xlist)
            except Error as e:
                self.logger.error("Error in select - %s" % (e))
                

            # Loop through readable
            for entry in readable:
                if entry == self.sdx_connection:
                    self.logger.debug("Receiving Command on sdx_connection")
                    cmd, data = self.sdx_connection.recv_cmd()
                    self.logger.debug("Received : %s:%s" % (cmd, data))
                    if cmd == SDX_NEW_RULE:
                        self.switch_connection.send_command(data)
                    elif cmd == SDX_RM_RULE:
                        self.switch_connection.remove_rule(data)
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

    def start_sdx_controller_connection(self):
        self.logger.debug("About to open SDX Controller Connection to %s:%s" % (IPADDR, PORT))
        self.sdx_connection = self.sdx_cm.open_outbound_connection(IPADDR, PORT)
        self.logger.debug("SDX Controller Connection - %s" % (self.sdx_connection))

    def start_switch_connection(self):
        pass

    def sdx_message_callback(self):
        pass
    # Is this necessary?

if __name__ == '__main__':
    LocalController()
