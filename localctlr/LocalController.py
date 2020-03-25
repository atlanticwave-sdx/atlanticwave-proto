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
import cPickle as pickle
from Queue import Queue, Empty
from time import sleep

from lib.AtlanticWaveModule import AtlanticWaveModule
from lib.Connection import select as cxnselect
from RyuControllerInterface import *
from LCRuleManager import *
from shared.SDXControllerConnectionManager import *
from shared.SDXControllerConnectionManagerConnection import *
from switch_messages import *

LOCALHOST = "127.0.0.1"
DEFAULT_RYU_CXN_PORT = 55767
DEFAULT_OPENFLOW_PORT = 6633

class LocalController(AtlanticWaveModule):
    ''' The Local Controller is responsible for passing messages from the SDX 
        Controller to the switch. It needs two connections to both the SDX 
        controller and switch(es).
        Singleton. ''' 

    def __init__(self, runloop=False, options=None):
        self.loggerid = 'localcontroller'
        self.logfilename = 'localcontroller-%s.log' % options.name
        self.debuglogfilename = None
        super(LocalController, self).__init__(self.loggerid, self.logfilename,
                                              self.debuglogfilename)
        
        self.name = options.name
        self.capabilities = "NOTHING YET" #FIXME: This needs to be updated
        self.logger.info("LocalController %s starting", self.name)

        # Import configuration information - this includes pulling information
        # from the stored DB (if there is anything), and from the options passed
        # in during startup (including the manifest file)
        self._setup(options)
        
        # Signal Handling
        signal.signal(signal.SIGINT, receive_signal)
        atexit.register(self.receive_exit)

        # Rules DB
        self.rm = LCRuleManager(self.loggerid)

        # Initial Rules
        self._initial_rules_dict = {}
        
        # Setup switch
        self._setup_switch()

        # Setup connection manager
        self.cxn_q = Queue()
        self.sdx_cm = SDXControllerConnectionManager(self.loggerid)
        self.sdx_connection = None
        self.start_cxn_thread = None

        self.logger.info("SDXControllerConnectionManager setup finish.")
        self.logger.debug("SDXControllerConnectionManager - %s" % (self.sdx_cm))

        # Start connections:
        self.start_switch_connection()
        self.start_sdx_controller_connection() # Blocking call
        self.logger.info("SDX Controller Connection established.")

        self.logger.warning("%s initialized: %s" % (self.__class__.__name__,
                                                    hex(id(self))))

        # Start main loop
        if runloop:
            self.start_main_loop()
            self.logger.info("Main Loop started.")

    def _setup_switch(self):
        self.switch_connection = RyuControllerInterface(self.name,
                                    self.manifest, self.lcip,
                                    self.ryu_cxn_port, self.openflow_port,
                                    self.switch_message_cb,
                                    self.loggerid)
        self.logger.info("RyuControllerInterface setup finish.")


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
        num_of_retry = 0
        all_rules = []

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
                        self.logger.debug("Adding Cxn to rlist: %s" % cxn)
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
                self.logger.error("LocalController: Error in select - %s" % (e))
                

            # Loop through readable
            for entry in readable:
                # Get Message
                try:
                    msg = entry.recv_protocol()
                except SDXMessageConnectionFailure as e:
                    # Connection needs to be disconnected.
                    self.logger.warning("CXN Failure: %s %s" % (entry, e))
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

                #FIXME: Check if the SDXMessage is valid at this stage
                
                # If HeartbeatRequest, send a HeartbeatResponse. This doesn't
                # require tracking anything, unlike when sending out a
                # HeartbeatRequest ourselves.
                if type(msg) == SDXMessageHeartbeatRequest:
                    self.logger.debug("Received a HBREQ message from %s" %
                                      hex(id(entry)))

                    hbr = SDXMessageHeartbeatResponse()
                    entry.send_protocol(hbr)
                
                # If HeartbeatResponse, call HeartbeatResponseHandler
                elif type(msg) == SDXMessageHeartbeatResponse:
                    self.logger.debug("Received a HBRES message from %s" %
                                      hex(id(entry)))
                    entry.heartbeat_response_handler(msg)

                # If InstallRule
                elif type(msg) == SDXMessageInstallRule:
                    self.logger.debug("Received a INSTL message from %s" %
                                      hex(id(entry)))
                    self.install_rule_sdxmsg(msg)
                    self.remove_all_rules_sdxmsg()

                # If RemoveRule
                elif type(msg) == SDXMessageRemoveRule:
                    self.logger.debug("Received a REMOV message from %s" %
                                      hex(id(entry)))
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
                    self.logger.warning("msg type %s - not valid: %s" % 
                                        (type(msg), msg))
                
                # All other types are something that shouldn't be seen, likely
                # because they're from the a Message that's not currently valid
                else:
                    self.logger.warning("msg type %s - not valid: %s" % 
                                        (type(msg), msg))


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
                if num_of_retry <= 5:
                    # Restart new connection
                    self.start_sdx_controller_connection()
                    sleep(5)
                
                self.all_rules = self.rm.list_all_rules
                num_of_retry = 0
                
    

    def _add_switch_config_to_db(self, switch_name, switch_config):
        # Pushes a switch info dictionary from manifest.
        # key: "<switch_name>_switchinfo"
        # value: <switch_config>
        key = switch_name + "_switchinfo"
        value = pickle.dumps(switch_config)
        if self._get_switch_config_in_db(switch_name) == None:
            self.logger.info("Adding new switch configuration for switch %s" %
                             switch_name)
            self.config_table.insert({'key':key, 'value':value})
        else:
            # Already exists, must update.
            self.logger.info("Updating switch configuration for switch %s" %
                             switch_name)
            self.config_table.update({'key':key, 'value':value},
                                     ['key'])

    def _add_ryu_config_to_db(self, ryu_config):
        # Pushes Ryu network configuration info into the DB.
        # key: "ryu_config"
        # value: ryu_config
        key = 'ryu_config'
        value = pickle.dumps(ryu_config)
        if self._get_ryu_config_in_db() == None:
            self.logger.info("Adding new Ryu configuration %s" %
                             ryu_config)
            self.config_table.insert({'key':key, 'value':value})
        else:
            # Already exists, must update.
            self.logger.info("Updating Ryu configuration %s" %
                             ryu_config)
            self.config_table.update({'key':key, 'value':value},
                                     ['key'])

    def _add_LC_config_to_db(self, lc_config):
        # Pushes LC network configuration info into the DB.
        # key: "lc_config"
        # value: lc_config
        key = 'lc_config'
        value = pickle.dumps(lc_config)
        if self._get_LC_config_in_db() == None:
            self.logger.info("Adding new LC configuration %s" %
                             lc_config)
            self.config_table.insert({'key':key, 'value':value})
        else:
            # Already exists, must update.
            self.logger.info("Updating LC configuration %s" %
                             lc_config)
            self.config_table.update({'key':key, 'value':value},
                                     ['key'])

    def _add_SDX_config_to_db(self, sdx_config):
        # Pushes SDX network configuration info into the DB.
        # key: "sdx_config"
        # value: sdx_config
        key = 'sdx_config'
        value = pickle.dumps(sdx_config)
        if self._get_SDX_config_in_db() == None:
            self.logger.info("Adding new SDX configuration %s" %
                             sdx_config)
            self.config_table.insert({'key':key, 'value':value})
        else:
            # Already exists, must update.
            self.logger.info("Updating SDX configuration %s" %
                             sdx_config)
            self.config_table.update({'key':key, 'value':value},
                                     ['key'])
    
    def _add_manifest_filename_to_db(self, manifest_filename):
        # Pushes LC network configuration info into the DB.
        # key: "manifest_filename"
        # value: manifest_filename
        key = 'manifest_filename'
        value = pickle.dumps(manifest_filename)
        if self._get_manifest_filename_in_db() == None:
            self.logger.info("Adding new manifest filename %s" %
                             manifest_filename)
            self.config_table.insert({'key':key, 'value':value})
        else:
            # Already exists, must update.
            self.logger.info("Updating manifest filename %s" %
                             manifest_filename)
            self.config_table.update({'key':key, 'value':value},
                                     ['key'])

    def _get_switch_config_in_db(self, switch_name):
        # Returns a switch configuration dictionary if one exists or None if one
        # does not.
        key = switch_name + "_switchinfo"
        d = self.config_table.find_one(key=key)
        if d == None:
            return None
        val = d['value']
        return pickle.loads(str(val))

    def _get_switch_internal_config(self, switch_id):
        ''' Gets switch internal config information based on datapath passed in
            Pulls information from the DB.
        '''
        key = str(switch_id)
        d = self.config_table.find_one(key=key)
        if d == None:
            return None
        val = d['value']
        return pickle.loads(str(val))

    def _get_ryu_config_in_db(self):
        # Returns the ryu configuration dictionary if it exists or None if it
        # does not.
        key = 'ryu_config'
        d = self.config_table.find_one(key=key)
        if d == None:
            return None
        val = d['value']
        return pickle.loads(str(val))

    def _get_LC_config_in_db(self):
        # Returns the LC configuration dictionary if it exists or None if it
        # does not.
        key = 'lc_config'
        d = self.config_table.find_one(key=key)
        if d == None:
            return None
        val = d['value']
        return pickle.loads(str(val))
    
    def _get_SDX_config_in_db(self):
        # Returns the SDX configuration dictionary if it exists or None if it
        # does not.
        key = 'sdx_config'
        d = self.config_table.find_one(key=key)
        if d == None:
            return None
        val = d['value']
        return pickle.loads(str(val))

    def _get_switch_internal_config_count(self):
        # Returns a count of internal configs.
        d = self.config_table.find()
        count = 0
        for entry in d:
            print "---------CW--ENTRY:-------------"
            print entry
            if (entry['key'] == 'lcip' or
                    entry['key'] == 'manifest_filename' or
                    entry['key'] == 'ryucxnport'):
                continue
            count += 1
        return count

    def _add_switch_internal_config_to_db(self, dpid, internal_config):
        # Pushes a switch internal_config into the db.
        # key: "<dpid>"
        # value: <internal_config>
        key = dpid
        value = pickle.dumps(internal_config)
        if self._get_switch_internal_config(dpid) == None:
            self.logger.info("Adding new internal_config for DPID %s" % dpid)
            self.config_table.insert({'key': key, 'value': value})
        else:
            # Already exists, must update
            self.logger.info("updating internal_config for DPID %s" % dpid)
            self.config_table.update({'key': key, 'value': value},
                                     ['key'])

    def _get_manifest_filename_in_db(self):
        # Returns the manifest filename if it exists or None if it does not.
        key = 'manifest_filename'
        d = self.config_table.find_one(key=key)
        if d == None:
            return None
        val = d['value']
        return pickle.loads(str(val))

    def _get_config_filename_in_db(self):
        # Returns the manifest filename if it exists or None if it does not.
        key = 'manifest_filename'
        d = self.config_table.find_one(key=key)
        print "------------_get_config_filename_in_db-----------"
        print d
        if d == None:
            return None
        val = d['value']
        return pickle.loads(str(val))

    def _setup(self, options): 
        self.manifest = options.manifest
        dbname = options.database

        # Get DB connection and tables set up.
        db_tuples = [('config_table', self.name+"-config")]
        self._initialize_db(dbname, db_tuples)

        # If manifest is None, try to get the name from the DB. This is needed
        # for the LC's RyuTranslateInterface
        if self.manifest == None:
            self.manifest = self._get_manifest_filename_in_db()
        elif (self.manifest != self._get_manifest_filename_in_db() and
              None != self._get_manifest_filename_in_db()):
            # Make sure it matches!
            #FIXME: Should we force evertying to be imported if different.
            raise Exception("Stored and passed in manifest filenames don't match up %s:%s" %
                            (str(self.manifest),
                             str(self._get_manifest_filename_in_db())))
       
        self.conf_file = None 
        # If the conf_name is None, try to get the name from the DB.
        if self.conf_file == None:
            self.conf_file = self._get_config_filename_in_db()
        elif (self.conf_file != self._get_config_filename_in_db() and
              None != self._get_config_filename_in_db()):
            # Make sure it matches!
            # FIXME: Should we force everything to be imported if different.
            raise Exception("Stored and passed in manifest filenames don't match up %s:%s" %
                            (str(self.conf_file),
                             str(self._get_config_filename_in_db())))

        # Get config file, if it exists
        try:
            self.logger.info("Opening config file %s" % self.conf_file)
            with open(self.conf_file) as data_file:
                data = json.load(data_file)
            lcdata = data['localcontrollers'][self.name]
        except Exception as e:
            self.logger.warning("exception when opening config file: %s" %
                                str(e))

        # Get Manifest, if it exists
        try:
            self.logger.info("Opening manifest file %s" % self.manifest)
            with open(self.manifest) as data_file:
                data = json.load(data_file)
            lcdata = data['localcontrollers'][self.name]
            self.logger.info("Successfully opened manifest file %s" %
                             self.manifest)
        except Exception as e:
            self.logger.warning("Exception when opening manifest file: %s" %
                                str(e))
            lcdata = None
        self._add_manifest_filename_to_db(self.manifest)

        # Check if things are stored in the db. If they are, use them.
        # If not, load from the manifest and store to DB.

        # Switch Config
        #FIXME: This isn't used here. It's used in RyuTranslateInterface.
        #Not storing it for now, despite having the helper functions written.

        # Ryu Config
        config = self._get_ryu_config_in_db()
        if config != None:
            self.ryu_cxn_port = config['ryucxninternalport']
            self.openflow_port = config['openflowport']
        else:
            self.ryu_cxn_port = lcdata['internalconfig']['ryucxninternalport']
            self.openflow_port = lcdata['internalconfig']['openflowport']
            self._add_ryu_config_to_db({'ryucxninternalport':self.ryu_cxn_port,
                                        'openflowport':self.openflow_port})

        # LC Config
        config = self._get_LC_config_in_db()
        if config != None:
            self.lcip = config['lcip']
        else:
            self.lcip = lcdata['lcip']
            self._add_LC_config_to_db({'lcip':self.lcip})
            
        # SDX Config
        config = self._get_SDX_config_in_db()
        if config != None:
            self.sdxip = config['sdxip']
            self.sdxport = config['sdxport']
        else:
            # Well, not quite the manifest...
            self.sdxip = options.host
            self.sdxport = options.sdxport
            self._add_SDX_config_to_db({'sdxip':self.sdxip,
                                        'sdxport':self.sdxport})   
        # OpenFlow/Switch configuration data
        config_count = self._get_switch_internal_config_count()
        print "------config_count------"
        print config_count
        if config_count == 0:
            # Nothing configured, get configs from config file
            for entry in lcdata['switchinfo']:
                dpid = str(int(entry['dpid'], 0))  # This is to normalize the DPID.
                ic = entry['internalconfig']
                ic['name'] = entry['name']
                self._add_switch_internal_config_to_db(dpid, ic)
  
        internal_config = self._get_switch_internal_config(204) 
        if internal_config == None:
            print "internal_config == None"
        #if 'managementvlan' in internal_config.keys():
        #    managementvlan = internal_config['managementvlan']
        #if 'managementvlanports' in internal_config.keys():
        #    managementvlanports = internal_config['managementvlanports']
        #print managementvlan
            
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
        self.logger.debug("SDX Controller Connection - %s: %s" % 
                          (hex(id(self.sdx_connection)), self.sdx_connection))

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
        
        self.logger.warning("Connection fully established to SDX")

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

        self.logger.debug("install_rule_sdxmsg: %d:%s:%s" % (cookie, 
                                                             switch_id, 
                                                             rule))

        self.rm.add_rule(cookie, switch_id, rule, RULE_STATUS_INSTALLING)
        self.switch_connection.send_command(switch_id, rule)
        self.rm.list_all_rules(True)
        self.logger.debug("----------self.rm.list_all_rules complete---------------") 
        #FIXME: This should be moved to somewhere where we have positively
        #confirmed a rule has been installed. Right now, there is no such
        #location as the LC/RyuTranslateInteface protocol is primitive.
        self.rm.set_status(cookie, switch_id, RULE_STATUS_ACTIVE)
        config = self._get_switch_internal_config(switch_id)
        self.logger.debug("---------CW: _get_switch_internal_config----------------")
        print config

    def remove_all_rules_sdxmsg(self):
        '''CW: this part is not working yet'''
        ''' Removes all rules based on cookie sent from the SDX Controller. '''
        rules = self.rm.list_all_rules()

        if rules == []:
            self.logger.error("remove_rule_sdxmsg: trying to remove a rule that doesn't exist %s" % cookie)
            return
        for rule in rules:
            self.logger.debug("Removing rule:")
            self.logger.debug(rule)
            self.logger.debug("Type of rule:")
            self.logger.debug(type(rule))
            cookie = rule.get_cookie()
            switch_id = rule.get_switch_id()
            self.rm.set_status(cookie, switch_id, RULE_STATUS_DELETING)
            self.switch_connection.remove_rule(switch_id, cookie)

            #FIXME: This should be moved to somewhere where we have positively
            #confirmed a rule has been removed. Right now, there is no such
            #location as the LC/RyuTranslateInteface protocol is primitive.
            self.rm.set_status(cookie, switch_id, RULE_STATUS_REMOVED)
            self.rm.rm_rule(cookie, switch_id)

    def remove_rule_sdxmsg(self, msg):
        ''' Removes rules based on cookie sent from the SDX Controller. If we do
            not have a rule under that cookie, odds are it's for the previous 
            instance of this LC. Log and drop it.
        '''
        switch_id = msg.get_data()['switch_id']
        cookie = msg.get_data()['cookie']
        rules = self.rm.get_rules(cookie, switch_id)

        self.logger.debug("--- MCEVIK: remove_rule_sdxmsg - rules: %s" % (rules.__dict__)) 

        self.logger.debug("remove_rule_sdxmsg:  %d:%s:%s" % (cookie, 
                                                             switch_id, 
                                                             rules))

        if rules == []:
            self.logger.error("remove_rule_sdxmsg: trying to remove a rule that doesn't exist %s" % cookie)
            return

        self.rm.set_status(cookie, switch_id, RULE_STATUS_DELETING)
        self.switch_connection.remove_rule(switch_id, cookie)

        #FIXME: This should be moved to somewhere where we have positively
        #confirmed a rule has been removed. Right now, there is no such
        #location as the LC/RyuTranslateInteface protocol is primitive.
        self.rm.set_status(cookie, switch_id, RULE_STATUS_REMOVED)
        self.rm.rm_rule(cookie, switch_id)

    def _initial_rule_install(self, rule):
        ''' This builds up a list of rules to be installed. 
            _initial_rules_complete() actually kicks off the install.
        '''
        c = rule.get_data()['rule'].get_cookie()
        sw = rule.get_data()['rule'].get_switch_id()

        self.rm.add_initial_rule(rule, c, sw)

    def _initial_rules_complete(self):
        ''' Calls the LCRuleManager to get delete and add rule lists, then 
            deletes outdated rules and adds new rule.
        '''
        delete_list = []
        add_list = []

        (delete_list, add_list) = self.rm.initial_rules_complete()
        self.rm.clear_initial_rules()

        for (entry, cookie, switch_id) in add_list:
            # Cookie isn't needed
            self.install_rule_sdxmsg(entry)
            
        for (entry, cookie, switch_id) in delete_list:
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

        elif cmd == SM_INTER_RYU_FAILURE:
            # This one's different. This is a failure we have to handle.
            # - Kill the RyuControllerInterface (RCI)
            # - Restart RCI
            self.logger.error("Received SM_INTER_RYU_FAILURE(%s), killing RCI" %
                              opaque)
            self.switch_connection = None
            self._setup_switch()
            

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

    parser.add_argument("-d", "--database", dest="database", type=str, 
                        action="store", help="Specifies the database ", 
                        default=":memory:")
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

    config_info_present = options.manifest or options.database
    if not config_info_present or not options.name:
        parser.print_help()
        exit()

    lc = LocalController(False, options)
    lc._main_loop()

