# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


import logging
import threading
import sys
import Queue
import dataset

from lib.Singleton import SingletonMixin
from lib.Connection import select as cxnselect
from shared.SDXControllerConnectionManager import *
from shared.UserPolicy import UserPolicyBreakdown
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

# Known UserPolicies
#FIXME: from shared.JsonUploadPolicy import *
from shared.L2TunnelPolicy import *


# Connection Queue actions defininition
NEW_CXN = "New Connection"
DEL_CXN = "Remove Connection"



class SDXControllerError(Exception):
    ''' Parent class, can be used as a catch-all for other errors '''
    pass

class SDXControllerConnectionError(SDXControllerError):
    ''' When there's an error with a connection. '''
    pass

class SDXController(SingletonMixin):
    ''' This is the main coordinating module of the SDX controller. It mostly 
        provides startup and coordination, rather than performan many actions by
        itself.
        Singleton. ''' 

    def __init__(self, runloop=True, mani=None, db=":memory:", run_topo=True):
        ''' The bulk of the work happens here. This initializes nearly everything
            and starts up the main processing loop for the entire SDX
            Controller. '''

        self._setup_logger()

        # Start DB connection. Used by other modules. details on the setup:
        # https://dataset.readthedocs.io/en/latest/api.html
        # https://github.com/g2p/bedup/issues/38#issuecomment-43703630
        self.db = dataset.connect('sqlite:///' + db, 
                                  engine_kwargs={'connect_args':
                                                 {'check_same_thread':False}})

        # self.run_topo decides whether or not to send rules.
        self.run_topo = run_topo

        # Modules with potentially configurable configuration files
        if mani != None:
            self.tm = TopologyManager.instance(mani)
        else:
            self.tm = TopologyManager.instance()

        # Initialize all the modules - Ordering is relatively important here
        self.aci = AuthenticationInspector.instance()
        self.azi = AuthorizationInspector.instance()
        self.be = BreakdownEngine.instance()
        self.rr = RuleRegistry.instance()
        self.vi = ValidityInspector.instance()

        if mani != None:
            self.pm = ParticipantManager.instance(mani)
            self.lcm = LocalControllerManager.instance(mani)
        else: 
            self.pm = ParticipantManager.instance()
            self.lcm = LocalControllerManager.instance()

        topo = self.tm.get_topology()


        # Set up the connection-related nonsense - Have a connection event queue
        self.ip = IPADDR        # from share.SDXControllerConnectionManager
        self.port = PORT
        self.cxn_q = Queue.Queue()
        self.connections = {}
        self.sdx_cm = SDXControllerConnectionManager()
        self.cm_thread = threading.Thread(target=self._cm_thread)
        self.cm_thread.daemon = True
        self.cm_thread.start()

        # Register known UserPolicies
#FIXME        self.rr.add_ruletype("json-upload", JsonUploadPolicy)
        self.rr.add_ruletype("l2tunnel", L2TunnelPolicy)


        # Start these modules last!
        if self.run_topo:
            self.rm = RuleManager.instance(self.db,
                                           self.sdx_cm.send_breakdown_rule_add,
                                           self.sdx_cm.send_breakdown_rule_rm)
        else:
            self.rm = RuleManager.instance(self.db,
                                           send_no_rules,
                                           send_no_rules)

        self.pm = ParticipantManager.instance()      #FIXME - Filename
        self.rapi = RestAPI.instance()

        # Go to main loop 
        if runloop:
            self._main_loop()

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
        # Receive name from LocalController, verify that it's in the topology
        cmd,name = cxn.recv_cmd()

        if cmd != SDX_IDENTIFY:
            #FIXME: raise some sort of error here.
            self.logger.error("LocalController not identifying correctly: %s, %s" % (cmd, name))
            return
        
        lcs = self.tm.get_lcs()

        self.logger.info("LocalController attempting to log in with name %s." % 
                         name)

        if name not in lcs:
            self.logger.error("LocalController with name %s attempting to get in. Only known nodes: %s" % (name, lcs))
            return
        # FIXME: Credentials exchange

        # Add connection to connections list
        self.connections[name] = cxn
        self.sdx_cm.associate_cxn_with_name(name, cxn)
        self.cxn_q.put((NEW_CXN, cxn))
        #FIXME: Send this to the LocalControllerManager

        #FIXME: This is to update the Rule Manager. It seems that whenever a callback is set, it gets a static image of that function/object. That seems incorrect. This should be a workaround.
        if self.run_topo:
            self.rm.set_send_add_rule(self.sdx_cm.send_breakdown_rule_add)
            self.rm.set_send_rm_rule(self.sdx_cm.send_breakdown_rule_rm)
        
    def _handle_connection_loss(self, cxn):
        #FIXME: Send this to the LocalControllerManager
        pass

    def start_main_loop(self):
        self.main_loop_thread = threading.Thread(target=self._main_loop)
        self.main_loop_thread.daemon = True
        self.main_loop_thread.start()
        self.logger.debug("Main Loop - %s" % (self.main_loop_thread))

    def _main_loop(self):
        # Set up the select structures
        rlist = self.connections.values()
        wlist = []
        xlist = rlist
        timeout = 2.0

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
            try: 
                readable, writable, exceptional = cxnselect(rlist,
                                                            wlist,
                                                            xlist,
                                                            timeout)
            except Exception as e:
                raise


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

def send_no_rules(param):
    pass

def usage():
    print "USAGE: python SDXController.py manifest <db-location> <--no_topo>"
    print "You must provide manifest files for the SDXController if running from the command line."
    print "You can provide a database location for the sqlite database. Otherwise, uses an in-memory database for temporary storage."
    print "--no_topo is used when not running local controllers for testing."
    exit()


if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser()

    parser.add_option("-d", "--database", dest="database", type="string", action="store",
                  help="Specifies the database. The default database is \":memory:\"", default=":memory:")
    parser.add_option("-m", "--manifest", dest="manifest", type="string", action="store",
                  help="specifies the manifest")
    parser.add_option("-N", "--no_topo", dest="topo", default=True, action="store_false", help="Run without the topology")
    
    (options, args) = parser.parse_args()
    
    if not options.manifest:
        usage()
        
    sdx = SDXController(False, options.manifest, options.database, options.topo)
    sdx._main_loop()

