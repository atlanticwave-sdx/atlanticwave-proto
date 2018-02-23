# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


import logging
import threading
import sys
import dataset
from Queue import Queue, Empty

from lib.Singleton import SingletonMixin
from lib.Connection import select as cxnselect
from shared.SDXControllerConnectionManager import *
from shared.SDXControllerConnectionManagerConnection import *
from shared.UserPolicy import UserPolicyBreakdown
from AuthenticationInspector import *
from AuthorizationInspector import *
from BreakdownEngine import *
from LocalControllerManager import *
from RestAPI import *
from RuleManager import *
from RuleRegistry import *
from TopologyManager import *
from ValidityInspector import *
from UserManager import *

# Known UserPolicies
#FIXME: from shared.JsonUploadPolicy import *
from shared.L2TunnelPolicy import *
from shared.L2MultipointPolicy import *
from shared.EndpointConnectionPolicy import *
from shared.EdgePortPolicy import *
from shared.LearnedDestinationPolicy import *
from shared.FloodTreePolicy import *
from shared.SDXPolicy import SDXEgressPolicy, SDXIngressPolicy


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

    def __init__(self, runloop=True, options=None):
        ''' The bulk of the work happens here. This initializes nearly everything
            and starts up the main processing loop for the entire SDX
            Controller. '''

        self._setup_logger()

        mani = options.manifest
        db = options.database
        run_topo = options.topo


        # Start DB connection. Used by other modules. details on the setup:
        # https://dataset.readthedocs.io/en/latest/api.html
        # https://github.com/g2p/bedup/issues/38#issuecomment-43703630
        self.db = dataset.connect('sqlite:///' + db, 
                                  engine_kwargs={'connect_args':
                                                 {'check_same_thread':False}})

        # self.run_topo decides whether or not to send rules.
        self.run_topo = run_topo

        # Modules with configuration files
        self.tm = TopologyManager.instance(mani)

        # Initialize all the modules - Ordering is relatively important here
        self.aci = AuthenticationInspector.instance()
        self.azi = AuthorizationInspector.instance()
        self.be = BreakdownEngine.instance()
        self.rr = RuleRegistry.instance()
        self.vi = ValidityInspector.instance()
        self.um = UserManager.instance(self.db, mani)


        if mani != None:
            self.lcm = LocalControllerManager.instance(mani)
        else: 
            self.lcm = LocalControllerManager.instance()

        topo = self.tm.get_topology()


        # Set up the connection-related nonsense - Have a connection event queue
        self.ip = options.host
        self.port = options.lcport
        self.cxn_q = Queue()
        self.connections = {}
        self.sdx_cm = SDXControllerConnectionManager()
        self.cm_thread = threading.Thread(target=self._cm_thread)
        self.cm_thread.daemon = True
        self.cm_thread.start()

        # Register known UserPolicies
        self.rr.add_ruletype(L2TunnelPolicy)
        self.rr.add_ruletype(L2MultipointPolicy)
        self.rr.add_ruletype(EndpointConnectionPolicy)
        self.rr.add_ruletype(EdgePortPolicy)
        self.rr.add_ruletype(LearnedDestinationPolicy)
        self.rr.add_ruletype(FloodTreePolicy)
        self.rr.add_ruletype(SDXEgressPolicy)
        self.rr.add_ruletype(SDXIngressPolicy)

        # Start these modules last!
        if self.run_topo:
            self.rm = RuleManager.instance(self.db,
                                           self.sdx_cm.send_breakdown_rule_add,
                                           self.sdx_cm.send_breakdown_rule_rm)
        else:
            self.rm = RuleManager.instance(self.db,
                                           send_no_rules,
                                           send_no_rules)

        self.rapi = RestAPI.instance(options.host,options.port,options.shib)


        # Install any rules switches will need. 
        self._prep_switches()

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
        self.logger.critical("Listening on %s:%d" % (self.ip, self.port))
        print("Listening on %s:%d" % (self.ip, self.port))
        pass

    def _get_existing_rules_by_name(self, name):
        # Goes to the RuleManager to get existing rules for a particular LC
        return self.rm.get_breakdown_rules_by_LC(name)
        
    def _handle_new_connection(self, cxn):
        # Receive name from LocalController, verify that it's in the topology
        self.logger.critical("Handling new connection %s" % cxn)
        print("Handling new connection %s" % cxn)

        # Get connection to main phase
        cxn.transition_to_main_phase_SDX(self._get_existing_rules_by_name)
        
        # Associate connection with name
        name = cxn.get_name()
        self.logger.info("LocalController attempting to log in with name %s." %
                         name)
        self.connections[name] = cxn
        self.sdx_cm.associate_cxn_with_name(name, cxn)
        self.cxn_q.put((NEW_CXN, cxn))

        # Update to Rule Manager
        #FIXME: This is to update the Rule Manager. It seems that whenever a callback is set, it gets a static image of that function/object. That seems incorrect. This should be a workaround.
        if self.run_topo:
            self.rm.set_send_add_rule(self.sdx_cm.send_breakdown_rule_add)
            self.rm.set_send_rm_rule(self.sdx_cm.send_breakdown_rule_rm)

        
        # Create EdgePortPolicy
        # Install an EdgePortPolicy per switch connected to this LC. This
        # installs basic rules for edge ports that are automatically determined
        # during breakdown of the rule
        topo = self.tm.get_topology()
        for switch in topo.node[name]['switches']:
            json_rule = {"EdgePort":{"switch":switch}}
            epp = EdgePortPolicy(AUTOGENERATED_USERNAME, json_rule)
            self.rm.add_rule(epp)
        
        
        
    def _handle_connection_loss(self, cxn):
        #FIXME: Send this to the LocalControllerManager
        # Remove connection association
        # Update the Rule Manager
        # Remove rules that are installed at startup
        # - Edgeport rules
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
                    self.logger.debug("Received None from recv_protocol %s" %
                                      (entry))
                    continue
                self.logger.debug("Received a %s message from %s" %
                                  (type(msg), entry))

                # If message is UnknownSource or L2MultipointUnknownSource,
                # Send the appropriate handler.
                if isinstance(msg, SDXMessageUnknownSource):
                    self._switch_message_unknown_source(msg)
                elif isinstance(msg, SDXMessageL2MultipointUnknownSource):
                    self._switch_change_callback_handler(msg)

                # Else: Log an error
                else:
                    self.logger.error("Message %s is not valid" % msg)

            # Loop through writable
            for entry in writable:
                # Anything to do here?
                pass

            # Loop through exceptional
            for entry in exceptional:
                # FIXME: Handle connection failures
                pass

    def _switch_message_unknown_source(self, msg):
        ''' This handles SDXMessageUnknownSource messages.
            'data' is a dictionary of the following pattern - see 
            shared/SDXControllerConnectionManagerConnection.py:
              {'switch':name, 'port':number, 'src':address}
        '''
        data = msg.get_data()
        json_rule = {"learneddest":{"dstswitch":data['switch'],
                                    "dstport":data['port'],
                                    "dstaddress":data['src']}}
        ldp = LearnedDestinationPolicy(AUTOGENERATED_USERNAME, json_rule)
        self.rm.add_rule(ldp)

    def _switch_change_callback_handler(self, msg):
        ''' This handles any message for switch_change_callbacks. 'data' is a 
            dictionary of the following pattern:
              {'cookie':cookie, 'data':opaque data for handler}
            The cookie is for looking up the policy that needs to handle this
            callback. data is opaque data that is passed to the 
            UserPolicy.switch_change_callback() function.
        '''
        data = msg.get_data()
        cookie = data['cookie']
        opaque = data['data']

        self.rm.change_callback_dispatch(cookie, opaque)
        
    def _prep_switches(self):
        ''' This sends any rules that are necessary to the switches, such as 
            installing broadcast flooding rules. '''
        json_rule = {FloodTreePolicy.get_policy_name():None}
        ftp = FloodTreePolicy(AUTOGENERATED_USERNAME, json_rule)
        self.rm.add_rule(ftp)
        


def send_no_rules(param):
    pass


if __name__ == '__main__':
    #from optparse import OptionParser
    #parser = OptionParser()

    import argparse
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("-d", "--database", dest="database", type=str, 
                        action="store", help="Specifies the database ", 
                        default=":memory:")
    parser.add_argument("-m", "--manifest", dest="manifest", type=str, 
                        action="store", help="specifies the manifest")    
    parser.add_argument("-s", "--shibboleth", dest="shib", default=False, 
                        action="store_true", help="Run with Shibboleth for authentication")

    parser.add_argument("-N", "--no_topo", dest="topo", default=True, 
                        action="store_false", help="Run without the topology")

    parser.add_argument("-H", "--host", dest="host", default='0.0.0.0', 
                        action="store", type=str, help="Choose a host address ")
    parser.add_argument("-p", "--port", dest="port", default=5000, 
                        action="store", type=int, 
                        help="Port number of web interface")
    parser.add_argument("-l", "--lcport", dest="lcport", default=PORT,
                        action="store", type=int,
                        help="Port number for LCs to connect to")

    options = parser.parse_args()
    print options
 
    if not options.manifest:
        parser.print_help()
        exit()
        
    sdx = SDXController(False, options)
    sdx._main_loop()

