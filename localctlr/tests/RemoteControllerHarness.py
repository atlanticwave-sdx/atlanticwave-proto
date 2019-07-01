# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


from shared.SDXControllerConnectionManager import *
from lib.Connection import *
from lib.Singleton import Singleton
import threading

#from shared.OpenFlowRule import OpenFlowRule as OFR
#from shared.match import *
#from shared.action import *
#from shared.instruction import *
#from shared.offield import *

from shared.SDXPolicy import *
from shared.SDXMatches import *
from shared.SDXActions import *

class RemoteControllerHarness(object):
    ''' Harness for local controller testing. '''
    __metaclass__ = Singleton

    def __init__(self):
        # Create useful examples
        self.examples = []
        self.examples.append(SDXIngressPolicy('dummy',
            '{"SDXIngress":{
            "starttime":"1985-04-12T23:20:50",
            "endtime":"2085-04-12T23:20:50",
            "switch":"atl-switch",
            "matches":[DSTMAC("00:00:00:00:00:00")],
            "actions":[ModifyDSTMAC("00:00:00:00:00:02")]}
            }'))
                             
        #self.examples.append(OFR(OpenFlowMatch([ETH_DST("00:00:00:00:00:01")]),
        #                         instruction_APPLY_ACTIONS([action_SET_FIELD(ETH_DST("00:00:00:00:00:02"))])))

        self.examples.append(SDXIngressPolicy('dummy',
            '{"SDXEgress":{
            "starttime":"1985-04-12T23:20:50",
            "endtime":"2085-04-12T23:20:50",
            "switch":"atl-switch",
            "matches":[ETHTYPE(0x0800), SRCIP("1.2.3.4")],
            "actions":[ModifySRCIP("2.3.4.5")]}
            }'))
        #self.examples.append(OFR(OpenFlowMatch([ETH_TYPE(0x0800), 
        #                                        IPV4_SRC("1.2.3.4")]),
        #                         instruction_APPLY_ACTIONS([action_SET_FIELD(IPV4_DST("2.3.4.5"))])))

        self.examples.append(SDXIngressPolicy('dummy',
            '{"SDXEgress":{
            "starttime":"1985-04-12T23:20:50",
            "endtime":"2085-04-12T23:20:50",
            "switch":"atl-switch",
            "matches":[DSTMAC("00:00:00:00:00:03"),
                       ETHTYPE(0x0800), 
                       SRCIP("3.4.5.6")],
            "actions":[ModifySRCMAC("00:00:00:00:00:04")]}
            }'))
        #self.examples.append(OFR(OpenFlowMatch([ETH_DST("00:00:00:00:00:03"), 
        #                                        ETH_TYPE(0x0800), 
        #                                        IPV4_SRC("3.4.5.6")]),
        #                         instruction_APPLY_ACTIONS([action_SET_FIELD(ETH_SRC("00:00:00:00:00:04"))])))

        self.examples.append(SDXIngressPolicy('dummy',
            '{"SDXEgress":{
            "starttime":"1985-04-12T23:20:50",
            "endtime":"2085-04-12T23:20:50",
            "switch":"atl-switch",
            "matches":[DSTMAC("00:00:00:00:00:05"),
                       ETHTYPE(0x0800), 
                       SRCIP("4.5.6.7")],
            "actions":[ModifySRCMAC("00:00:00:00:00:04"),
                       DSTIP("5.6.7.8")]}
            }'))
        #self.examples.append(OFR(OpenFlowMatch([ETH_DST("00:00:00:00:00:05"),
        #                                        ETH_TYPE(0x0800),
        #                                        IPV4_SRC("4.5.6.7")]),
        #                         instruction_APPLY_ACTIONS([action_SET_FIELD(ETH_SRC("00:00:00:00:00:04")),
        #                                                    action_SET_FIELD(IPV4_DST("5.6.7.8"))])))
        
        self.examples.append(SDXIngressPolicy('dummy',
            '{"SDXEgress":{
            "starttime":"1985-04-12T23:20:50",
            "endtime":"2085-04-12T23:20:50",
            "switch":"atl-switch",
            "matches":[IPPROTO(6),
                       ETHTYPE(0x0800)],
            "actions":[Forward1)]}
            }'))
        #self.examples.append(OFR(OpenFlowMatch([IP_PROTO(6),
        #                                        ETH_TYPE(0x0800)]),
#                                 instruction_WRITE_ACTIONS([action_OUTPUT(1)]),
        #                         instruction_APPLY_ACTIONS([action_OUTPUT(1)]),
        #                         priority=123,
        #                         cookie=1234,
        #                         table=1,
        #                         switch_id=1))
                                               
                                                
        # Set up connection
        self.ip = IPADDR
        self.port = PORT
        self.client = None
        self.cm = SDXControllerConnectionManager()
        self.cm_thread = threading.Thread(target=self._cm_thread)
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
        self.client.send_cmd(SDX_NEW_RULE, cmd)

    def send_rm_command(self, cmd):
        self.client.send_cmd(SDX_RM_RULE, cmd)

    
