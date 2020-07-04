from __future__ import absolute_import
from __future__ import unicode_literals
# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


from builtins import str
from builtins import hex
from ControllerInterface import *
from InterRyuControllerConnectionManager import *
from ryu.ofproto import ofproto_v1_3
from ryu.cmd.manager import main
from lib.Singleton import Singleton
from lib.Connection import select as cxnselect
from shared.LCRule import LCRule
from switch_messages import *

import threading
import subprocess
import sys
import os

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


    def __init__(self, lcname, conffile, lcip,
                 ryu_cxn_port, openflow_port, lc_callback,
                 loggeridprefix='localcontroller', 
                 run_ryu_manager=True, run_main_loop=True):
        loggerid = loggeridprefix + '.ryucontrollerinterface'
        super(RyuControllerInterface, self).__init__(loggerid)

        self.lcname = lcname
        self.conffile = conffile
        self.lcip = lcip
        self.ryu_cxn_port = ryu_cxn_port
        self.openflow_port = openflow_port
        self.lc_callback = lc_callback
        self.ryu_process = None

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
        if run_ryu_manager:
            self.logger.debug("About to start ryu-manager.")
            current_dir = os.path.dirname(os.path.realpath(__file__))
            self.logger.debug("ENV")
            subprocess.Popen(['env'])
            self.logger.debug("ENV - shell=True")
            subprocess.Popen(['env'], shell=True)
            self.ryu_process = subprocess.Popen(['ryu-manager --app-list %s/RyuTranslateInterface.py --log-dir . --log-file ryu.log --verbose --ofp-tcp-listen-port %s --ofp-listen-host %s --atlanticwave-lcname %s --atlanticwave-conffile %s' % 
                                                 (current_dir, 
                                                  self.openflow_port, 
                                                  '0.0.0.0', 
                                                  self.lcname, 
                                                  self.conffile)], 
                                                shell=True,
                                                #env=os.environ,
                                                preexec_fn=os.setsid)

            self.logger.debug("Started ryu-manager.")

            # Don't complete until the connection is received by inter_cm ...
            self.inter_cm_condition.acquire()
            self.inter_cm_condition.wait()

            # ... and we've gotten notice that they've gotten a connection
            # with at least one switch:
            dps = self.inter_cm_cxn.recv_cmd()

            # FIXME: This cannot be permanent. Each piece should be opened
            # upseperately...
        
            self.logger.warning("%s initialized: %s" % (
                self.__class__.__name__, hex(id(self))))

        if run_main_loop:
            # Start Main Loop
            self.start_main_loop()
            self.logger.info("Main Loop started.")

    def _inter_cm_thread(self):
        self.logger.debug("RyuControllerInterface: Starting inter_cm_thread: %s:%s" %
                          (self.lcip, self.ryu_cxn_port))
        self.inter_cm.new_connection_callback(self._new_inter_cm_thread)
        self.inter_cm.open_listening_port(self.lcip, self.ryu_cxn_port)
        self.logger.debug("RyuControllerInterface: inter_cm_thread - port opened")

    def _new_inter_cm_thread(self, cxn):
        self.inter_cm_cxn = cxn
        self.inter_cm_condition.acquire()
        self.inter_cm_condition.notify()
        self.inter_cm_condition.release()

    def _kill_inter_cm(self):
        if self.inter_cm_cxn != None:
            self.inter_cm_cxn.close()
            self.inter_cm_cxn = None
        if self.ryu_process != None:
            self.ryu_process.kill()

    def send_command(self, switch_id, rule):
        if not isinstance(rule, LCRule):
            raise ControllerInterfaceTypeError("rule is not of type LCRule: " + str(type(rule)) + 
                                               "\n    Value: " + str(rule))

        self.logger.debug("Sending  new cmd to RTI: %s:%s" % 
                          (switch_id, rule))
        self.inter_cm_cxn.send_cmd(ICX_ADD, (switch_id, rule))

    def remove_rule(self, switch_id, sdxcookie):
        self.logger.debug("Removing old cmd to RTI: %s:%s" % 
                          (switch_id, sdxcookie))
        self.inter_cm_cxn.send_cmd(ICX_REMOVE, (switch_id, str(sdxcookie)))

    def get_ryu_process(self):
        return self.ryu_process

    def start_main_loop(self):
        self.main_loop_thread = threading.Thread(target=self._main_loop)
        self.main_loop_thread.daemon = True
        self.main_loop_thread.start()
        self.logger.debug("Main Loop - %s" % (self.main_loop_thread))

    def _main_loop(self):
        ''' This is the main loop for the Local Controller. User should call 
            start_main_loop() to start it. ''' 

        rlist = [self.inter_cm_cxn]
        wlist = []
        xlist = rlist

        self.logger.debug("Inside Main Loop, Inter-CM connection: %s" % (self.inter_cm_cxn))

        while(True):
            # Based, in part, on https://pymotw.com/2/select/
            try:
                readable, writable, exceptional = cxnselect(rlist,
                                                            wlist,
                                                            xlist)
            except Exception as e:
                self.logger.error("RCI: Error in select - %s" % (e))
                self.logger.error("rlist: %s" % rlist)
                # This means that the Inter-Ry connection has died. 
                # - Kill it with the LocalController
                # - Kill the subprocess -
                # - Return out of main loop

                self.lc_callback(SM_INTER_RYU_FAILURE, None)
                self._kill_inter_cm()
                return
                
                

            # Loop through readable
            for entry in readable:
                if entry == self.inter_cm_cxn:
                    cmd, data = self.inter_cm_cxn.recv_cmd()
                    self.logger.debug("Received on inter_cm_cxn : %s:%s" % 
                                      (cmd, data))
                    if cmd == ICX_UNKNOWN_SOURCE:
                        self.lc_callback(SM_UNKNOWN_SOURCE, data)
                    elif cmd == ICX_L2MULTIPOINT_UNKNOWN_SOURCE:
                        self.lc_callback(SM_L2MULTIPOINT_UNKNOWN_SOURCE, data)
                    elif cmd == ICX_DATAPATHS:
                        self.logging.info("Received current datapaths: %s" %
                                          data)
                        #FIXME: anything here?


                #elif?

            # Loop through writable
            for entry in writable:
                # Anything to do here?
                pass

            # Loop through exceptional
            for entry in exceptional:
                # FIXME: Handle connection failures
                pass
