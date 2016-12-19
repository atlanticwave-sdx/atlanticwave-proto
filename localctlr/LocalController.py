# Copyrightg 2016 - Sean Donovan
# AtlanticWave/SDX Project


import logging
import threading
import sys
import json

from shared.Singleton import SingletonMixin
from RyuControllerInterface import *
from shared.SDXControllerConnectionManager import *
from shared.Connection import select

# Types of rules that need translation
from shared.LCRule import *
from shared.VlanTunnelLCRule import *
from shared.MatchActionLCRule import *

LOCALHOST = "127.0.0.1"
DEFAULT_RYU_CXN_PORT = 55767
DEFAULT_OPENFLOW_PORT = 6633


class LocalController(SingletonMixin):
    ''' The Local Controller is responsible for passing messages from the SDX 
        Controller to the switch. It needs two connections to both the SDX 
        controller and switch(es).
        Singleton. ''' 

    def __init__(self, runloop=False, name=None, manifest_filename=None):
        # Setup logger
        self._setup_logger()
        self.name = name
        self.logger.info("LocalController %s starting", self.name)

        # Import configuration information
        self.lcip = LOCALHOST
        self.ryu_cxn_port = DEFAULT_RYU_CXN_PORT
        self.openflow_port = DEFAULT_OPENFLOW_PORT
        if manifest_filename != None:
            self._import_configuration(manifest_filename)

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
                readable, writable, exceptional = select(rlist,
                                                         wlist,
                                                         xlist)
            except Exception as e:
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

    def _import_configuration(self, manifest_filename):
        with open(manifest_filename) as data_file:
            data = json.load(data_file)

        # Look at information under the self.name entry
        lcdata = data['localcontrollers'][self.name]
        self.lcip = lcdata['lcip']
        self.ryu_cxn_port = lcdata['internalconfig']['ryucxninternalport']
        self.openflow_port = lcdata['internalconfig']['openflowport']

    def start_sdx_controller_connection(self):
        self.logger.debug("About to open SDX Controller Connection to %s:%s" % (IPADDR, PORT))
        self.sdx_connection = self.sdx_cm.open_outbound_connection(IPADDR, PORT)
        self.logger.debug("SDX Controller Connection - %s" % (self.sdx_connection))
        # Send name
        self.sdx_connection.send(self.name)

        # FIXME: Credentials exchange

    def start_switch_connection(self):
        pass

    def sdx_message_callback(self):
        pass
    # Is this necessary?


    def _translate_to_OF(self, lcrule):
        ''' This translates from LCRules to OFRules. All the following functions 
            are helpers for this. '''

        # Verify input
        if not isinstance(lcrule, LCRule):
            raise TypeError("lcrule %s is not of type LCRule: %s" %
                            (lcrule, type(lcrule)))

        # Switch based on actual type
        results = None
        if type(lcrule) == MatchActionLCRule:
            results = self._translate_MatchActionLCRule(lcrule)

        elif type(lcrule) == VlanTunnelLCRule:
            results = self._translate_VlanTunnelLCRule(lcrule)

        # Return translated rule.
        return results

    def _translate_MatchActionLCRule(self, marule):
        matchlist = []
        actionlist = []

        # Translate all the matches
        xlated_match = self._translate_LCMatch(marule.get_matches(),
                                               marule.get_ingress())

        # Translate all the actions
        xlated_actions = self._translate_LCAction(marule.get_actions(),
                                                  marule.get_ingress())

        # Build the instruction
        instruction = instruction_APPLY_ACTIONS(xlated_actions)
        table = None #FIXME
        priority = None #FIXME
        cookie = None #FIXME
        switch_id = marule.get_switch_id()

        # Build the OpenFlowRule
        rule = OpenFlowRule(xlated_match, instruction, 
        

                
        pass
        
    def _translate_VlanLCRule(self, vlanrule):
        # Create outbound rule

        # If bidirectional, create inbound rule

        #FIXME: Bandwidth management stuff
        

        pass

    def _translate_LCMatch(self, lcmatches, ingress):
        # for each match:

        # Augment the matches with all the prereqs
        # If there's a prereq in conflict (i.e., user specified somethign in the 
        # same field, there's a problem, raise an error).

        
        pass


    def _translate_LCAction(self, lcactions, ingress):
        # for each action:
        
        # translate to appropriate action type.
        pass

    def _translate_LCField(self, type, value):
        # Figure out the correct class, and fill it in
        pass


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print "USAGE: python LocalController.py LCName manifest_file"
        print "The local controller must be given a name if running from the command line."
        print "The local controller must be given a manifest file for configuration information if running from the command line."
        exit()
    name = sys.argv[1]
    manifest = sys.argv[2]
    lc = LocalController(False, name, manifest)
    lc._main_loop()
