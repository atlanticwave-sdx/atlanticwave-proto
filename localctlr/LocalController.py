# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


import logging
import threading
from shared.Singleton import Singleton
from SDXControllerConnectionManager import *
from RyuControllerInterface import *
from shared.Connection import select



# FIXME: this needs to be figured out.
IPADDR = '127.0.0.1'
PORT = 5555

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

        # Setup connection manager
        self.sdx_connection = SDXControllerConnectionManager()


        # Start connections:
        self.start_switch_connection()
        self.start_sdx_controller_connection()

    def start_main_loop(self):
        self.main_loop_thread = threading.Thread(target=self._main_loop)
        self.main_loop_thread.daemon = True
        self.main_loop_thread.start()
        
    def _main_loop(self):
        ''' This is the main loop for the Local Controller. User should call 
            start_main_loop() to start it. ''' 
        

        # Other thigns that need setting up
        self.mainloop = None

    def start(self):
        self.mainloop = threading.Thread(target=self._main_loop)
        self.mainloop.daemon = True
        self.mainloop.start()

    def _main_loop(self):
        # Main loop
        rlist = [self.sdx_connection]
        wlist = []
        xlist = rlist

        while(True):
            # Based, in part, on https://pymotw.com/2/select/
            readable, writable, exceptional = select(rlist,
                                                     wlist,
                                                     xlist)

            # Loop through readable
            for entry in readable:
                if entry == self.sdx_connection:
                    cmd = self.sdx_connection.recv()
                    self.switch_connection.send_command(cmd)
                #elif?

            # Loop through writable
            for entry in exceptional:
                # Handle connection failures
                pass

            # Loop through exceptional
            for entry in exceptional:
                # Handle connection failures
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
        self.sdx_connection.open_outbound_connection(IPADDR, PORT)

    def start_switch_connection(self):
        pass

    def sdx_message_callback(self):
        pass
    # Is this necessary?

if __name__ == '__main__':
    LocalController()
