# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


import logging
import threading
import sys
import Queue

from shared.Singleton import Singleton
from shared.SDXControllerConnectionManager import *
from shared.Connection import select
from shared.UserRule import UserRuleBreakdown
from AuthenticationInspector import *
from AuthorizationInspector import *
from BreakdownEngine import *
from LocalControllerManager import *
from ParticipantManager import *
from RestAPI import *
from RuleManager import *
from RuleRegistry import *
from TopologyManager import *
from ValidityInspector import *


class SDXControllerError(Exception):
    ''' Parent class, can be used as a catch-all for other errors '''
    pass

class SDXControllerConnectionError(SDXControllerError):
    ''' When there's an error with a connection. '''
    pass

class SDXController(object):
    ''' This is the main coordinating module of the SDX controller. It mostly 
        provides startup and coordination, rathe rthan performan many actions by
        itself.
        Singleton. ''' 
    __metaclass__ = Singleton

    # Connection Queue actions defininition
    NEW_CXN = "New Connection"
    DEL_CXN = "Remove Connection"

    def __init__(self):
        ''' The bulk of the work happens here. This initializes nearly everything
            and starts up the main processing loop for the entire SDX
            Controller. '''
        # Initialize all the modules - Ordering is relatively important here
        self.aci = AuthenticationInspector()
        self.azi = AuthorizationInspector()
        self.be = BreakdownEngine()
        self.rr = RuleRegistry()
        self.tm = TopologyManager()
        self.vi = ValidityInspector()
        self.pm = ParticipantManager()
        self.lcm = LocalControllerManager()

        # Start these modules last!
        self.rm = RuleManager(self.send_breakdown_rule_add,
                              self.send_breakdown_rule_rm)
        self.rapi = RestAPI()
        self.pm = ParticipantManager()      #FIXME - Filename
        self.lcm = LocalControllerManager() #FIXME - Filename

        # Set up the connection-related nonsense - Have a connection event queue
        self.ip = IPADDR        # from share.SDXControllerConnectionManager
        self.port = PORT
        self.cxn_q = Queue.Queue()
        self.connections = {}
        self.sdx_cm = SDXControllerConnectionManager()
        self.cm_thread = threading.Thread(target=self._cm_thread)
        self.cm_thread.daemon = True
        self.cm_thread.start()
        
        # Go to main loop 
        pass

    def _setup_logger(self):
        ''' Internal function for setting up the logger formats. '''
        # reused from https://github.com/sdonovan1985/netassay-ryu/blob/master/base/mcm.py
        formatter = logging.Formatter('%(asctime)s %(name)-12s: %(levelname)-8s %(message)s')
        console = logging.StreamHandler()
        console.setLevel(logging.WARNING)
        console.setFormatter(formatter)
        logfile = logging.FileHandler('sdxcontroller.log')
        logfile.setLevel(logging.DEBUG)
        logfile.setFormatter(formatter)
        self.logger = logging.getLogger('sdxcontroller')
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(console)
        self.logger.addHandler(logfile)

    def _cm_thread(self):
        self.sdx_cm.new_connection_callback(self._handle_new_connection)
        self.sdx_cm.open_listening_port(self.ip, self.port)
        pass
        
    def _handle_new_connection(self, cxn):
        self.connections[cxn.get_address()] = cxn
        self.cxn_q.put((NEW_CXN, cxn))
        #FIXME: Send this to the LocalControllerManager

    def _handle_connection_loss(self, cxn):
        #FIXME: Send this to the LocalControllerManager
        pass


    def _main_loop(self):
        # Set up the select structures
        rlist = self.connections.values()
        wlist = []
        xlist = rlist
        timeout = .5

        # Main loop - Have a ~500ms timer on the select call to handle cxn events
        while True:
            # Handle event queue messages
            try:
                while not self.cxn_q.empty():
                    (action, cxn) = self.cxn_q.get(False)
                    if action == NEW_CXN:
                        if cxn in rlist:
                            # Already there. Weird, but OK
                            pass
                        rlist.append(cxn)
                        wlist = []
                        xlist = rlist
                        
                    elif action == DEL_CXN:
                        if cxn in rlist:
                            rlist.remove(cxn)
                            wlist = []
                            xlist = rlist
                            
            except Queue.Empty as e:
                # This is raised if the cxn_q is empty of events.
                # Normal behaviour
                pass
                

            
            # Dispatch messages as appropriate
            try: readable, writeable, exceptional = select(rlist,
                                                           wlist,
                                                           xlist,
                                                           timeout)
            except Error as e:
                self.logger.error("Error in select - %s" % (e))                


            # Loop through readable
            for entry in readable:
                cmx, data = entry.recv_cmd()
                
                if entry == self.sdx_connection:
                    self.logger.debug("Receiving Command on sdx_connection")
                    cmd, data = self.sdx_connection.recv_cmd()
                    self.logger.debug("Received : %s:%s" % (cmd, data))
                    if cmd == SDX_NEW_RULE:
                        pass
                    elif cmd == SDX_RM_RULE:
                        pass

                #elif?

            # Loop through writable
            for entry in writable:
                # Anything to do here?
                pass

            # Loop through exceptional
            for entry in exceptional:
                # FIXME: Handle connection failures
                pass
    def _send_breakdown_rule(self, bd, cmd):
        ''' Used by the callback functions (below) to actually perform the 
            sending of commands to the Local Controllers. This is all pretty
            much the same, with only the command changing. '''
        # The cmd is from the list of commands in  SDXControllerConnectionManager
        lc = bd.get_lc()
        if lc not in self.connections.keys():
            raise SDXControllerConnectionError("%s is not in the current connections." % lc)
        
        lc_cxn = self.connections[lc]

        for rule in bd.get_list_of_rules():
            lc_cxn.send_cmd(cmd, rule)

        
    def send_breakdown_rule_add(self, bd):
        ''' This takes in a UserRuleBreakdown and send it to the Local Controller
            that it has a connection to in order to add rules. '''
        try:
            self._send_breakdown_rule(bd, SDX_NEW_RULE)
        except Exception as e: raise

    def send_breakdown_rule_rm(self, bd):
        ''' This takes in a UserRuleBreakdown and send it to the Local Controller
            that it has a connection to in order to remove rules. '''
        try:
            self._send_breakdown_rule(bd, SDX_RM_RULE)
        except Exception as e: raise
