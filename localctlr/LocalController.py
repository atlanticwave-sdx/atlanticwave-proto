# Copyrightg 2016 - Sean Donovan
# AtlanticWave/SDX Project


import logging
import threading
import sys
import json
from Queue import Queue, Empty
from time import sleep

from lib.Singleton import SingletonMixin
from lib.Connection import select as cxnselect
from RyuControllerInterface import *
from shared.SDXControllerConnectionManager import *
from shared.SDXControllerConnectionManagerConnection import *
from switch_messages import *

LOCALHOST = "127.0.0.1"
DEFAULT_RYU_CXN_PORT = 55767
DEFAULT_OPENFLOW_PORT = 6633

NEW_CXN = "New Connection"
DEL_CXN = "Remove Connection"

class LocalController(SingletonMixin):
    ''' The Local Controller is responsible for passing messages from the SDX 
        Controller to the switch. It needs two connections to both the SDX 
        controller and switch(es).
        Singleton. ''' 

    def __init__(self, runloop=False, options=None):
        # Setup logger
        self._setup_logger()
        self.name = options.name
        self.capabilities = "NOTHING YET" #FIXME: This needs to be updated
        self.logger.info("LocalController %s starting", self.name)

        # Parse out the options
        # Import configuration information
        self.manifest = options.manifest
        self.sdxip = options.host
        self.sdxport = options.sdxport

        self.lcip = LOCALHOST
        self.ryu_cxn_port = DEFAULT_RYU_CXN_PORT
        self.openflow_port = DEFAULT_OPENFLOW_PORT
        if self.manifest != None:
            self._import_configuration()

        # Setup switch
        self.switch_connection = RyuControllerInterface(self.name,
                                    self.manifest, self.lcip,
                                    self.ryu_cxn_port, self.openflow_port,
                                    self.switch_message_cb)
        self.logger.info("RyuControllerInterface setup finish.")

        # Setup connection manager
        self.cxn_q = Queue()
        self.sdx_cm = SDXControllerConnectionManager()
        self.sdx_connection = None
        self.start_cxn_thread = None

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
        rlist = []
        wlist = []
        xlist = rlist
        timeout = 1.0

        self.logger.debug("Inside Main Loop, SDX connection: %s" % (self.sdx_connection))

        while(True):
            # Based, in part, on https://pymotw.com/2/select/ and
            # https://stackoverflow.com/questions/17386487/
            try:
                while not self.cxn_q.empty():
                    (action, dxn) = self.cxn_q.get(False)
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
 

            if len(rlist) == 0:
                sleep(timeout/2)
                next
            
            try:
                readable, writable, exceptional = cxnselect(rlist,
                                                            wlist,
                                                            xlist,
                                                            timeout)
            except Exception as e:
                self.logger.error("Error in select - %s" % (e))
                

            # Loop through readable
            for entry in readable:
                # Get Message
                msg = entry.recv_protocol()
                self.logger.debug("Received a %s message from %s" %
                                  (type(msg), entry))

                #FIXME: Check if the SDXMessage is valid at this stage
                
                # If HeartbeatRequest, send a HeartbeatResponse. This doesn't
                # require tracking anything, unlike when sending out a
                # HeartbeatRequest ourselves.
                if type(msg) == SDXMessageHeartbeatRequest:
                    hbr = SDXMessageHeartbeatResponse()
                    entry.send_protocol(hbr)
                
                # If HeartbeatResponse, call HeartbeatResponseHandler
                elif type(msg) == SDXMessageHeartbeatResponse:
                    entry.heartbeat_response_handler(msg)

                # If InstallRule FIXME
                elif type(msg) == SDXMessageInstallRule:
                    self.install_rule_sdxmsg(msg)
                    
                # If InstallRuleComplete - ERROR! LC shouldn't receive this.
                # If InstallRuleFailure -  ERROR! LC shouldn't receive this.
                # If RemoveRuleComplete - ERROR! LC shouldn't receive this.
                # If RemoveRuleFailure -  ERROR! LC shouldn't receive this.
                # If UnknownSource - ERROR! LC shouldn't receive this.
                # If SwitchChangeCallback -  ERROR! LC shouldn't receive this.
                elif (type(msg) == SDXMessageInstallRuleComplete and
                      type(msg) == SDXMessageInstallRuleFailure and
                      type(msg) == SDXMessageRemoveRuleComplete and
                      type(msg) == SDXMessageRemoveRuleFailure and
                      type(msg) == SDXMessageUnknownSource and
                      type(msg) == SDXMessageSwitchChangeCallback):
                    raise TypeError("msg type %s - not valid: %s" % (type(msg),
                                                                     msg))
                
                # All other types are something that shouldn't be seen, likely
                # because they're from the a Message that's not currently valid
                else:
                    raise TypeError("msg type %s - not valid: %s" % (type(msg),
                                                                     msg))


            # Loop through writable
            for entry in writable:
                # Anything to do here?
                pass

            # Loop through exceptional
            for entry in exceptional:
                # FIXME: Handle connection failures
                # Clean up current connection
                self.sdx_connection.close()
                self.sdx_connection = None
                self.cxn_q.put((DEL_CXN, cxn))
                
                # Restart new connection
                self.start_sdx_controller_connection()

        
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

    def _import_configuration(self):
        with open(self.manifest) as data_file:
            data = json.load(data_file)

        # Look at information under the self.name entry
        lcdata = data['localcontrollers'][self.name]
        self.lcip = lcdata['lcip']
        self.ryu_cxn_port = lcdata['internalconfig']['ryucxninternalport']
        self.openflow_port = lcdata['internalconfig']['openflowport']

    def start_sdx_controller_connection(self):
        # Kick off thread to start connection.
        if self.start_cxn_thread != None:
            raise Exception("start_cxn_thread %s already exists." % self.start_cxn_thread)
        self.start_cxn_thread = threading.Thread(target=self._start_sdx_controller_connection_thread)
        self.start_cxn_thread.daemon = True
        self.start_cxn_thread.start()
        self.logger.debug("start_cdx_controller_connection-thread - %s" %
                          self.start_cxn_thread)

    def _start_sdx_controller_connection_thread(self):
        # Start connection
        self.logger.debug("About to open SDX Controller Connection to %s:%s" % 
                          (self.sdxip, self.sdxport))
        self.sdx_connection = self.sdx_cm.open_outbound_connection(self.sdxip, 
                                                                   self.sdxport)
        self.logger.debug("SDX Controller Connection - %s" % 
                          (self.sdx_connection))

        # Transition to Main Phase
        self.sdx_connection.transition_to_main_phase_LC(self.name,
                                                   self.capabilities,
                                                   self.install_rule_sdxmsg)
        
        # Upon successful return of connection, add NEW_CXN to cxn_q
        self.cxn_q.put((NEW_CXN, self.sdx_connection))

        # Finish up thread
        self.start_cxn_thread = None
        

    def start_switch_connection(self):
        pass

    def sdx_message_callback(self):
        pass
    # Is this necessary?

    def install_rule_sdxmsg(self, msg):
        switch_id = msg.get_data()['switch_id']
        rule = msg.get_data()['rule']
        self.switch_connection.send_command(switch_id, rule)
        
    def switch_message_cb(self, cmd, opaque):
        ''' Called by SwitchConnection to pass information back from the Switch
            type is the type of message defined in switch_messages.py.
            opaque is the message that's being sent back, which is source 
            dependent.
        '''
        if cmd == SM_UNKNOWN_SOURCE:
            # Create an SDXMessageUnknownSource and send it.
            msg = SDXMessageUnknownSource(opaque['src'], opaque['port'],
                                          opaque['switch'])
            self.sdx_connection.send_protocol(msg)
        
        elif cmd == SM_L2MULTIPOINT_UNKNOWN_SOURCE:
            # Create an SDXMessageSwitchChangeCallback and send it.
            msg = SDXMessageSwitchChangeCallback(opaque)
            self.sdx_connection.send_protocol(msg)

        #FIXME: Else?
            

if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("-m", "--manifest", dest="manifest", type=str,
                        action="store", help="specifies the manifest")
    parser.add_argument("-n", "--name", dest="name", type=str,
                        action="store", help="Specify the name of the LC")
    parser.add_argument("-H", "--host", dest="host", default=IPADDR,
                        action="store", type=str, 
                        help="IP address of SDX Controller")
    parser.add_argument("-p", "--port", dest="sdxport", default=PORT, 
                        action="store", type=int, 
                        help="Port number of SDX Controller")

    options = parser.parse_args()
    print options

    if not options.manifest or not options.name:
        parser.print_help()
        exit()

    lc = LocalController(False, options)
    lc._main_loop()

