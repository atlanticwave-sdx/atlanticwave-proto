# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


from shared.SDXControllerConnectionManager import *
from shared.Connection import *
from shared.Singleton import Singleton
import threading

from shared.OpenFlowRule import OpenFlowRule as OFR
from shared.match import *
from shared.action import *
from shared.instruction import *
from shared.offield import *

class RemoteControllerHarness(object):
    ''' Harness for local controller testing. '''
    __metaclass__ = Singleton

    def __init__(self):
        # Create useful examples
        self.examples = []
        self.examples.append(OFR(OpenFlowMatch([ETH_DST("00:00:00:00:00:01")]),
                                 instruction_APPLY_ACTIONS([action_SET_FIELD(ETH_DST("00:00:00:00:00:02"))])))
        self.examples.append(OFR(OpenFlowMatch([IP_SRC("1.2.3.4")]),
                                 instruction_APPLY_ACTIONS([action_SET_FIELD(IP_DST("2.3.4.5"))])))
        self.examples.append(OFR(OpenFlowMatch([ETH_DST("00:00:00:00:00:03"),
                                                IP_SRC("3.4.5.6")]),
                                 instruction_APPLY_ACTIONS([action_SET_FIELD(ETH_SRC("00:00:00:00:00:04"))])))
        self.examples.append(OFR(OpenFlowMatch([ETH_DST("00:00:00:00:00:05"),
                                                IP_SRC("4.5.6.7")]),
                                 instruction_APPLY_ACTIONS([action_SET_FIELD(ETH_SRC("00:00:00:00:00:04")),
                                                            action_SET_FIELD(IP_DST("5.6.7.8"))])))

                             
                             
        
        # Set up connection
        self.ip = IPADDR
        self.port = PORT
        self.client = None
        self.cm = SDXControllerConnectionManager()
        self.cm_thread = threading.Thread(self._cm_thread)
        self.cm_thread.daemon = True
        self.cm_thread.start()

    def _cm_thread(self):
        self.cm.new_connection_callback(self.connection_cb)
        self.cm.open_listening_port(self.ip, self.port)

    def connection_cb(self, cxn):
        self.client = cxn
            
    def is_connected(self):
        # figure out if connected
        return (self.client != None)

    def send_new_command(self, cmd):
        self.cxn.send_cmd(SDX_NEW_RULE, cmd)

    def send_rm_command(self, cmd):
        self.cxn.send_cmd(SDX_RM_RULE, cmd)

    
