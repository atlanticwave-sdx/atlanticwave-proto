# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


import threading
import sys
from Queue import Queue, Empty

from lib.AtlanticWaveModule import AtlanticWaveModule
from lib.Connection import select as cxnselect
from shared.SDXControllerConnectionManager import *
from shared.SDXControllerConnectionManagerConnection import *
from shared.UserPolicy import UserPolicyBreakdown
from AuthenticationInspector import *
from AuthorizationInspector import *
from BreakdownEngine import *
from LocalControllerManager import *
from RestAPI import *
from PolicyManager import *
from PolicyRegistry import *
from TopologyManager import *
from ValidityInspector import *
from UserManager import *
from SenseAPI import *

# Known UserPolicies
#FIXME: from shared.JsonUploadPolicy import *
from shared.L2TunnelPolicy import *
from shared.L2MultipointPolicy import *
from shared.EndpointConnectionPolicy import *
from shared.EdgePortPolicy import *
from shared.LearnedDestinationPolicy import *
from shared.FloodTreePolicy import *
from shared.SDXPolicy import SDXEgressPolicy, SDXIngressPolicy



class SDXControllerError(Exception):
    ''' Parent class, can be used as a catch-all for other errors '''
    pass

class SDXControllerConnectionError(SDXControllerError):
    ''' When there's an error with a connection. '''
    pass

class SDXController(AtlanticWaveModule):
    ''' This is the main coordinating module of the SDX controller. It mostly 
        provides startup and coordination, rather than performan many actions by
        itself.
        Singleton. ''' 

    def __init__(self, runloop=True, options=None):
        ''' The bulk of the work happens here. This initializes nearly 
            everything and starts up the main processing loop for the entire SDX
            Controller. '''
        self.loggerid = 'sdxcontroller'
        self.logfilename = 'sdxcontroller.log'
        self.debuglogfilename = None
        super(SDXController, self).__init__(self.loggerid, self.logfilename,
                                            self.debuglogfilename)

        mani = options.manifest
        db = options.database
        run_topo = options.topo

        self.db_filename = db

        # self.run_topo decides whether or not to send rules.
        self.run_topo = run_topo

        # Modules with configuration files
        self.tm = TopologyManager(self.loggerid, mani)

        # Initialize all the modules - Ordering is relatively important here
        self.aci = AuthenticationInspector(self.loggerid)
        self.azi = AuthorizationInspector(self.loggerid)
        self.be = BreakdownEngine(self.loggerid)
        self.pr = PolicyRegistry(self.loggerid)
        self.vi = ValidityInspector(self.loggerid)
        self.um = UserManager(self.db_filename, mani, self.loggerid)

        if mani != None:
            self.lcm = LocalControllerManager(self.loggerid, mani)
        else: 
            self.lcm = LocalControllerManager(self.loggerid)

        topo = self.tm.get_topology()


        # Set up the connection-related nonsense - Have a connection event queue
        self.ip = options.host
        self.port = options.lcport
        self.connections = {}
        self.sdx_cm = SDXControllerConnectionManager(self.loggerid)
        self.cm_thread = threading.Thread(target=self._cm_thread)
        self.cm_thread.daemon = True
        self.cm_thread.start()

        # Register known UserPolicies
        self.pr.find_policies()

        # Start these modules last!
        if self.run_topo:
            self.pm = PolicyManager(self.db_filename, self.loggerid,
                                    self.sdx_cm.send_breakdown_rule_add,
                                    self.sdx_cm.send_breakdown_rule_rm)
        else:
            self.pm = PolicyManager(self.db_filename, self.loggerid,
                                    send_no_rules,
                                    send_no_rules)

        self.rapi = RestAPI(self.loggerid,
                            options.host, options.port, options.shib)
        self.sapi = SenseAPI(self.loggerid,
                             host=options.host, port=options.sport)


        # Install any rules switches will need. 
        self._prep_switches()

        self.logger.warning("%s initialized: %s" % (self.__class__.__name__,
                                                    hex(id(self))))

        # Go to main loop 
        if runloop:
            self._main_loop()

    def _cm_thread(self):
        self.sdx_cm.new_connection_callback(self._handle_new_connection)
        self.sdx_cm.open_listening_port(self.ip, self.port)
        self.logger.critical("Listening on %s:%d" % (self.ip, self.port))
        print("Listening on %s:%d" % (self.ip, self.port))
        pass

    def _get_existing_rules_by_name(self, name):
        # Goes to the PolicyManager to get existing rules for a particular LC
        return self.pm.get_breakdown_rules_by_LC(name)

    def _clean_up_oustanding_cxn(self, name):
        # Check to see if there's an existing connection. If there is, close it.
        if name in self.connections.keys():
            old_cxn = self.connections[name]
            self.logger.warning("Closing old connection for %s : %s" %
                                (name, old_cxn))
            self._handle_connection_loss(old_cxn)

        
        
    def _handle_new_connection(self, cxn):
        # Receive name from LocalController, verify that it's in the topology
        self.logger.critical("Handling new connection %s" % cxn)

        # Get connection to main phase
        try:
            cxn.transition_to_main_phase_SDX(self._clean_up_oustanding_cxn,
                                             self._get_existing_rules_by_name)
        except (SDXControllerConnectionTypeError,
                SDXControllerConnectionValueError) as e:
            # These error can happen, and their not the end of the world. In 
            # this case, we need to close the connection.
            self.logger.error("Connection transition to main phase failed. %s: %s" %
                              (cxn, e))
            cxn.close()
            return

        except Exception as e:
            # We need to close the connection, and raise the exception as this 
            # is unhandled.
            self.logger.error("Connection transition to main phase failed. %s: %s" %
                              (cxn, e))
            cxn.close()
            raise

        
        # Associate connection with name
        name = cxn.get_name()
        self.logger.info("LocalController attempting to log in with name %s." %
                         name)
        self.connections[name] = cxn
        self.sdx_cm.associate_cxn_with_name(name, cxn)

        # Update to Rule Manager
        #FIXME: This is to update the Rule Manager. It seems that whenever a callback is set, it gets a static image of that function/object. That seems incorrect. This should be a workaround.
        if self.run_topo:
            self.pm.set_send_add_policy(self.sdx_cm.send_breakdown_rule_add)
            self.pm.set_send_rm_policy(self.sdx_cm.send_breakdown_rule_rm)

        
        # Create EdgePortPolicy
        # Install an EdgePortPolicy per switch connected to this LC. This
        # installs basic rules for edge ports that are automatically determined
        # during breakdown of the rule
        topo = self.tm.get_topology()
        self.logger.warning("New connection - name %s details %s" % (name, cxn))
        for switch in topo.node[name]['switches']:
            json_rule = {"EdgePort":{"switch":switch}}
            epp = EdgePortPolicy(AUTOGENERATED_USERNAME, json_rule)
            self.pm.add_policy(epp)

    def _handle_connection_loss(self, cxn):
        #FIXME: Send this to the LocalControllerManager
        # Remove connection association
        # Update the Rule Manager
        # Remove rules that are installed at startup
        # - Edgeport rules

        # Get LC name
        name = cxn.get_name()

        # Delete connections associations
        self.sdx_cm.dissociate_name_with_cxn(name)
        # Get all EdgePort policies
        all_edgeport_policies = self.pm.get_policies({'ruletype':'EdgePort'})
        
        # for each switch owned by a particular LC, delete that particular rule
        topo = self.tm.get_topology()
        for switch in topo.node[name]['switches']:
            json_rule = {"EdgePort":{"switch":switch}}
            for p in all_edgeport_policies:
                (rule_hash, json_ver, ruletype, user, state) = p
                if json_rule == json_ver:
                    self.pm.remove_policy(rule_hash, user)


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

        # Main loop - Have a ~500ms timer on the select call to handle cxn 
        # events
        while True:
            # Handle event queue messages
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
                            self._handle_connection_loss(cxn)
                            rlist.remove(cxn)
                            wlist = []
                            xlist = rlist
                    # Next queue element
                    q_ele = self.sdx_cm.get_cxn_queue_element()
            except:
                raise
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
                self.logger.warning("select returned error: %s" % e)
                # This can happen if, say, there's a disconnection that hasn't
                # cleaned up or occured *during* the timeout period. This is due
                # to select failing.
                sleep(timeout/2)
                continue

            # Loop through readable
            for entry in readable:
                # Get Message
                try:
                    msg = entry.recv_protocol()
                except SDXMessageConnectionFailure as e:
                    # Connection needs to be disconnected.
                    entry.close()
                    continue
                except:
                    raise

                # Can return None if there was some internal message.
                if msg == None:
                    #self.logger.debug("Received internal message from recv_protocol %s" %
                    #                  hex(id(entry)))
                    continue
                self.logger.debug("Received a %s message from %s" %
                                  (type(msg), hex(id(entry))))

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
        self.pm.add_policy(ldp)

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

        self.pm.change_callback_dispatch(cookie, opaque)
        
    def _prep_switches(self):
        ''' This sends any rules that are necessary to the switches, such as 
            installing broadcast flooding rules. 
            FIXME: Will need to be updated to accomodate dynamic topologies.
            Also need to deal with deleting this when  there's a topology 
            change.
        '''
        json_rule = {FloodTreePolicy.get_policy_name():None}
        ftp = FloodTreePolicy(AUTOGENERATED_USERNAME, json_rule)
        self.pm.add_policy(ftp)
        


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
    parser.add_argument("-e", "--sense", dest="sport", default=5001, 
                        action="store", type=int, 
                        help="Port number of SENSE interface")
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

