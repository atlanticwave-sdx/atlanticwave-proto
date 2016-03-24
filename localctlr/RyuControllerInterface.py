# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


from ControllerInterface import ControllerInterface
from InterRyuControllerConnectionManager import *
from ryu.ofproto import ofproto_v1_3
from shared.Singleton import Singleton
from shared.OpenFlowRule import OpenFlowRule
from ryu.cmd.manager import main

from threading import Thread


class RyuControllerInterface(ControllerInterface):
    ''' This is a particular implementation of the ControllerInterface class
        that connects using Ryu. It inherits its interface from its parent 
        class. 
        It, by itself, does not interface with Ryu. This is because of how Ryu
        works. The ryu-manager must run each application, so in order to deal
        with that, we use some rather ugly passthroughs. First, we start the
        RyuTranslateInterface that takes commands, translates them to Ryu, and
        creates and sends the FlowMod messages. Second, there is a Inter-Ryu
        Connection that both RyuControllerInterface and RyuTranslateInterface 
        can talk to in order to pass messages between each other.
    '''


    def __init__(self, *args, **kwargs):
        super(RyuControllerInterface, self).__init__(*args, **kwargs)

        # Set up server connection for RyuTranslateInterface to connect to.
        self.inter_cm = InterRyuControllerConnectionManager()
        self.inter_cm_cxn = None
        self.inter_cm_condition = threading.Condition()
        self.inter_cm_thread = threading.Thread(target=self._inter_cm_thread)
        self.inter_cm_thread.daemon = True
        self.inter_cm_thread.start()
        
        # Start up Ryu as a subprocess
        # FIXME: need a way to get the path to RyuTranslateInterface better than this
        self.ryu_thread = Thread(target=main,
                                 args=(),
                                 kwargs={'args':["/home/sdx/atlanticwave-proto/localctlr/RyuTranslateInterface.py"]})
        self.ryu_thread.daemon = True
        self.ryu_thread.start()

        # Don't complete until the connection is received by inter_cm ...
        self.inter_cm_condition.wait()

        # ... and we've gotten notice that they've gotten a connection with at
        # least one switch:
        dps = self.inter_cm_cxn.recv()
        print "Datapaths received from RyuTranslateInterface: "
        print dps
        # FIXME: This cannot be permanent. Each piece should be opened up
        # seperately...
        
        # FIXME: What else?
        pass

    def _inter_cm_thread(self):
        self.inter_cm.new_connection_callback(self._new_inter_cm_thread)
        #FIXME: hardcoded!
        self.inter_cm.open_listening_port("127.0.0.1", 55767)

    def _new_inter_cm_thread(self, cxn):
        self.inter_cm_cxn = cxn
        self.inter_cm_condition.notify()

    def send_command(self, rule):
        if not isinstance(rule, OpenFlowRule):
            raise ControllerInterfaceTypeError("rule is not of type OpenFlowRule: " + type(rule))

        #FIXME - Need a command and a rule, not just a rule.
        self.inter_cm_cxn.send(rule)

    def remove_rule(self, rule):
        raise Error("NOT IMPLEMENTED.")
        if not isinstance(rule, OpenFlowRule):
            raise ControllerInterfaceTypeError("rule is not of type OpenFlowRule: " + type(rule))

        # FIXME: How to make this cleaner?
        self.queue.remove_rule(rule)


