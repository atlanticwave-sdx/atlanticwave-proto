from __future__ import print_function
# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


from shared.SDXControllerConnectionManager import *
from lib.Connection import select as cxnselect
from lib.Singleton import Singleton
from time import sleep
import threading
import os

#from shared.OpenFlowRule import OpenFlowRule as OFR
#from shared.match import *
#from shared.action import *
#from shared.instruction import *
#from shared.offield import *

from shared.SDXPolicy import *
from shared.SDXMatches import *
from shared.SDXActions import *

from shared.MatchActionLCRule import *
from shared.LCFields import *
from shared.LCAction import *

dummy_log = "Testing"

class RemoteControllerHarness(object):
    ''' Harness for local controller testing. '''
    __metaclass__ = Singleton

    def __init__(self):
        # Create useful examples
        self.examples = []

        rule = MatchActionLCRule(1, 
                                 [ETH_DST("00:00:00:00:00:00")],
                                 [SetField(ETH_DST("00:00:00:00:00:02"))])
        rule.set_cookie(100)
        self.examples.append(rule)
            
        rule = MatchActionLCRule(1,
                                 [ETH_TYPE(0x0800), IPV4_SRC("1.2.3.4")],
                                 [SetField(IPV4_SRC("2.3.4.5"))])
        rule.set_cookie(100)
        self.examples.append(rule)


        rule = MatchActionLCRule(1,
                                 [ETH_DST("00:00:00:00:00:03"),
                                  ETH_TYPE(0x0800),
                                  IPV4_SRC("3.4.5.6")],
                                 [SetField(ETH_SRC("00:00:00:00:00:04"))])
        rule.set_cookie(100)
        self.examples.append(rule)


        rule = MatchActionLCRule(1,
                                 [ETH_DST("00:00:00:00:00:05"),
                                  ETH_TYPE(0x0800),
                                  IPV4_SRC("4.5.6.7")],
                                 [SetField(ETH_SRC("00:00:00:00:00:04")),
                                  SetField(IPV4_DST("5.6.7.8"))])
        rule.set_cookie(100)
        self.examples.append(rule)


        rule = MatchActionLCRule(1,
                                 [IP_PROTO(6), ETH_TYPE(0x0800)],
                                 [Forward(1)])
        rule.set_cookie(100)
        self.examples.append(rule)
        #self.examples.append(SDXEgressPolicy('dummy',
        #    {"SDXEgress":
        #     {"starttime":"1985-04-12T23:20:50",
        #      "endtime":"2085-04-12T23:20:50",
        #      "switch":"atl-switch",
        #      "matches":[{"ip_proto":6},
        #                 {"eth_type":0x08000}],
        #      "actions":[{"Forward":1}]}}
        #    ))
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
        self.cm = SDXControllerConnectionManager(dummy_log)
        self.cm_thread = threading.Thread(target=self._cm_thread)
        self.cm_thread.daemon = True
        self.cm_thread.start()

    def _cm_thread(self):
        self.cm.new_connection_callback(self.connection_cb)
        self.cm.open_listening_port(self.ip, self.port)

    def connection_cb(self, cxn):
        self.client = cxn
        self.client.transition_to_main_phase_SDX(lambda a:None, 
                                                 lambda a: [])
        self.client_thread = threading.Thread(target=self._client_thread)
        self.client_thread.daemon = True
        self.client_thread.start()
        print("Connection fully established to LC")

    def _client_thread(self):
        rlist = [self.client]
        wlist = []
        xlist = rlist
        timeout = 1.0

        print("Starting Client Thread: %s" % self.client)
        while(True):
            print ("RCHarness: Beginning of main loop")
            try:
                readable, writeable, exceptional = cxnselect(rlist,
                                                             wlist,
                                                             xlist,
                                                             timeout)
            except Exception as e:
                print("RCHarness: Error in select - %s" % e)
                for entry in rlist:
                    entry.close()
                exit()
            for entry in readable:
                try:
                    print("RCHarness: Calling recv_protocol")
                    msg = entry.recv_protocol()
                    print("RCHarness: Received %s" % msg)
                    # Nothing to do with msg - printing to see what's what.
                except SDXMessageConnectionFailure as e:
                    print("RCHarness: CXN Failure %s %s" % (entry, e))
                    rlist.remove(entry)
                    entry.close()
            print ("RCHarness: End of main loop")
            
    def is_connected(self):
        # figure out if connected
        return (self.client != None)

    def send_new_command(self, cmd):
        switch_id = 1
        msg = SDXMessageInstallRule(cmd, switch_id)
        print("about to send: %s" % msg)
        self.client.send_protocol(msg)
        #self.client.send_cmd(SDX_NEW_RULE, cmd)

    def send_rm_command(self, rule):
        switch_id = 1
        msg = SDXMessageRemoveRule(rule.get_cookie(), switch_id)
        print("about to send: %s" % msg)
        self.client.send_protocol(msg)
        #self.client.send_cmd(SDX_RM_RULE, cmd)

    
