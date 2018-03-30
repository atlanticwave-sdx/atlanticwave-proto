# Copyrightg 2016 - Sean Donovan
# AtlanticWave/SDX Project


import logging
import threading
import sys
import json
import signal
import os
import atexit
import traceback
from Queue import Queue, Empty
from time import sleep

from lib.Singleton import SingletonMixin
from lib.Connection import select as cxnselect
from RyuControllerInterface import *
from LCRuleManager import *
from shared.SDXControllerConnectionManager import *
from shared.SDXControllerConnectionManagerConnection import *
from switch_messages import *

LOCALHOST = "127.0.0.1"
DEFAULT_RYU_CXN_PORT = 55767
DEFAULT_OPENFLOW_PORT = 6633

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

        # Signal Handling
        signal.signal(signal.SIGINT, receive_signal)
        atexit.register(self.receive_exit)

        # Rules DB
        self.rm = LCRuleManager()

        # Initial Rules
        self._initial_rules_dict = {}
        
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
                q_ele = self.sdx_cm.get_cxn_queue_element()
                while q_ele != None:
                    (action, cxn) = q_ele
                    if action == NEW_CXN:
                        self.logger.warning("Adding connection %s" % cxn)
                        if cxn in rlist:
                            # Already there. Weird, but OK
                            pass
                        rlist.append(cxn)
                        wlist = []
                        xlist = rlist
                        
                    elif action == DEL_CXN:
                        self.logger.warning("Removing connection %s" % cxn)
                        if cxn in rlist:
                            # Need to clean up the sdx_connection, as it has
                            # already failed and been (mostly) cleaned up.
                            self.sdx_connection = None
                            rlist.remove(cxn)
                            wlist = []
                            xlist = rlist


                    # Next queue element
                    q_ele = self.sdx_cm.get_cxn_queue_element()
            except Empty as e:
                # This is raised if the cxn_q is empty of events.
                # Normal behaviour
                pass
 
            if self.sdx_connection == None:
                print "SDX_CXN = None, start_cxn_thread = %s" % str(self.start_cxn_thread)
            # Restart SDX Connection if it's failed.
            if (self.sdx_connection == None and
                self.start_cxn_thread == None):
                self.logger.info("Restarting SDX Connection")
                self.start_sdx_controller_connection() #Restart!

            if len(rlist) == 0:
                sleep(timeout/2)
                continue
            
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
                try:
                    msg = entry.recv_protocol()
                except SDXMessageConnectionFailure as e:
                    # Connection needs to be disconnected.
                    self.cxn_q.put((DEL_CXN, entry))
                    entry.close()
                    continue
                except:
                    raise

                 # Can return None if there was some internal message.
                if msg == None:
                    #self.logger.debug("Received None from recv_protocol %s" %
                    #                  (entry))
                    continue
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

                # If InstallRule
                elif type(msg) == SDXMessageInstallRule:
                    self.install_rule_sdxmsg(msg)

                # If RemoveRule
                elif type(msg) == SDXMessageRemoveRule:
                    self.remove_rule_sdxmsg(msg)
                    
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
            
        try:
            self.sdx_connection.transition_to_main_phase_LC(self.name,
                                                self.capabilities,
                                                self._initial_rule_install,
                                                self._initial_rules_complete)

        except (SDXControllerConnectionTypeError,
                SDXControllerConnectionValueError) as e:
            # This can happen. In this case, we need to close the connection,
            # null out the connection, and end the thread.
            self.logger.error("SDX Connection transition to main phase failed with possible benign error. %s : %s" %
                              (self.sdx_connection, e))
            self.sdx_connection.close()
            self.sdx_connection = None
            self.start_cxn_thread = None
            return        
        except Exception as e:
            # We need to clean up the connection as in the errors above, 
            # then raise this error, as this *is* a problem that we need more 
            # info on.
            self.logger.error("SDX Connection transition to main phase failed with unhandled exception %s : %s" %
                              (self.sdx_connection, e))
            self.sdx_connection.close()
            self.sdx_connection = None
            self.start_cxn_thread = None
            raise     
        
        # Upon successful return of connection, add NEW_CXN to cxn_q
        self.cxn_q.put((NEW_CXN, self.sdx_connection))

        # Finish up thread
        self.start_cxn_thread = None
        return

    def start_switch_connection(self):
        pass

    def sdx_message_callback(self):
        pass
    # Is this necessary?

    def install_rule_sdxmsg(self, msg):
        switch_id = msg.get_data()['switch_id']
        rule = msg.get_data()['rule']
        cookie = rule.get_cookie()

        self.rm.add_rule(cookie, lcrule), RULE_STATUS_INSTALLING)
        self.switch_connection.send_command(switch_id, rule)

        
        #FIXME: This should be moved to somewhere where we have positively
        #confirmed a rule has been installed. Right now, there is no such
        #location as the LC/RyuTranslateInteface protocol is primitive.
        self.rm.set_status(cookie, RULE_STATUS_ACTIVE)

    def remove_rule_sdxmsg(self, msg):
        ''' Removes rules based on cookie sent from the SDX Controller. If we do
            not have a rule under that cookie, odds are it's for the previous 
            instance of this LC. Log and drop it.
        '''
        switch_id = msg.get_data()['switch_id']
        cookie = msg.get_data()['cookie']
        rule = self.rm.get_rule(cookie)

        if rule == None:
            self.logger.error("remove_rule_sdxmsg: trying to remove a rule that doesn't exist %s" % cookie)
            return
        self.rm.set_status(cookie, RULE_STATUS_DELETING)
        self.switch_connection.remove_rule(switch_id, cookie)

        #FIXME: This should be moved to somewhere where we have positively
        #confirmed a rule has been removed. Right now, there is no such
        #location as the LC/RyuTranslateInteface protocol is primitive.
        self.rm.set_status(cookie, RULE_STATUS_REMOVED)
        self.rm.rm_rule(cookie)

    def _initial_rule_install(self, rule):
        ''' This builds up a list of rules to be installed. 
            _initial_rules_complete() actually kicks off the install.
        '''
        k = rule.get_data()['rule'].get_cookie()
        self.rm.add_initial_rule(rule, k)

    def _initial_rules_complete(self):
        ''' Calls the LCRuleManager to get delete and add rule lists, then 
            deletes outdated rules and adds new rule.
        '''
        delete_list = []
        add_list = []

        (delete_list, add_list) = self.rm.initial_rules_complete()

        for (entry, cookie) in add_list:
            # Cookie isn't needed
            self.install_rule_sdxmsg(entry)
            
        for (entry, cookie) in delete_list:
            # Extract the switch_id
            switch_id = entry.get_switch_id()

            # Create the RemoveRule to send to self.remove_rule_sdxmsg()
            msg = SDXMessageRemoveRule(cookie, switch_id)
            self.remove_rule_sdxmsg(msg)

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

    def get_ryu_process(self):
        return self.switch_connection.get_ryu_process()

    def receive_exit(self):
        print "EXIT RECEIVED"
        print "\n\n%d\n\n" % self.get_ryu_process().pid
        os.killpg(self.get_ryu_process().pid, signal.SIGKILL)

# Cleanup related functions
def receive_signal(signum, stack):
    print "Caught signal %d" % signum
    print "stack: \n" + "".join(traceback.format_stack(stack))
    exit()        


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

