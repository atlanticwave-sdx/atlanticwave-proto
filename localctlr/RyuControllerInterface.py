# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


from ControllerInterface import *
from InterRyuControllerConnectionManager import *
from ryu.ofproto import ofproto_v1_3
from ryu.cmd.manager import main
from lib.Singleton import Singleton
from shared.LCRule import LCRule

import threading
import logging
import subprocess
import sys

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


    def __init__(self, lcname, conffile, openflow_port):
        super(RyuControllerInterface, self).__init__()

        self._setup_logger()

        self.lcname = lcname
        self.conffile = conffile
        self.openflow_port = openflow_port

        # Set up server connection for RyuTranslateInterface to connect to.
        self.inter_cm = InterRyuControllerConnectionManager()
        self.inter_cm_cxn = None
        self.inter_cm_condition = threading.Condition()
        self.inter_cm_thread = threading.Thread(target=self._inter_cm_thread)
        self.inter_cm_thread.daemon = True
        self.inter_cm_thread.start()
        
        # Start up Ryu as a subprocess
        # FIXME: need a way to get the path to RyuTranslateInterface better than this
        #        self.ryu_thread = threading.Thread(target=main,
        #                                           args=(),
        #                                           kwargs={'args':["/home/sdx/atlanticwave-proto/localctlr/RyuTranslateInterface.py"]})

        #        self.ryu_thread.daemon = True
        #        self.ryu_thread.start()
        # This doesn't work as it should: Normally, you would have two different
        # strings within the list. For some reason, ryu-manager doesn't like 
        # this, thus one long string.
        self.logger.debug("About to start ryu-manager.")
        subprocess.Popen(['ryu-manager --app-list /home/sdx/atlanticwave-proto-lcinterface/localctlr/RyuTranslateInterface.py --log-dir . --log-file ryu.log --verbose --ofp-tcp-listen-port %s --atlanticwave-lcname %s --atlanticwave-conffile %s' % (self.openflow_port, self.lcname, self.conffile)], 
                         shell=True)

        self.logger.debug("Started ryu-manager.")
        # Don't complete until the connection is received by inter_cm ...
        self.inter_cm_condition.acquire()
        self.inter_cm_condition.wait()

        # ... and we've gotten notice that they've gotten a connection with at
        # least one switch:
        dps = self.inter_cm_cxn.recv_cmd()

        # FIXME: This cannot be permanent. Each piece should be opened up
        # seperately...
        
        # FIXME: What else?
        self.logger.info("RyuControllerInterface initialized.")
        pass

    def _inter_cm_thread(self):
        self.inter_cm.new_connection_callback(self._new_inter_cm_thread)
        self.inter_cm.open_listening_port(self.lcip, self.ryu_cxn_port)

    def _new_inter_cm_thread(self, cxn):
        self.inter_cm_cxn = cxn
        self.inter_cm_condition.acquire()
        self.inter_cm_condition.notify()
        self.inter_cm_condition.release()

    def send_command(self, switch_id, rule):
        if not isinstance(rule, LCRule):
            raise ControllerInterfaceTypeError("rule is not of type LCRule: " + str(type(rule)) + 
                                               "\n    Value: " + str(rule))

        #self.logger.debug("Sending  new cmd to RyuTranslateInterface: %s:%s" % (switch_id, rule))
        self.inter_cm_cxn.send_cmd(ICX_ADD, (switch_id, rule))

    def remove_rule(self, switch_id, sdxcookie):
        #self.logger.debug("Removing old cmd to RyuTranslateInterface: %s:%s" % (switch_id, sdxcookie))
        self.inter_cm_cxn.send_cmd(ICX_REMOVE, (switch_id, str(sdxcookie)))

    def _setup_logger(self):
        ''' Internal function for setting up the logger formats. '''
        # This is from LocalController
        # reused from https://github.com/sdonovan1985/netassay-ryu/blob/master/base/mcm.py
        formatter = logging.Formatter('%(asctime)s %(name)-12s: %(levelname)-8s %(message)s')
        console = logging.StreamHandler()
        console.setLevel(logging.WARNING)
        console.setFormatter(formatter)
        logfile = logging.FileHandler('localcontroller.log')
        logfile.setLevel(logging.DEBUG)
        logfile.setFormatter(formatter)
        self.logger = logging.getLogger('localcontroller.ryucontrollerinterface')
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(console)
        self.logger.addHandler(logfile) 
