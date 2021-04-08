from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals
# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


from future import standard_library
standard_library.install_aliases()
from builtins import hex
from builtins import str
from builtins import object
import logging
import threading
import dataset
import pickle as pickle
import requests
import json
from time import sleep

# Generic AtlanticWave/SDX imports
from shared.LCAction import *
from shared.LCFields import *
from shared.LCRule import *
from shared.ofconstants import *
from localctlr.oftables import *
from localctlr.InterRyuControllerConnectionManager import *

# Ryu libraries
from ryu import cfg
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.utils import hex_array
from ryu.lib.packet import packet, ethernet, ether_types

# LC Rule Types
from shared.MatchActionLCRule import *
from shared.VlanTunnelLCRule import *
from shared.LearnedDestinationLCRule import *
from shared.EdgePortLCRule import *
from shared.L2MultipointEndpointLCRule import *
from shared.L2MultipointFloodLCRule import *
from shared.L2MultipointLearnedDestinationLCRule import *
from shared.FloodTreeLCRule import *
from shared.ManagementVLANLCRule import *
from shared.ManagementLCRecoverRule import *
from shared.ManagementSDXRecoverRule import *

LOCALHOST = "127.0.0.1"

CONF = cfg.CONF

L2MULTIPOINTCORSABWDISABLED = False


class TranslatedRuleContainer(object):
    ''' Parent class for holding both LC and Corsa rules '''
    pass


class TranslatedLCRuleContainer(TranslatedRuleContainer):
    ''' Used by RyuTranslateInterface to track translations of LCRules. Contains
        Ryu-friendly objects. Not for use outside RyuTranslateInterface. '''

    def __init__(self, cookie, table, priority, match, instructions,
                 buffer_id=None, idle_timeout=0, hard_timeout=0):
        self.cookie = cookie
        self.table = table
        self.priority = priority
        self.match = match
        self.instructions = instructions
        self.buffer_id = buffer_id
        self.idle_timeout = idle_timeout
        self.hard_timeout = hard_timeout

    def __str__(self):
        return "%s:%s:%s\n%s\n%s\n%s:%s:%s" % (self.cookie, self.table,
                                               self.priority, self.match,
                                               self.instructions,
                                               self.buffer_id,
                                               self.idle_timeout,
                                               self.hard_timeout)

    def __repr__(self):
        return "%s:%s:%s" % (self.cookie, self.match, self.instructions)

    def get_cookie(self):
        return self.cookie

    def get_table(self):
        return self.table

    def get_priority(self):
        return self.priority

    def get_match(self):
        return self.match

    def get_instructions(self):
        return self.instructions

    def get_buffer_id(self):
        return self.buffer_id

    def get_idle_timeout(self):
        return self.idle_timeout

    def get_hard_timeout(self):
        return self.hard_timeout


class TranslatedLCRuleGroupContainer(TranslatedRuleContainer):
    ''' Used by RyuTranslateInterface to track translations of Group Creation Rule in P2MP. Contains
        Ryu-friendly objects. Not for use outside RyuTranslateInterface. '''

    def __init__(self, cookie, table, groupType, group_id, instructions, weight=100, watch_port=0,watch_group=0):
        self.cookie = cookie
        self.table = table
        self.groupType = groupType
        self.group_id = group_id
        self.weight = weight
        self.watch_port = watch_port
        self.watch_group = watch_group
        self.instructions = instructions

    def __str__(self):
        return "%s:%s:%s\n%s\n%s\n%s:%s:%s" % (self.cookie, self.table,
                                               self.groupType, self.group_id,
                                               self.weight,
                                               self.watch_port,
                                               self.watch_group,
                                               self.instructions)

    def __repr__(self):
        return "%s:%s:%s:%s" % (self.cookie, self.groupType,self.group_id,self.instructions)

    def get_cookie(self):
        return self.cookie

    def get_table(self):
        return self.table

    def get_groupType(self):
        return self.groupType

    def get_group_id(self):
        return self.group_id

    def get_weight(self):
        return self.weight

    def get_watch_port(self):
        return self.watch_port

    def get_watch_group(self):
        return self.watch_group

    def get_instructions(self):
        return self.instructions


class TranslatedCorsaRuleContainer(TranslatedRuleContainer):
    ''' Used by RyuTranslateInterface to track translations of Corsa Rules.
        Contains what is needed to make a REST request. '''

    def __init__(self, function, url, json, token, list_of_valid_responses):
        self.function = function
        self.url = url
        self.json = json
        self.token = token
        self.valid_responses = list_of_valid_responses

    def __str__(self):
        return "%s:%s:%s:%s" % (self.url, self.json,
                                self.valid_responses, self.token)

    def get_function(self):
        # Function should be "patch", "post", or "get"
        return self.function

    def get_url(self):
        return self.url

    def get_json(self):
        return self.json

    def get_token(self):
        return self.token

    def get_valid_responses(self):
        return self.valid_responses


class GotoTable(LCAction):
    ''' This performs a goto table instruction in OpenFlow.
        This is not part of shared/LCAction.py because we don't want the
        SDXController-level rules to use it, thus it's here. It's very similar
        to all the other LCActions. '''

    def __init__(self, table):
        self.table = table
        super(GotoTable, self).__init__("GotoTable")

    def __str__(self):
        retstr = "%s:%s" % (self._name, self.table)
        return retstr

    def get(self):
        return self.table


class RyuTranslateInterface(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(RyuTranslateInterface, self).__init__(*args, **kwargs)

        loggerid = 'localcontroller.ryutranslateinterface'
        logfilename = 'localcontroller-%s.log' % CONF['atlanticwave']['lcname']
        debuglogfilename = 'debug' + logfilename
        self._setup_loggers(loggerid, logfilename, debuglogfilename)
        self.logger.warning("Starting up RyuTranslateInterface")

        # Configuration file + parsing
        self.name = CONF['atlanticwave']['lcname']
        self.conf_file = CONF['atlanticwave']['conffile']
        self.db_name = CONF['atlanticwave']['dbfile']
        self.control_topo = CONF['atlanticwave']['controltopo']

        if self.db_name == "":
            self.db_name = ":memory:"

        # Import configuration information - this includes pulling information
        # from the stored DB (if there is anything), and from the options passed
        # in during startup (including the manifest file)
        self._setup()

        # Establish connection to RyuControllerInterface
        self.inter_cm = InterRyuControllerConnectionManager()
        self.logger.info("RyuTranslateInterface: Opening outbound connection to RyuConnectionInterface on %s:%s" % (
        self.lcip, self.ryu_cxn_port))
        self.inter_cm_cxn = self.inter_cm.open_outbound_connection(self.lcip,
                                                                   self.ryu_cxn_port)

        self.datapaths = {}
        self.current_of_cookie = 0

        # Spawn main_loop thread
        self.loop_thread = threading.Thread(target=self.main_loop)
        self.loop_thread.daemon = True
        self.loop_thread.start()

        # Start up the connection to switch?

        # PacketIn callback structure setup
        self.packet_in_cbs = {}

        # TODO: Reestablish connection? Do I have to do anything?
        self.logger.warning("%s initialized: %s" % (self.__class__.__name__,
                                                    hex(id(self))))

    # The two _setup_loggers function is from lib/AtlanticWaveModule.py.
    # This cannot inherit from AtlanticWaveModule or any of it's children, so we
    # need to manually include some of it's functionality.
    def _setup_loggers(self, loggerid, logfilename=None, debuglogfilename=None):
        ''' Internal function for setting up the logger formats. '''
        # reused from https://github.com/sdonovan1985/netassay-ryu/blob/master/base/mcm.py
        # Modified based on https://stackoverflow.com/questions/7173033/
        self.logger = logging.getLogger(loggerid)
        self.dlogger = logging.getLogger("debug." + loggerid)
        if logfilename != None:
            formatter = logging.Formatter('%(asctime)s %(name)-12s: %(thread)s %(levelname)-8s %(message)s')
            console = logging.StreamHandler()
            console.setLevel(logging.WARNING)
            console.setFormatter(formatter)
            logfile = logging.FileHandler(logfilename)
            logfile.setLevel(logging.DEBUG)
            logfile.setFormatter(formatter)
            self.logger.setLevel(logging.DEBUG)
            self.logger.addHandler(console)
            self.logger.addHandler(logfile)

        if debuglogfilename != None:
            formatter = logging.Formatter('%(asctime)s %(name)-12s: %(thread)s %(levelname)-8s %(message)s')
            console = logging.StreamHandler()
            console.setLevel(logging.DEBUG)
            console.setFormatter(formatter)
            logfile = logging.FileHandler(debuglogfilename)
            logfile.setLevel(logging.DEBUG)
            logfile.setFormatter(formatter)
            self.dlogger.setLevel(logging.DEBUG)

    def dlogger_tb(self):
        ''' Print out the current traceback. '''
        tbs = format_stack()
        all_tb = "Traceback: id: %s\n" % str(hex(id(self)))
        for line in tbs:
            all_tb = all_tb + line
        self.dlogger.warning(all_tb)

    def _initialize_db(self, db_filename):
        # Details on the setup:
        # https://dataset.readthedocs.io/en/latest/api.html
        # https://github.com/g2p/bedup/issues/38#issuecomment-43703630
        self.logger.critical("Connection to DB: %s" % db_filename)
        self.db = dataset.connect('sqlite:///' + db_filename,
                                  engine_kwargs={'connect_args':
                                                     {'check_same_thread': False}})
        # Try loading the tables, if they don't exist, create them.
        # <lcname>-config - Columns are 'key' and 'value'
        config_table_name = self.name + "-config"
        rule_table_name = self.name + "-rule"
        if config_table_name in self.db:
            self.logger.info("Trying to load %s from DB" % config_table_name)
            self.config_table = self.db.load_table(config_table_name)
            self.logger.info("Trying to load %s from DB" % rule_table_name)
            self.rule_table = self.db.load_table(rule_table_name)
        else:
            # If load_table() fails, that's fine! It means that the table
            # doesn't yet exist. So, create it.
            self.logger.info("Failed to load %s from DB, creating new table" %
                             config_table_name)
            self.config_table = self.db[config_table_name]
            self.rule_table = self.db[rule_table_name]

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

    def _add_config_filename_to_db(self, manifest_filename):
        # Pushes LC network configuration info into the DB.
        # key: "manifest_filename"
        # value: manifest_filename
        key = 'manifest_filename'
        value = pickle.dumps(manifest_filename)
        if self._get_manifest_filename_in_db() == None:
            self.logger.info("Adding new manifest filename %s" %
                             manifest_filename)
            self.config_table.insert({'key': key, 'value': value})
        else:
            # Already exists, must update.
            self.logger.info("Updating manifest filename %s" %
                             manifest_filename)
            self.config_table.update({'key': key, 'value': value},
                                     ['key'])

    def _add_lcip_to_db(self, lcip):
        # Pushes LC IP info into the DB.
        # key: "lcip"
        # value: lcip
        key = 'lcip'
        value = pickle.dumps(lcip)
        if self._get_lcip_in_db() == None:
            self.logger.info("Adding new lcip %s" %
                             lcip)
            self.config_table.insert({'key': key, 'value': value})
        else:
            # Already exists, must update.
            self.logger.info("Updating lcip %s" %
                             lcip)
            self.config_table.update({'key': key, 'value': value},
                                     ['key'])

    def _add_ryu_cxn_port_to_db(self, ryucxnport):
        # Pushes Ryu Cxn Port info into the DB.
        # key: "ryucxnport"
        # value: ryucxnport
        key = 'ryucxnport'
        value = pickle.dumps(ryucxnport)
        if self._get_lcip_in_db() == None:
            self.logger.info("Adding new ryucxnport %s" %
                             ryucxnport)
            self.config_table.insert({'key': key, 'value': value})
        else:
            # Already exists, must update.
            self.logger.info("Updating ryucxnport %s" %
                             ryucxnport)
            self.config_table.update({'key': key, 'value': value},
                                     ['key'])

    def _get_switch_internal_config(self, dpid):
        ''' Gets switch internal config information based on datapath passed in
            Pulls information from the DB.
        '''
        key = str(dpid)
        d = self.config_table.find_one(key=key)
        if d == None:
            return None
        val = d['value']
        return pickle.loads(val)

    def _get_switch_internal_config_count(self):
        # Returns a count of internal configs.
        d = self.config_table.find()
        count = 0
        for entry in d:
            if (entry['key'] == 'lcip' or
                    entry['key'] == 'manifest_filename' or
                    entry['key'] == 'ryucxnport'):
                continue
            count += 1
        return count

    def _get_config_filename_in_db(self):
        # Returns the manifest filename if it exists or None if it does not.
        key = 'manifest_filename'
        d = self.config_table.find_one(key=key)
        if d == None:
            return None
        val = d['value']
        return pickle.loads(val)

    def _get_lcip_in_db(self):
        # Returns the lcip if it exists or None if it does not.
        key = 'lcip'
        d = self.config_table.find_one(key=key)
        if d == None:
            return None
        val = d['value']
        return pickle.loads(val)

    def _get_ryu_cxn_port_in_db(self):
        # Returns the Ryu Cxn Port if it exists or None if it does not.
        key = 'ryucxnport'
        d = self.config_table.find_one(key=key)
        if d == None:
            return None
        val = d['value']
        return pickle.loads(val)

    def _setup(self):
        dbname = self.db_name

        # Get DB connection and tables set up.
        self._initialize_db(dbname)

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

        # Check if things are stored in the db. If they are, use them.
        # If  not, load from the config file and store to the DB.

        # LCIP
        config = self._get_lcip_in_db()
        if config != None:
            self.lcip = config
        else:
            self.lcip = lcdata['lcip']
            self._add_lcip_to_db(self.lcip)

        # Ryu Connection Port
        config = self._get_ryu_cxn_port_in_db()
        if config != None:
            self.ryu_cxn_port = config
        else:
            self.ryu_cxn_port = lcdata['internalconfig']['ryucxninternalport']
            self._add_ryu_cxn_port_to_db(self.ryu_cxn_port)

        # OpenFlow/Switch configuration data
        config_count = self._get_switch_internal_config_count()
        if config_count == 0:
            # Nothing configured, get configs from config file
            for entry in lcdata['switchinfo']:
                dpid = str(int(entry['dpid'], 0))  # This is to normalize the DPID.
                ic = entry['internalconfig']
                ic['name'] = entry['name']
                self._add_switch_internal_config_to_db(dpid, ic)

    def main_loop(self):
        ''' This is the main loop that reads and works with the data coming from
            the Inter-Ryu Connection. It loops through, looking for new events.
            If there is one to be processed, process it.
        '''

        # First, wait till we have at least one datapath.
        self.logger.info("Looking for datapath")
        while len(list(self.datapaths.keys())) == 0:
            self.logger.info("Waiting " + str(self.datapaths))
            sleep(1)

        # Send message over to the Controller Interface to let it know that
        # we have at least one switch.
        self.inter_cm_cxn.send_cmd(ICX_DATAPATHS,
                                   str(self.datapaths))

        while True:

            # FIXME - This is static: only installing rules right now.
            event_type, event_data = self.inter_cm_cxn.recv_cmd()
            (switch_id, event) = event_data
            if switch_id not in list(self.datapaths.keys()):
                self.logger.warning("switch_id %s does not match known switches: %s" %
                                    (switch_id, list(self.datapaths.keys())))

                # FIXME - Need to update this for sending errors back
                continue

            datapath = self.datapaths[switch_id]

            if event_type == ICX_ADD:
                self.install_rule(datapath, event)
            elif event_type == ICX_REMOVE:
                self.remove_rule(datapath, event)

            ###except Exception as e:
            ###    self.logger.error("main_loop: Caught %s" % e)
            ###    self.logger.error("main_loop: Exiting!")
            ###    exit()
            # FIXME - There may need to be more options here. This is just a start.

    # Handles switch connect event
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        self.logger.warning("Connection from: " + str(ev.msg.datapath.id) + " for " + str(self))
        self.datapaths[ev.msg.datapath.id] = ev.msg.datapath

        # Call bootstrapping for switch functions
        self._new_switch_bootstrapping(ev)

    # From the Ryu mailing list: https://sourceforge.net/p/ryu/mailman/message/33584125/
    @set_ev_cls(ofp_event.EventOFPErrorMsg,
                [CONFIG_DISPATCHER, MAIN_DISPATCHER])
    def error_msg_handler(self, ev):
        msg = ev.msg
        self.logger.error('OFPErrorMsg received: type=0x%02x code=0x%02x '
                          'message=%s',
                          msg.type, msg.code, hex_array(msg.data))

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        # Look through the packet_in_cbs's dictionary and send it onwards.
        cookie = ev.msg.cookie

        if cookie in self.packet_in_cbs:
            cb = self.packet_in_cbs[cookie]
            cb(ev)
        else:
            self.logger.error('Packet-in with cookie 0x%02x has no callback.',
                              cookie)

    def _new_switch_bootstrapping(self, ev):
        ''' This bootstraps new switches when they come online. '''
        # Null out all tables
        # Install default rules on all tables
        # For ALL tables except the last table:
        #   - Create a MatchActionLCRule to send to next table. Priority 0
        # Learning table edge ports are handled by rules coming from the
        # SDX controller at startup.
        switch_id = 0  # This is unimportant:
        # it's never used in the translation
        datapath = ev.msg.datapath

        self.remove_all_flows(datapath)

        of_cookie = self._get_new_OF_cookie(-1,-1)  # FIXME: magic number
        results = []

        try:
            with open(self.control_topo) as control_topo_file:
                controltopo = json.load(control_topo_file)
        except Exception as e:
            self.logger.warning("exception when opening control plane topology file: %s" %
                                str(e))
        
        # Get config file, if it exists
        try:
            self.logger.info("Opening config file %s" % self.conf_file)
            with open(self.conf_file) as data_file:
                data = json.load(data_file)
            lcdata = data['localcontrollers'][self.name]
        except Exception as e:
            self.logger.warning("exception when opening config file: %s" %
                                str(e))

        # TODO: double check the case where one lc has multiple switches
        portinfo = []
        switchname = ""
        for entry in lcdata['switchinfo']:
            if str(entry['dpid']) == str(datapath.id):
                self.logger.info("Found portinfo for %s" % entry['name'])
                portinfo = entry['portinfo']
                switchname = entry['name']

        if not portinfo:
            raise ValueError("DPID %s does not have port info" %
                             datapath.id)

        steiner_tree_dist_nodes = controltopo[switchname]

        managementvlanports = []
        for entry in portinfo:
            if entry['destination'] in steiner_tree_dist_nodes and 'dtn' not in entry['destination']:
                managementvlanports.append(int(entry['portnumber']))
        
        if not managementvlanports:
            raise ValueError("DPID %s does not have valid steiner tree" %
                             datapath.id)
            return

        # In-band Communication
        # Extract management VLAN and ports from the manifest
        internal_config = self._get_switch_internal_config(datapath.id)
        if internal_config == None:
            raise ValueError("DPID %s does not have internal_config" %
                             datapath.id)
            return
        if 'managementvlan' in list(internal_config.keys()):
            managementvlan = internal_config['managementvlan']
        else:
            raise ValueError("DPID %s does not have managementvlan" %
                             datapath.id)
            return
        
        # Old method that reads managementvlanports from manifest
        #if 'managementvlanports' in list(internal_config.keys()):
        #    managementvlanports = internal_config['managementvlanports']
        #else:
        #    raise ValueError("DPID %s does not have managementvlanports" %
        #                     datapath.id)
        #    return


        for table in ALL_TABLES_EXCEPT_LAST:
            matches = []  # FIXME: what's the equivalent of match(*)?
            actions = [Continue()]
            priority = PRIORITY_DEFAULT
            marule = MatchActionLCRule(switch_id, matches, actions)
            results += self._translate_MatchActionLCRule(datapath,
                                                         table,
                                                         of_cookie,
                                                         marule,
                                                         priority)

        # For last table
        #   - Create a default drop rule (if necessary needed). Priority 0
        for i in (managementvlanports):
            self.logger.debug("Using default management ports.")
            matches = [IN_PORT(i)]
            actions = [Drop()]
            priority = PRIORITY_DEFAULT_PLUS_ONE
            table = LASTTABLE
            marule = MatchActionLCRule(switch_id, matches, actions)
            results += self._translate_MatchActionLCRule(datapath,
                                                         table,
                                                         of_cookie,
                                                         marule,
                                                         priority)
        # Catch-all for those not in the same port
        matches = []
        actions = [Drop()]
        priority = PRIORITY_DEFAULT
        table = LASTTABLE
        marule = MatchActionLCRule(switch_id, matches, actions)
        results += self._translate_MatchActionLCRule(datapath,
                                                     table,
                                                     of_cookie,
                                                     marule,
                                                     priority)

        # In-band Communication
        # If the management VLAN needs to be setup, set it up.
        if 'managementvlan' in list(internal_config.keys()):
            managementvlan = internal_config['managementvlan']
            managementvlanports = internal_config['managementvlanports']
            untaggedmanagementvlanports = []
            if 'untaggedmanagementvlanports' in list(internal_config.keys()):
                untaggedmanagementvlanports = internal_config['untaggedmanagementvlanports']

            table = L2TUNNELTABLE
            mvrule = ManagementVLANLCRule(switch_id,
                                          managementvlan,
                                          managementvlanports,
                                          untaggedmanagementvlanports)
            results += self._translate_ManagementVLANLCRule(datapath,
                                                            table,
                                                            of_cookie,
                                                            mvrule)

        # Install default rules
        for rule in results:
            self.add_flow(datapath, rule)

    def _backup_port_recover(self, datapath, of_cookie, lc_recover_rule):
        '''Remove existing default port and use backup port'''
        self.logger.debug("got ManagementLCRecoverRule")
        self.logger.debug("Checking if backup port is available")
        switch_id = 0  # This is unimportant:
        # it's never used in the translation

        of_cookie = self._get_new_OF_cookie(-1, -1)  # FIXME: magic number
        results = []

        # In-band Communication
        # Extract management VLAN and ports from the manifest
        internal_config = self._get_switch_internal_config(datapath.id)
        if internal_config == None:
            raise ValueError("DPID %s does not have internal_config" %
                             datapath.id)
        if 'managementvlan' in list(internal_config.keys()):
            managementvlan = internal_config['managementvlan']
        if 'managementvlanports' in list(internal_config.keys()):
            managementvlanports = internal_config['managementvlanports']

        if 'managementvlanbackupports' in list(internal_config.keys()):
            managementvlanbackupports = internal_config['managementvlanbackupports']
        else:
            self.logger.debug("No backup port provided")
            return

        # In-band Communication
        # If the management VLAN needs to be setup, set it up.
        if 'managementvlan' in list(internal_config.keys()):
            managementvlan = internal_config['managementvlan']
            managementvlanports = internal_config['managementvlanports']
            untaggedmanagementvlanports = []
            if 'untaggedmanagementvlanports' in list(internal_config.keys()):
                untaggedmanagementvlanports = internal_config['untaggedmanagementvlanports']

            table = L2TUNNELTABLE
            mvrule = ManagementVLANLCRule(switch_id,
                                          managementvlan,
                                          managementvlanports,
                                          untaggedmanagementvlanports)
            results += self._translate_ManagementVLANLCRule(datapath,
                                                            table,
                                                            of_cookie,
                                                            mvrule)

        self.logger.debug("REMOVING default flows")
        # Install default rules
        for rule in results:
            self.remove_flow(datapath, rule)

        # Add backup management vlan ports
        results = []
        if 'managementvlan' in list(internal_config.keys()):
            managementvlan = internal_config['managementvlan']
            managementvlanbackupports = internal_config['managementvlanbackupports']
            untaggedmanagementvlanports = []
            if 'untaggedmanagementvlanports' in list(internal_config.keys()):
                untaggedmanagementvlanports = internal_config['untaggedmanagementvlanports']

            table = L2TUNNELTABLE
            mvrule = ManagementVLANLCRule(switch_id,
                                          managementvlan,
                                          managementvlanbackupports,
                                          untaggedmanagementvlanports)
            results += self._translate_ManagementVLANLCRule(datapath,
                                                            table,
                                                            of_cookie,
                                                            mvrule)

        self.logger.debug("ADDING backup management VLAN flows")
        # Install default rules
        for rule in results:
            self.add_flow(datapath, rule)

    def _backup_port_recover_from_sdx_msg(self, datapath, of_cookie, lc_recover_rule):
        '''Remove existing default port and use backup port'''
        self.logger.debug("got ManagementSDXRecoverRule from SDX message")
        self.logger.debug("Checking if backup port is available")
        switch_id = 0  # This is unimportant:
        # it's never used in the translation

        of_cookie = self._get_new_OF_cookie(-1, -1)  # FIXME: magic number
        results = []

        # In-band Communication
        # Extract management VLAN and ports from the manifest
        internal_config = self._get_switch_internal_config(datapath.id)
        if internal_config == None:
            raise ValueError("DPID %s does not have internal_config" %
                             datapath.id)
        if 'managementvlan' in list(internal_config.keys()):
            managementvlan = internal_config['managementvlan']
        if 'managementvlanports' in list(internal_config.keys()):
            managementvlanports = internal_config['managementvlanports']

        if 'sdxmanagementvlanbackupports' in list(internal_config.keys()):
            sdxmanagementvlanbackupports = internal_config['sdxmanagementvlanbackupports']
        else:
            self.logger.debug("No SDX management VLAN backup port provided")
            return

        # In-band Communication
        # If the management VLAN needs to be setup, set it up.
        if 'managementvlan' in list(internal_config.keys()):
            managementvlan = internal_config['managementvlan']
            managementvlanports = internal_config['managementvlanports']
            untaggedmanagementvlanports = []
            if 'untaggedmanagementvlanports' in list(internal_config.keys()):
                untaggedmanagementvlanports = internal_config['untaggedmanagementvlanports']

            table = L2TUNNELTABLE
            mvrule = ManagementVLANLCRule(switch_id,
                                          managementvlan,
                                          managementvlanports,
                                          untaggedmanagementvlanports)
            results += self._translate_ManagementVLANLCRule(datapath,
                                                            table,
                                                            of_cookie,
                                                            mvrule)

        self.logger.debug("REMOVING default flows")
        # Install default rules
        for rule in results:
            self.remove_flow(datapath, rule)

        # Add backup management vlan ports
        results = []
        if 'managementvlan' in list(internal_config.keys()):
            managementvlan = internal_config['managementvlan']
            sdxmanagementvlanbackupports = internal_config['sdxmanagementvlanbackupports']
            untaggedmanagementvlanports = []
            if 'untaggedmanagementvlanports' in list(internal_config.keys()):
                untaggedmanagementvlanports = internal_config['untaggedmanagementvlanports']

            table = L2TUNNELTABLE
            mvrule = ManagementVLANLCRule(switch_id,
                                          managementvlan,
                                          sdxmanagementvlanbackupports,
                                          untaggedmanagementvlanports)
            results += self._translate_ManagementVLANLCRule(datapath,
                                                            table,
                                                            of_cookie,
                                                            mvrule)

        self.logger.debug("ADDING SDX msg backup flows")
        # Install default rules
        for rule in results:
            self.add_flow(datapath, rule)

    def _translate_MatchActionLCRule(self, datapath, table,
                                     of_cookie, marule, priority=100):
        ''' This translates MatchActionLCRules. There is only one rule generated
            by any given MatchActionLCRule.
            Returns a list of TranslatedLCRuleContainers
        '''
        results = []

        # Translate all the pieces
        match = self._translate_LCMatch(datapath,
                                        marule.get_matches(),
                                        table)
        instructions = self._translate_LCAction(datapath,
                                                marule.get_actions(),
                                                table)

        # Make the TranslatedRuleContainer, and return it.
        trc = TranslatedLCRuleContainer(of_cookie, table, priority,
                                        match, instructions)
        results.append(trc)

        return results

    def _translate_VlanLCRule(self, datapath, table, of_cookie, vlanrule):
        ''' This translates VlanLCRules. This can generate one or two rules,
            depending on if this is a bidirectional tunnel (the norm) or not.
            Returns a list of TranslatedLCRuleContainers
        '''
        results = []
        internal_config = self._get_switch_internal_config(datapath.id)
        if internal_config == None:
            raise ValueError("DPID %s does not have internal_config" %
                             datapath.id)

        # Create Outbound Rule
        # There are two options here: Corsa or Non-Corsa. Non-Corsa is for
        # regular OpenFlow switches (such as OVS) and is more straight forward.
        # NOTE: if bandwidth isn't being reserved, use non-Corsa path.

        if (internal_config['corsaurl'] == "" or
                vlanrule.get_bandwidth() == 0):
            # Make the equivalent MatchActionLCRule, translate it, and use these
            # as the results. Easier translation!
            switch_id = 0  # This is unimportant:
            # it's never used in the translation
            matches = [IN_PORT(vlanrule.get_inport()),
                       VLAN_VID(vlanrule.get_vlan_in())]
            actions = [SetField(VLAN_VID(vlanrule.get_vlan_out())),
                       Forward(vlanrule.get_outport())]
            marule = MatchActionLCRule(switch_id, matches, actions)
            results += self._translate_MatchActionLCRule(datapath,
                                                         table,
                                                         of_cookie,
                                                         marule)

            # If bidirectional, create inbound rule
            if vlanrule.get_bidirectional() == True:
                matches = [IN_PORT(vlanrule.get_outport()),
                           VLAN_VID(vlanrule.get_vlan_out())]
                actions = [SetField(VLAN_VID(vlanrule.get_vlan_in())),
                           Forward(vlanrule.get_inport())]
                marule = MatchActionLCRule(switch_id, matches, actions)
                results += self._translate_MatchActionLCRule(datapath,
                                                             table,
                                                             of_cookie,
                                                             marule)

        else:
            # Corsa case is more complicated.
            # 4 OpenFlow rules needed:
            #   - Inbound port  on VLAN in  to BW-in-port    on VLAN out
            #   - BW-out-port   on VLAN out to Outbound port on VLAN out
            #   - BW-in-port    on VLAN out to Inbound port  on VLAN in
            #   - Outbound port on VLAN out to BW-out-port   on VLAN out

            # 1 Bandwidth Reservation REST rule needed
            #   - Set Bandwith information for the tunnel

            # OpenFlow rules are *very* similar to the non-Corsa case
            switch_id = 0  # This is unimportant:
            # it's never used in the translation
            matches = [IN_PORT(vlanrule.get_inport()),
                       VLAN_VID(vlanrule.get_vlan_in())]
            actions = [SetField(VLAN_VID(vlanrule.get_vlan_out())),
                       Forward(internal_config['corsabwin'])]
            marule = MatchActionLCRule(switch_id, matches, actions)
            results += self._translate_MatchActionLCRule(datapath,
                                                         table,
                                                         of_cookie,
                                                         marule)

            matches = [IN_PORT(internal_config['corsabwout']),
                       VLAN_VID(vlanrule.get_vlan_out())]
            actions = [SetField(VLAN_VID(vlanrule.get_vlan_out())),
                       Forward(vlanrule.get_outport())]
            marule = MatchActionLCRule(switch_id, matches, actions)
            results += self._translate_MatchActionLCRule(datapath,
                                                         table,
                                                         of_cookie,
                                                         marule)

            # If bidirectional, create inbound rule
            if vlanrule.get_bidirectional() == True:
                matches = [IN_PORT(internal_config['corsabwin']),
                           VLAN_VID(vlanrule.get_vlan_out())]
                actions = [SetField(VLAN_VID(vlanrule.get_vlan_in())),
                           Forward(vlanrule.get_inport())]
                marule = MatchActionLCRule(switch_id, matches, actions)
                results += self._translate_MatchActionLCRule(datapath,
                                                             table,
                                                             of_cookie,
                                                             marule)

                matches = [IN_PORT(vlanrule.get_outport()),
                           VLAN_VID(vlanrule.get_vlan_out())]
                actions = [SetField(VLAN_VID(vlanrule.get_vlan_out())),
                           Forward(internal_config['corsabwout'])]
                marule = MatchActionLCRule(switch_id, matches, actions)
                results += self._translate_MatchActionLCRule(datapath,
                                                             table,
                                                             of_cookie,
                                                             marule)

            # Bandwidth REST rules rely on the REST API. If it changes, then
            # this may need to be modified.
            bridge = internal_config['corsaratelimitbridge']
            vlan = vlanrule.get_vlan_out()
            bandwidth = vlanrule.get_bandwidth()

            # Find out the request_url
            tunnel_url = (internal_config['corsaurl'] + "api/v1/bridges/" +
                          bridge + "/tunnels?list=true")
            print()
            "Requesting tunnels from %s" % tunnel_url
            rest_return = requests.get(tunnel_url,
                                       headers={'Authorization':
                                                    internal_config['corsatoken']},
                                       verify=False)  # FIXME: HARDCODED

            print()
            "Looking for %s on ports %s" % (vlan,
                                            internal_config['corsaratelimitports'])

            for entry in rest_return.json()['list']:
                if (entry['vlan-id'] == vlan and
                        int(entry['port']) in internal_config['corsaratelimitports']):
                    request_url = entry['links']['self']['href']
                    # This implements Red/Green, per Corsa's spec. Anything over
                    # the CIR value (and not part of a CBS burst) will be marked
                    # red and dropped.
                    jsonval = [{'op': 'replace',
                                'path': '/meter/cir',
                                'value': bandwidth},
                               {'op': 'replace',
                                'path': '/meter/cbs',
                                'value': bandwidth},
                               {'op': 'replace',
                                'path': '/meter/eir',
                                'value': 0},
                               {'op': 'replace',
                                'path': '/meter/ebs',
                                'value': 0}]
                    valid_responses = [204]

                    print()
                    "Patching %s:%s" % (request_url, json)
                    results.append(TranslatedCorsaRuleContainer("patch",
                                                                request_url,
                                                                jsonval,
                                                                internal_config['corsatoken'],
                                                                valid_responses))

        # Return results to be used.
        return results

    def _translate_LearnedDestinationLCRule(self, datapath, switch_table,
                                            of_cookie, ldrule):
        ''' This translates LearnedDestinationLCRules. This will generate a
            single rule.
            Returns a list of TranslatedRuleContainers
        '''
        results = []
        switch_id = 0  # This is unimportant: it's never used in the translation
        matches = [ETH_DST(ldrule.get_dst_address())]
        actions = [Forward(ldrule.get_outport())]
        priority = PRIORITY_GENERIC_LEARNED
        marule = MatchActionLCRule(switch_id, matches, actions)
        results += self._translate_MatchActionLCRule(datapath,
                                                     switch_table,
                                                     of_cookie,
                                                     marule,
                                                     priority)
        return results

    def _translate_EdgePortLCRule(self, datapath, switch_table,
                                  of_cookie, eprule):
        ''' This translates EdgePortLCRules. EdgePortLCRules declare that this is
            an edge port, nothing more. This will generate a single rule.
            Returns a list of TranslatedRuleContainers
        '''
        results = []
        switch_id = 0  # This is unimportant: it's never used in the translation
        matches = [IN_PORT(eprule.get_edgeport())]
        actions = [Continue(), Forward(OFPP_CONTROLLER)]
        priority = PRIORITY_GENERIC_LEARNING
        marule = MatchActionLCRule(switch_id, matches, actions)
        results += self._translate_MatchActionLCRule(datapath,
                                                     switch_table,
                                                     of_cookie,
                                                     marule,
                                                     priority)
        return results

    def _translate_L2MultipointFloodLCRule(self, datapath, switch_table,
                                           of_cookie, mpfrule):
        ''' This translates L2MultipointFloodLCRules. L2MultipointFloodLCRules
            are for ports that are on the interior of a Steiner tree that
            connects L2Multipoint LANs. Endpoint switches use
            L2MultipointEndpointLCRules instead.
            Returns a list of TranslatedRuleContainers
        '''
        results = []
        switch_id = 0  # This is unimportant: it's never used in the translation

        vlan = mpfrule.get_intermediate_vlan()
        for port in mpfrule.get_flooding_ports():
            matches = [IN_PORT(port), VLAN_VID(vlan)]
            actions = []
            for outport in mpfrule.get_flooding_ports():
                if outport != port:
                    actions.append(Forward(outport))
            priority = PRIORITY_L2M_FLOOD_FORWARDING
            marule = MatchActionLCRule(switch_id, matches, actions)
            results += self._translate_MatchActionLCRule(datapath,
                                                         switch_table,
                                                         of_cookie,
                                                         marule,
                                                         priority)
        return results

    def _translate_L2MultipointEndpointLCRule(self, datapath,
                                              endpoint_table,
                                              translate_table,
                                              flood_table,
                                              learning_table,
                                              of_cookie, mperule):
        ''' This translates L2MultipointEndpointLCRules.
            L2MultipointEndpointLCRules are uses for endpoints on a Steiner tree
            connecting L2Multipoint LANs. These handle bandwidth management,
            VLAN rewriting for edge ports, flooding on the switch that has the
            endpoint, and learning rule installation.
            Interior switches on the Steiner tree are handled by the
            L2MultipointFloodLCRule instead, and are much simpler.
            Returns a list of TranslatedRuleContainers
        '''
        results = []
        internal_config = self._get_switch_internal_config(datapath.id)
        if internal_config == None:
            raise ValueError("DPID %s does not have internal_config" %
                             datapath.id)

        switch_id = 0  # This is unimportant: it's never used in the translation
        intermediate_vlan = mperule.get_intermediate_vlan()

        # Non-Corsa first
        if (internal_config['corsaurl'] == "" or
                L2MULTIPOINTCORSABWDISABLED):
            # Endpoint ports
            # - Translate VLANs on ingress on endpoint_table
            # - Install learning rules on intermediate VLAN on ingress on
            #   learning table
            for (port, vlan) in mperule.get_endpoint_ports_and_vlans():
                matches = [IN_PORT(port), VLAN_VID(vlan)]
                actions = [SetField(VLAN_VID(intermediate_vlan)), Continue()]
                priority = PRIORITY_L2MULTIPOINT
                marule = MatchActionLCRule(switch_id, matches, actions)
                results += self._translate_MatchActionLCRule(datapath,
                                                             endpoint_table,
                                                             of_cookie,
                                                             marule,
                                                             priority)

                matches = [IN_PORT(port), VLAN_VID(intermediate_vlan)]
                actions = [Continue(), Forward(OFPP_CONTROLLER)]
                priority = PRIORITY_L2MULTIPOINT_LEARNING
                marule = MatchActionLCRule(switch_id, matches, actions)
                results += self._translate_MatchActionLCRule(datapath,
                                                             learning_table,
                                                             of_cookie,
                                                             marule,
                                                             priority)

            # Endpoint and Flooding ports.
            # - Install flooding rules on flood table
            flooding_ports = mperule.get_flooding_ports()
            endpoint_ports = [port for (port, vlan) in
                              mperule.get_endpoint_ports_and_vlans()]
            ports = flooding_ports + endpoint_ports

            for port in ports:
                matches = [IN_PORT(port), VLAN_VID(intermediate_vlan)]
                actions = []
                for outport in flooding_ports:
                    if outport != port:
                        actions.append(Forward(outport))
                for (outport, vlan) in mperule.get_endpoint_ports_and_vlans():
                    if outport != port:
                        actions.append(SetField(VLAN_VID(vlan)))
                        actions.append(Forward(outport))
                priority = PRIORITY_L2M_FLOOD_FORWARDING
                marule = MatchActionLCRule(switch_id, matches, actions)
                results += self._translate_MatchActionLCRule(datapath,
                                                             flood_table,
                                                             of_cookie,
                                                             marule,
                                                             priority)

                matches = [IN_PORT(port),
                           VLAN_VID(intermediate_vlan),
                           ETH_DST('ff:ff:ff:ff:ff:ff')]
                # Same actions as above, no need to rebuild
                priority = PRIORITY_L2M_BROADCAST_FORWARDING
                marule = MatchActionLCRule(switch_id, matches, actions)
                results += self._translate_MatchActionLCRule(datapath,
                                                             flood_table,
                                                             of_cookie,
                                                             marule,
                                                             priority)

        # Corsa Case
        else:
            # Endpoint rules

            self.logger.debug("L2MultipointEndpointLCRule: Corsa Case L2MULTIPOINTCORSABWDISABLED %s " % (L2MULTIPOINTCORSABWDISABLED))

            for (port, vlan) in mperule.get_endpoint_ports_and_vlans():
                self.logger.debug("L2MultipointEndpointLCRule: port: %s -  vlan: %s" % (port, vlan))
                self.logger.debug("L2MultipointEndpointLCRule: IN_PORT: %s -  VLAN_VID: %s" % (IN_PORT(port), VLAN_VID(vlan)))
                bridge = internal_config['corsabridge']
                bridge_ratelimit_l2mp = internal_config['corsaratelimitbridgel2mp']
                bandwidth = mperule.get_bandwidth()
                
                port_url_bridge = (internal_config['corsaurl'] + "api/v1/bridges/" +
				       bridge + "/tunnels")
                       
                port_url_bridge_ratelimit_l2mp = (internal_config['corsaurl'] + "api/v1/bridges/" +
						      bridge_ratelimit_l2mp + "/tunnels")
                              
                valid_responses = [201]
                
                l2mp_bw_in_port = vlan
                l2mp_bw_out_port = int(intermediate_vlan) + 10000

                self.logger.debug("L2MultipointEndpointLCRule: l2mp_bw_in_port: %s -  l2mp_bw_out_port: %s" % (l2mp_bw_in_port, l2mp_bw_out_port))


		        # Create tunnels and ofports on corsabridge
		        # 1422  --> 5
		        # 10001 --> 6

                request_url = port_url_bridge

                jsonval = {'ofport': l2mp_bw_out_port,
				'port': internal_config['corsabwoutl2mp'],
				'vlan-id': vlan,
				'shaped-rate': bandwidth}
                
                self.logger.debug("L2MultipointEndpointLCRule: Tunnel attach %s:%s" % (request_url, jsonval))
                results.append(TranslatedCorsaRuleContainer("post",
    							 request_url,
    							 jsonval,
    							 internal_config['corsatoken'],
    							 valid_responses))
                                 
                jsonval = {'ofport': l2mp_bw_in_port,
				'port': internal_config['corsabwinl2mp'],
				'vlan-id': vlan,
				'shaped-rate': bandwidth}

                self.logger.debug("L2MultipointEndpointLCRule: Tunnel attach %s:%s" % (request_url, jsonval))
                results.append(TranslatedCorsaRuleContainer("post",
								 request_url,
								 jsonval,
								 internal_config['corsatoken'],
								 valid_responses))


		        # Create tunnels and ofports on corsaratelimitbridgel2mp (br19)
		        # 1422  --> 7
		        # 10001 --> 8
	 
                request_url = port_url_bridge_ratelimit_l2mp

                jsonval = {'ofport': l2mp_bw_in_port,
				'port': internal_config['corsaratelimitportsl2mp'][0],
				'vlan-id': vlan,
				'shaped-rate': bandwidth}
                self.logger.debug("L2MultipointEndpointLCRule: Tunnel attach %s:%s" % (request_url, jsonval))
                results.append(TranslatedCorsaRuleContainer("post",
								 request_url,
								 jsonval,
								 internal_config['corsatoken'],
								 valid_responses))

                jsonval = {'ofport': l2mp_bw_out_port,
				'port': internal_config['corsaratelimitportsl2mp'][1],
				'vlan-id': vlan,
				'shaped-rate': bandwidth}

                self.logger.debug("L2MultipointEndpointLCRule: Tunnel attach %s:%s" % (request_url, jsonval))
                results.append(TranslatedCorsaRuleContainer("post",
								 request_url,
								 jsonval,
								 internal_config['corsatoken'],
								 valid_responses))



            self.logger.debug("L2MultipointEndpointLCRule: mperule.get_flooding_ports           : %s" % (mperule.get_flooding_ports()))
            self.logger.debug("L2MultipointEndpointLCRule: mperule.get_endpoint_ports_and_vlans : %s" % (mperule.get_endpoint_ports_and_vlans()))

            # Endpoint ports
            # - Translate VLANs on ingress on endpoint_table
            # - Install learning rules on intermediate VLAN on ingress on
            #   learning table

            self.logger.debug("L2MultipointEndpointLCRule: ENDPOINT TABLE and LEARNING TABLE")
            for (port, vlan) in mperule.get_endpoint_ports_and_vlans():
		#self.logger.debug("--- L2MultipointEndpointLCRule: port: %s - vlan: %s" % (port, vlan))
                l2mp_bw_in_port = vlan
                l2mp_bw_out_port = int(intermediate_vlan) + 10000

                # Flow.1
                matches = [IN_PORT(port), VLAN_VID(vlan)]
                actions = []
                actions.append(Forward(l2mp_bw_in_port))
                priority = PRIORITY_L2MULTIPOINT
                marule = MatchActionLCRule(switch_id, matches, actions)
                results += self._translate_MatchActionLCRule(datapath,
                                                             endpoint_table,
                                                             of_cookie,
                                                             marule,
                                                             priority)

                # Flow.2
                matches = [IN_PORT(l2mp_bw_out_port), VLAN_VID(vlan)]
                actions = [SetField(VLAN_VID(intermediate_vlan)), Continue()]
                priority = PRIORITY_L2MULTIPOINT
                marule = MatchActionLCRule(switch_id, matches, actions)
                results += self._translate_MatchActionLCRule(datapath,
                                                             endpoint_table,
                                                             of_cookie,
                                                             marule,
                                                             priority)

                # Flow.3
                matches = [IN_PORT(l2mp_bw_out_port), VLAN_VID(intermediate_vlan)]
                actions = [Continue(), Forward(OFPP_CONTROLLER)]
                priority = PRIORITY_L2MULTIPOINT_LEARNING
                marule = MatchActionLCRule(switch_id, matches, actions)
                results += self._translate_MatchActionLCRule(datapath,
                                                             learning_table,
                                                             of_cookie,
                                                             marule,
                                                             priority)

            self.logger.debug("L2MultipointEndpointLCRule: FLOOD TABLE")
            # Endpoint and Flooding ports.
            # - Install flooding rules on flood table
            flooding_ports = mperule.get_flooding_ports()
            endpoint_ports = [port for (port, vlan) in
                              mperule.get_endpoint_ports_and_vlans()]
            self.logger.debug("L2MultipointEndpointLCRule: FLOOD TABLE 
                               mperule.get_flooding_ports           : %s" % 
                               (flooding_ports))
            self.logger.debug("L2MultipointEndpointLCRule: FLOOD TABLE 
                               mperule.get_endpoint_ports_and_vlans : %s" % 
                               (endpoint_ports))


            # Flooding ports

            if len(flooding_ports) > 1 :
                use_grouptable = 1

                # Creating an indirect group for vlan tranlation in the switch 
                # that is also an interior node in the Steiner tree.
                groupType = datapath.ofproto.OFPGT_INDIRECT
                group_id = int(intermediate_vlan)
                group_list={}

                self.logger.debug("L2MultipointEndpointLCRule: FLOOD TABLE 
                                   GroupTable : use_grouptable : %d - group_id : %d" % 
                                   (use_grouptable, group_id))

                for (outport, vlan) in mperule.get_endpoint_ports_and_vlans():
                    self.logger.debug("L2MultipointEndpointLCRule: FLOOD TABLE 
                                       GroupTable : outport: %s vlan: %s group_id: %s" % 
                                       (outport, vlan, group_id))
                    actions = []
                    actions.append(SetField(VLAN_VID(vlan)))
                    actions.append(Forward(l2mp_bw_out_port))

                    # Make the TranslatedRuleContainer, and return it.
                    tgc = TranslatedLCRuleGroupContainer(of_cookie, flood_table,
                                                         groupType, group_id,
                                                         self._translate_LCAction(datapath,
                                                         actions,
                                                         flood_table))
                    results.append(tgc)
                    group_list[outport]=group_id
                    #group_id+=1
            else:
                use_grouptable = 0
                self.logger.debug("L2MultipointEndpointLCRule: FLOOD TABLE 
                                   GroupTable : use_grouptable : %d" % 
                                   (use_grouptable))


            for port in flooding_ports:
                self.logger.debug("L2MultipointEndpointLCRule: FLOOD TABLE 
                                   -1- : port:%s in flooding_ports:%s" % 
                                  (port, flooding_ports))
                # Flow.4
                matches = [IN_PORT(port), VLAN_VID(intermediate_vlan)]
                actions = []

                for outport in flooding_ports:
                    self.logger.debug("L2MultipointEndpointLCRule: FLOOD TABLE 
                                       -2- : outport:%s in flooding_ports:%s " % 
                                       (outport, flooding_ports))
                    if outport != port:
                        self.logger.debug("L2MultipointEndpointLCRule: FLOOD TABLE 
                                           -2- : outport:%s in flooding_ports:%s - 
                                           actions.append(Forward(outport)) " % 
                                           (outport, flooding_ports))
                        actions.append(Forward(outport))

                for (outport, vlan) in mperule.get_endpoint_ports_and_vlans():
                    self.logger.debug("L2MultipointEndpointLCRule: FLOOD TABLE 
                                       -3- : outport: %s vlan: %s" % 
                                       (outport, vlan))

                    if use_grouptable:
                        if outport != port:
                            self.logger.debug("L2MultipointEndpointLCRule: FLOOD TABLE 
                                               -3- : use_grouptable 1 with group_id %d - 
                                               actions.append(Group(group_id)) " % 
                                               (group_id))
                            actions.append(Group(group_id))
                    else: 
                        if outport != port:
                            self.logger.debug("L2MultipointEndpointLCRule: FLOOD TABLE 
                                               -3- : use_grouptable 0 setField: %s l2mp_bw_out_port: %s - 
                                               actions.append(Forward(l2mp_bw_out_port))" % 
                                               (vlan, l2mp_bw_out_port))
                            actions.append(SetField(VLAN_VID(vlan)))
                            actions.append(Forward(l2mp_bw_out_port))


                priority = PRIORITY_L2M_FLOOD_FORWARDING
                marule = MatchActionLCRule(switch_id, matches, actions)
                results += self._translate_MatchActionLCRule(datapath,
                                                             flood_table,
                                                             of_cookie,
                                                             marule,
                                                             priority)

                # Flow.5
                matches = [IN_PORT(port),
                           VLAN_VID(intermediate_vlan),
                           ETH_DST('ff:ff:ff:ff:ff:ff')]
                # Same actions as above, no need to rebuild
                priority = PRIORITY_L2M_BROADCAST_FORWARDING
                marule = MatchActionLCRule(switch_id, matches, actions)
                results += self._translate_MatchActionLCRule(datapath,
                                                             flood_table,
                                                             of_cookie,
                                                             marule,
                                                             priority)

            # Flow.8
            l2mp_bw_out_port = int(intermediate_vlan) + 10000

            matches = [IN_PORT(l2mp_bw_out_port), VLAN_VID(intermediate_vlan)]
            actions = []

            for port in flooding_ports:
                self.logger.debug("L2MultipointEndpointLCRule -4- : Flow.8: outport: %s " % (port))
                actions.append(Forward(port))

            priority = PRIORITY_L2M_FLOOD_FORWARDING
            marule = MatchActionLCRule(switch_id, matches, actions)
            results += self._translate_MatchActionLCRule(datapath,
                                                             flood_table,
                                                             of_cookie,
                                                             marule,
                                                             priority)
            # Flow.9
            matches = [IN_PORT(l2mp_bw_out_port),
                       VLAN_VID(intermediate_vlan),
                       ETH_DST('ff:ff:ff:ff:ff:ff')]
            # Same actions as above, no need to rebuild
            priority = PRIORITY_L2M_BROADCAST_FORWARDING
            marule = MatchActionLCRule(switch_id, matches, actions)
            results += self._translate_MatchActionLCRule(datapath,
                                                         flood_table,
                                                         of_cookie,
                                                         marule,
                                                         priority)



            # Endpoint ports
            for (port, vlan) in mperule.get_endpoint_ports_and_vlans():
                self.logger.debug("L2MultipointEndpointLCRule -5- : port: %s " % (port))

                l2mp_bw_in_port = vlan
                l2mp_bw_out_port = int(intermediate_vlan) + 10000

                # Flow.6
                matches = [IN_PORT(l2mp_bw_in_port), VLAN_VID(vlan)]
                actions = []
                actions.append(Forward(port))
                priority = PRIORITY_L2M_FLOOD_FORWARDING
                marule = MatchActionLCRule(switch_id, matches, actions)
                results += self._translate_MatchActionLCRule(datapath,
                                                             flood_table,
                                                             of_cookie,
                                                             marule,
                                                             priority)
                # Flow.7
                matches = [IN_PORT(l2mp_bw_in_port),
                           VLAN_VID(vlan),
                           ETH_DST('ff:ff:ff:ff:ff:ff')]
                # Same actions as above, no need to rebuild
                priority = PRIORITY_L2M_BROADCAST_FORWARDING
                marule = MatchActionLCRule(switch_id, matches, actions)
                results += self._translate_MatchActionLCRule(datapath,
                                                             flood_table,
                                                             of_cookie,
                                                             marule,
                                                             priority)

        return results

    def _translate_L2MultipointLearnedDestinationLCRule(self, datapath,
                                                        switch_table, of_cookie,
                                                        ldrule):
        ''' This translates L2MultipointLearnedDestinationLCRules. This will
            generate one rule.
            For non-endpoints, this will forward along the intermediate VLAN
            that's being used for the L2MultipointPolicy.
            For endpoints, this will translate VLAN to the destination VLAN,
            then forward.
        '''
        results = []
        switch_id = 0  # This is unimportant: it's never used in the translation
        matches = [VLAN_VID(ldrule.get_intermediate_vlan)(),
                   ETH_DST(ldrule.get_dst_address())]
        actions = None
        # Non-endpoints
        if ldrule.get_intermediate_vlan() == ldrule.get_out_vlan():
            actions = [Forward(ldrule.get_outport())]
        else:
            actions = [SetField(VLAN_VID(ldrule.get_out_vlan())),
                       Forward(ldrule.get_outport())]
        priority = PRIORITY_L2M_DESTINATION_FORWARDING
        marule = MatchActionLCRule(switch_id, matches, actions)
        results += self._translate_MatchActionLCRule(datapath,
                                                     switch_table,
                                                     of_cookie,
                                                     marule,
                                                     priority)
        return results

    def _translate_FloodTreeLCRule(self, datapath, switch_table,
                                   of_cookie, ftrule):
        ''' This translate FloodTreeLCRules. FloodTreeLCRules are for ports on a
            broadcast flood tree, so len(ports) number of rules need to be
            installed for each FloodTreeLCRule.
            Returns a list of TranslatedRUleContainers
        '''
        results = []
        switch_id = 0  # This is unimportant: it's never used in the translation
        priority = PRIORITY_FLOOD_FORWARDING

        ports = ftrule.get_ports()

        for port in ports:
            matches = [IN_PORT(port), ETH_DST('ff:ff:ff:ff:ff:ff')]
            actions = []

            # Forward to all other ports
            for dstport in ports:
                if dstport == port:
                    continue
                actions.append(Forward(dstport))
            marule = MatchActionLCRule(switch_id, matches, actions)
            results += self._translate_MatchActionLCRule(datapath,
                                                         switch_table,
                                                         of_cookie,
                                                         marule,
                                                         priority)
        return results

    def _translate_ManagementVLANLCRule(self, datapath, switch_table, of_cookie,
                                        mvrule):
        ''' This translates ManagementVLANLCRUles. This will generate one rule.
            For non-endpoints, this will forward along the intermediate VLAN
            that's being used for the L2MultipointPolicy.
            For endpoints, this will translate VLAN to the destination VLAN,
            then forward.
        '''
        results = []
        switch_id = 0  # This is unimportant: it's never used in the translation
        priority = PRIORITY_MGMT_VLAN

        mgmt_vlan = mvrule.get_mgmt_vlan()
        mgmt_ports = mvrule.get_mgmt_vlan_ports()
        untagged_mgmt_ports = mvrule.get_untagged_mgmt_vlan_ports()

        for vlan_port in (mgmt_ports + untagged_mgmt_ports):
            if vlan_port in mgmt_ports:
                matches = [VLAN_VID(mgmt_vlan), IN_PORT(vlan_port)]
                actions = []
            elif len(mgmt_ports) > 0:
                matches = [IN_PORT(vlan_port)]
                actions = [PushVLAN(),
                           SetField(VLAN_VID(mgmt_vlan))]
            else:
                # Special case where there is no MGMTVLAN, just Forwarding
                matches = [IN_PORT(vlan_port)]
                actions = []

            # Tagged ports - Forward with already setup VLAN
            for out_port in mgmt_ports:
                if out_port != vlan_port:
                    actions.append(Forward(out_port))
            # Untagged ports - clear the VLAN first, then forward
            if len(untagged_mgmt_ports) > 0 and len(mgmt_ports) > 0:
                actions.append(PopVLAN())
            for out_port in untagged_mgmt_ports:
                if out_port != vlan_port:
                    actions.append(Forward(out_port))

            marule = MatchActionLCRule(switch_id, matches, actions)
            results += self._translate_MatchActionLCRule(datapath,
                                                         switch_table,
                                                         of_cookie,
                                                         marule,
                                                         priority)

        return results

    def _translate_LCMatch(self, datapath, matches, table):
        args = {}
        for m in matches:
            # Add match to list
            args[m.get_name()] = m.get()
            # Add the prereqs to the list too
            for prereq in m.get_prereqs():
                if prereq.get_name() in list(args.keys()):
                    pass
                args[prereq.get_name()] = prereq.get()
                # FIXME: If there's a prereq in conflict (i.e., user specified
                # somethign in the same field, there's a problem) raise an
                # error.

        return datapath.ofproto_parser.OFPMatch(**args)

    def _translate_LCAction(self, datapath, actions, table):
        ''' This translates the user-level actions into OpenFlow-level Actions
            and instructions. Returns a list of instructions. '''

        parser = datapath.ofproto_parser
        ofproto = datapath.ofproto
        instructions = []
        aa_results = []

        for action in actions:
            # The first fiew action types are pretty easy: they all end up in
            # an OFPIT_APPLY_ACTIONS instruction.
            if isinstance(action, Forward):
                aa_results.append(parser.OFPActionOutput(action.get()))
                continue
            elif isinstance(action, SetField):
                args = {}
                f = action.get()
                args[f.get_name()] = f.get()
                aa_results.append(parser.OFPActionSetField(**args))
                continue
            elif isinstance(action, PushVLAN):
                aa_results.append(parser.OFPActionPushVlan())
                continue
            elif isinstance(action, PopVLAN):
                aa_results.append(parser.OFPActionPopVlan())
                continue
            # If we've gotten this far, that means the next action is *not* a
            # Forward, SetField, PushVLAN, or PopVLAN action, but will use a
            # different Instruction type, so wrap up the existing actions in an
            # APPLY_ACTIONS instruction first.
            # This is a bit dirty and confusing, sadly.
            if len(aa_results) > 0:
                instructions.append(parser.OFPInstructionActions(
                    ofproto.OFPIT_APPLY_ACTIONS, aa_results))
                aa_results = []

            # Drop is different, it should be the only instruction involved with
            # the match and should clear the actions that are installed.
            if isinstance(action, Drop):
                # This is an error!
                if len(actions) > 1:
                    # FIXME: raise an error
                    pass
                # To drop, need to clear actions associated with the match.
                instructions.append(parser.OFPInstructionActions(
                    ofproto.OFPIT_CLEAR_ACTIONS, []))

            # Continue and GotoTable are a bit different, as they both reference
            # other tables using the OFPIT_GOTO_TABLE instruction.
            elif isinstance(action, Continue):
                # table is the current table, we want to go to the next table
                instructions.append(parser.OFPInstructionGotoTable(table + 1))
            elif isinstance(action, GotoTable):
                instructions.append(parser.OFPInstructionGotoTable(action.get()))
            # WriteMetadata is a separate instruction, so must be handled
            # separetely
            elif isinstance(action, WriteMetadata):
                (value, mask) = action.get()
                instructions.append(parser.OFPInstructionWriteMetadata(value,
                                                                       mask))

        # Are there any values in aa_results? If so, put them in APPLY_ACTIONS
        # This is for the case where a bunch of simple rules (Forward, SetField,
        # PushVLAN, PopVLAN) are the only rules that exist, and they haven't yet
        # been put into an instruction.
        if len(aa_results) > 0:
            instructions.append(parser.OFPInstructionActions(
                ofproto.OFPIT_APPLY_ACTIONS, aa_results))
            # Return all the instructions added up
        return instructions

    def corsa_rest_cmd(self, rc):
        ''' Handles sending of REST commands to Corsa Switches. '''
        verify = False  # FIXME: Hardcoded
        if rc.get_function() == "get":
            response = requests.get(rc.get_url(),
                                    json=rc.get_json(),
                                    headers={'Authorization': rc.get_token()},
                                    verify=verify)
        elif rc.get_function() == "post":
            response = requests.post(rc.get_url(),
                                     json=rc.get_json(),
                                     headers={'Authorization': rc.get_token()},
                                     verify=verify)
        elif rc.get_function() == "patch":
            response = requests.patch(rc.get_url(),
                                      json=rc.get_json(),
                                      headers={'Authorization': rc.get_token()},
                                      verify=verify)
        else:
            raise ValueError("Function not valid: %s:%s" %
                             (rc.get_function(),
                              rc.get_json()))

        if response.status_code not in rc.get_valid_responses():
            raise Exception("REST command failed %s:%s\n    %s\n    %s" %
                            (rc.get_function(),
                             rc.get_json(),
                             response.status_code,
                             response.json()))

    def add_flow(self, datapath, rc):
        ''' Ease-of-use wrapper for adding flows. '''
        parser = datapath.ofproto_parser

        self.logger.debug("add_flow for %d:%d:%d:%s:%s" % (
            rc.get_cookie(),
            rc.get_table(),
            rc.get_priority(),
            rc.get_match(),
            rc.get_instructions()))

        if rc.get_buffer_id() != None:
            mod = parser.OFPFlowMod(datapath=datapath,
                                    cookie=rc.get_cookie(),
                                    table_id=rc.get_table(),
                                    buffer_id=rc.get_buffer_id(),
                                    priority=rc.get_priority(),
                                    match=rc.get_match(),
                                    instructions=rc.get_instructions(),
                                    idle_timeout=rc.get_idle_timeout(),
                                    hard_timeout=rc.get_hard_timeout())
        else:
            mod = parser.OFPFlowMod(datapath=datapath,
                                    cookie=rc.get_cookie(),
                                    table_id=rc.get_table(),
                                    # No buffer
                                    priority=rc.get_priority(),
                                    match=rc.get_match(),
                                    instructions=rc.get_instructions(),
                                    idle_timeout=rc.get_idle_timeout(),
                                    hard_timeout=rc.get_hard_timeout())

        datapath.send_msg(mod)

    def remove_flow(self, datapath, rc):
        # BASE ON: https://github.com/sdonovan1985/netassay-ryu/blob/672a31228ab08abe55c19e75afa52490e76cbf77/base/mcm.py#L283
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        command = ofproto.OFPFC_DELETE
        out_group = ofproto.OFPG_ANY
        out_port = ofproto.OFPP_ANY

        cookie = rc.get_cookie()
        table = rc.get_table()
        match = rc.get_match()

        self.logger.debug("RyuTranslateInterface:remove_flow(): %d,%d:%d:%s:%s:%s:%s" % (
                cookie,
                datapath.id,
                table,
                command,out_group,out_port,match))
        
        mod = parser.OFPFlowMod(datapath=datapath, cookie=cookie,
                                table_id=table, command=command,
                                out_group=out_group, out_port=out_port,
                                match=match)
        datapath.send_msg(mod)

    def remove_all_flows(self, datapath):
        # BASED ON: https://github.com/FlowForwarding/LINC-Switch/blob/master/scripts/ryu/remove_flows_v1_3.py
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        command = ofproto.OFPFC_DELETE
        out_group = ofproto.OFPG_ANY
        out_port = ofproto.OFPP_ANY
        table = ofproto.OFPTT_ALL

        mod = parser.OFPFlowMod(datapath=datapath, table_id=table,
                                command=command, out_group=out_group,
                                out_port=out_port)
        datapath.send_msg(mod)


    def add_group(self, datapath, rc):
        ''' Ease-of-use wrapper for adding group. '''
        ofp_parser = datapath.ofproto_parser
        ofp=datapath.ofproto
        self.logger.debug("add_group for %d:%d:%d:%d:%s" % (
            rc.get_cookie(),
            rc.get_table(),
            rc.get_groupType(),
            rc.get_group_id(),
            rc.get_instructions()))

        buckets = [ofp_parser.OFPBucket(rc.weight, rc.watch_port, rc.watch_group,
                                    rc.get_instructions())]

        req = ofp_parser.OFPGroupMod(datapath, ofp.OFPGC_ADD,
                                 rc.groupType, rc.group_id, buckets)
        datapath.send_msg(req)

    def remove_group(self, datapath, rc):
        ''' Ease-of-use wrapper for removing group. '''
        ofp_parser = datapath.ofproto_parser
        ofp=datapath.ofproto
        self.logger.debug("remove_group for %d:%d:%d:%d:%s" % (
            rc.get_cookie(),
            rc.get_table(),
            rc.get_groupType(),
            rc.get_group_id(),
            rc.get_instructions()))

        buckets = [ofp_parser.OFPBucket(rc.weight, rc.watch_port, rc.watch_group,
                                    rc.get_instructions())]

        req = ofp_parser.OFPGroupMod(datapath, ofp.OFPGC_DELETE,
                                 rc.groupType, rc.group_id, buckets)
        datapath.send_msg(req)


    def install_rule(self, datapath, sdx_rule):
        ''' The main loop calls this to handle adding a new rule.
            This function handles the translation from the SDX-provided rule to
            OpenFlow rules that the switch can actually work with. '''

        # FIXME: this is where translation from LC/SDX interface to the near OF
        # interface should happen

        # Verify input
        if not isinstance(sdx_rule, LCRule):
            raise TypeError("lcrule %s is not of type LCRule: %s" %
                            (sdx_rule, type(sdx_rule)))

        # Get a cookie based on the SDX Controller cookie
        of_cookie = self._get_new_OF_cookie(sdx_rule.get_cookie(), datapath.id)
        self.logger.debug("Cookie 0x%02x used in datapath %s for %s" % (of_cookie, datapath.id, sdx_rule))

        # Convert rule into instructions for Ryu. Switch through the different
        # types of supported LCRules for individual translation.
        switch_rules = None
        switch_table = None

        self.logger.debug("SDX Rule %s being installed in datapath %s" %
                          (sdx_rule, datapath.id))

        if isinstance(sdx_rule, MatchActionLCRule):
            if sdx_rule.get_ingress == True:
                # Ingress rules are applied right before being sent to the
                # destination network.
                switch_table = SDXINGRESSRULETABLE
            else:
                # Egress rules are applied immediately after leaving the source
                # network.
                switch_table = SDXEGRESSRULETABLE

            switch_rules = self._translate_MatchActionLCRule(datapath,
                                                             switch_table,
                                                             of_cookie,
                                                             sdx_rule)

        elif isinstance(sdx_rule, VlanTunnelLCRule):
            # VLAN rules happen before anything else.
            switch_table = L2TUNNELTABLE
            switch_rules = self._translate_VlanLCRule(datapath,
                                                      switch_table,
                                                      of_cookie,
                                                      sdx_rule)

        elif isinstance(sdx_rule, LearnedDestinationLCRule):
            # Learning switch forwarding rules happen as a fallback at the end
            switch_table = FORWARDINGTABLE
            switch_rules = self._translate_LearnedDestinationLCRule(datapath,
                                                                    switch_table,
                                                                    of_cookie,
                                                                    sdx_rule)
        elif isinstance(sdx_rule, EdgePortLCRule):
            # For bootstrapping for learning. Needs to register a CB as well.
            switch_table = LEARNINGTABLE
            switch_rules = self._translate_EdgePortLCRule(datapath,
                                                          switch_table,
                                                          of_cookie,
                                                          sdx_rule)
            self._register_packet_in_cb(of_cookie, self.unknown_source_cb)
        elif isinstance(sdx_rule, L2MultipointFloodLCRule):
            # Installs
            switch_table = FORWARDINGTABLE
            self.logger.debug("L2MultipointFlood: %d:%d:%s" % (switch_table,
                                                               of_cookie,
                                                               sdx_rule))

            switch_rules = self._translate_L2MultipointFloodLCRule(datapath,
                                                                   switch_table,
                                                                   of_cookie,
                                                                   sdx_rule)
        elif isinstance(sdx_rule, L2MultipointEndpointLCRule):
            # Uses
            endpoint_table = L2TUNNELTABLE
            translate_table = SDXEGRESSRULETABLE
            flood_table = FORWARDINGTABLE
            learning_table = LEARNINGTABLE
            switch_table = endpoint_table  # Used in some logs down below.
            self.logger.debug("L2MultipointEndpointLCRule: %d,%d:%d:%s" % (
                endpoint_table, flood_table,
                of_cookie,
                sdx_rule))
            switch_rules = self._translate_L2MultipointEndpointLCRule(datapath,
                                                                      endpoint_table,
                                                                      translate_table,
                                                                      flood_table,
                                                                      learning_table,
                                                                      of_cookie,
                                                                      sdx_rule)
            self._register_packet_in_cb(of_cookie,
                                        self.l2multipoint_unknown_source_cb)
            # This is to keep some logs down below happy. L2MultipointEndpoints
            # are weird, and the loggingisn't well suited.
            switch_table = endpoint_table

        elif isinstance(sdx_rule, L2MultipointLearnedDestinationLCRule):
            # Learning switch forwarding rules happen as a fallback at the end
            switch_table = FORWARDINGTABLE
            switch_rules = self._translate_L2MultipointLearnedDestinationLCRule(
                datapath,
                switch_table,
                of_cookie,
                sdx_rule)

        elif isinstance(sdx_rule, FloodTreeLCRule):
            switch_table = FORWARDINGTABLE
            switch_rules = self._translate_FloodTreeLCRule(datapath,
                                                           switch_table,
                                                           of_cookie,
                                                           sdx_rule)

        elif isinstance(sdx_rule, ManagementVLANLCRule):
            switch_table = L2TUNNELTABLE
            switch_rules = self._translate_ManagementVLANLCRule(datapath,
                                                                switch_table,
                                                                of_cookie,
                                                                sdx_rule)

        elif isinstance(sdx_rule, ManagementLCRecoverRule):
            self._backup_port_recover(datapath, of_cookie, sdx_rule)
            return

        elif isinstance(sdx_rule, ManagementSDXRecoverRule):
            self._backup_port_recover_from_sdx_msg(datapath, of_cookie, sdx_rule)
            return

        if switch_rules == None or switch_table == None:
            if not isinstance(sdx_rule, ManagementLCRecoverRule):
                self.logger.error(
                    "switch_rules or switch_table is None for msg: %s\n  switch_rules - %s\n  switch_table - %s" %
                    sdx_rule, switch_rules, switch_table)
            # FIXME: This shouldn't happen...
            pass

        # Save off instructions to local database.
        self.logger.debug("Inserting into switch table %d switch rules %s" %
                          (switch_table, switch_rules))
        self._install_rule_in_db(sdx_rule.get_cookie(), datapath.id, of_cookie,
                                 sdx_rule, switch_rules, switch_table)

        # Send instructions to the switch.
        self.logger.debug("Calling add_flow on the following:")
        for rule in switch_rules:
            if type(rule) == TranslatedLCRuleContainer:
                self.logger.debug("  %s" % rule)
                self.add_flow(datapath, rule)
            elif type(rule) == TranslatedLCRuleGroupContainer:
                self.logger.debug("  %s - _Group" % rule)
                self.add_group(datapath,rule)
            elif type(rule) == TranslatedCorsaRuleContainer:
                self.logger.debug("  %s - CORSA_REST_CMD" % rule)
                self.corsa_rest_cmd(rule)

    def remove_rule(self, datapath, sdx_cookie):
        ''' The main loop calls this to handle removing an existing rule.
            This function removes the existing OpenFlow rules associated with
            a given sdx_cookie. '''

        # Remove a rule.
        # Find the OF cookie based on the SDX Cookie
        of_cookie = self._find_OF_cookie(sdx_cookie,datapath.id)

        # Get the Rules based on the it.
        (switch_id, swcookie, sdxrule, swrules, table) = self._get_rule_in_db(sdx_cookie, datapath.id)

        if (switch_id == None and 
                swcookie == None and
                sdxrule == None and
                swrules == None and
                table == None):
            self.logger.error("No rule to remove for sdx_cookie %s" %
                              sdx_cookie)
            return

        self.logger.error("RyuTranslateInterface:remove_rule(): remove a rule for sdx_cookie %s:%s" %
                              (sdx_cookie, switch_id))
        try:
            # Remove flows
            for rule in swrules:
                if type(rule) == TranslatedLCRuleContainer:
                    self.logger.error("RyuTranslateInterface:remove_rule(): remove a TranslatedLCRuleContainer rule for sdx_cookie %s:%s" %
                              (sdx_cookie, switch_id))
                    self.remove_flow(datapath, rule)
                elif type(rule) == TranslatedLCRuleGroupContainer:
                    self.logger.error("RyuTranslateInterface:remove_rule(): remove a TranslatedLCRuleGroupContainer rule for sdx_cookie %s:%s" %
                              (sdx_cookie, switch_id))
                    self.remove_group(datapath, rule)
                elif type(rule) == TranslatedCorsaRuleContainer:
                    # Currently, don't have to do anything here.
                    self.logger.error("RyuTranslateInterface:remove_rule(): remove a TranslatedCorsaRuleContainer rule for sdx_cookie %s:%s" %
                              (sdx_cookie, switch_id))
                    pass
        except Exception as e:
            self.logger.error("Error in remove_rule %s:%s" % (sdx_cookie,
                                                              of_cookie))
            self.logger.error("  swcookie: %s" % swcookie)
            self.logger.error("  sdxrule: %s" % sdxrule)
            self.logger.error("  swrules: %s" % swrules)
            self.logger.error("  table: %s" % table)
            raise e

        # Remove rule infomation from database
        self._remove_rule_in_db(sdx_cookie, switch_id)

    def _install_rule_in_db(self, sdxcookie, switch_id, switchcookie,
                            sdxrule, switchrules, switchtable):
        ''' This installs a rule into the DB. This makes life a lot easier and
            provides a central point to handle DB interactions. '''
        # Columns for the "rules" table:
        #   sdxcookie - The SDX rule's provided cookie. This must be unique.
        #   switchcookie - The generated switch cookie. This will be unique.
        #   sdxrule - The LCRule that the SDX sent down to be installed
        #   switchrules - A list of Ryu-formatted rules that can be sent to the
        #      switch directly
        #   switchtable - The table that the rules are going to be installed.
        #      A single LCRule should only affect one table at a time.

        # FIXME: Checking to make sure it's not already there?
        self.rule_table.insert({'sdxcookie': sdxcookie,
                                'switchid': switch_id,
                                'switchcookie': switchcookie,
                                'sdxrule': pickle.dumps(sdxrule),
                                'switchrules': pickle.dumps(switchrules),
                                'switchtable': switchtable})

    def _remove_rule_in_db(self, sdx_cookie, switch_id):
        ''' This removes a rule from the DB. This makes life a lot easier and
            provides a central point to handle DB interactions. '''
        # FIXME: Make sure it does exist.
        self.rule_table.delete(sdxcookie=sdx_cookie, switchid=switch_id)

    def _get_rule_in_db(self, sdx_cookie, switch_id):
        ''' This returns a rule from the DB. This makes life a lot easier and
            provides a central point to handle DB interactions.
            Returns a tuple:
            (switchcookie, sdxrule, switchrules, switchtable) '''
        result = self.rule_table.find_one(sdxcookie=sdx_cookie, switchid=switch_id)
        if result == None:
            return (None, None, None, None)
        return (result['switchid'],
                result['switchcookie'],
                pickle.loads(result['sdxrule']),
                pickle.loads(result['switchrules']),
                result['switchtable'])

    def _get_new_OF_cookie(self, sdx_cookie, switch_id):
        ''' Creates a new cookie that can be used by OpenFlow switches.
            Populates a local database with information so that cookie can be
            looked up for rule removal. '''
        if self.rule_table.find_one(sdxcookie=sdx_cookie, switchid=switch_id) != None:
            # FIXME: This shouldn't happen...
            self.logger.error("Existing sdxcookie: %s, switchid: %s",sdx_cookie,switch_id)
            pass

        of_cookie = self.current_of_cookie
        self.current_of_cookie += 1

        return of_cookie

    def _find_OF_cookie(self, sdx_cookie, switch_id):
        ''' Looks up OpenFlow cookie in local database based on a provided
            sdx_cookie. '''
        result = self.rule_table.find_one(sdxcookie=sdx_cookie, switchid=switch_id)
        if result == None:
            return None
        return result['switchcookie']

    def _find_sdx_cookie(self, of_cookie, switch_id):
        ''' Loops up the SDX cookie in local database based on a provided
            of_cookie. '''
        result = self.rule_table.find_one(switchcookie=of_cookie,switchid=switch_id)
        if result == None:
            return None
        return result['sdxcookie']

    def _register_packet_in_cb(self, cookie_id, function):
        ''' Used for registeringcookies for packet_in callbacks. Function is
            called with the packet_in event. '''
        self.logger.debug("Registering cookie 0x%02x to function %s for packet_in handling" % (cookie_id, function))
        self.packet_in_cbs[cookie_id] = function

    def _deregister_packet_in_cb(self, cookie_id):
        ''' Used for deregistering cookies for packet_in callbacks. '''
        self.logger.debug("Deregistering cookie 0x%02x" % cookie_id)
        del self.packet_in_cbs[cookie_id]

    def unknown_source_cb(self, ev):
        ''' Handles new unknown source callbacks. This does two things upon
            receipt of a packet:
              - Sends info to  RyuControllerInterface to eventually send to SDX
                controller with sdx_cm.send_new_host_port_mapping()
              - Creates new rule to skip forwarding that source address to ctlr
        '''
        # Send info to SDX Controller
        switch_id = 0  # This is unimportant:
        # it's never used in the translation

        datapath = ev.msg.datapath
        switch_name = self._get_switch_internal_config(datapath.id)['name']
        port = ev.msg.match['in_port']
        pkt = packet.Packet(ev.msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]
        src_address = eth.src

        self.inter_cm_cxn.send_cmd(ICX_UNKNOWN_SOURCE,
                                   {"switch": switch_name,
                                    "port": port,
                                    "src": src_address})

        # New forwarding rule to skip over that again
        matches = [IN_PORT(port), ETH_SRC(src_address)]
        actions = [Continue()]
        table = LEARNINGTABLE
        of_cookie = ev.msg.cookie  # Keep the same cookie as the original rule
        priority = PRIORITY_GENERIC_LEARNED
        marule = MatchActionLCRule(switch_id, matches, actions)
        results = self._translate_MatchActionLCRule(datapath,
                                                    table,
                                                    of_cookie,
                                                    marule,
                                                    priority)
        for rule in results:
            self.add_flow(datapath, rule)

    def l2multipoint_unknown_source_cb(self, ev):
        ''' Handles new unknown source callbacks on L2MultipointPolicy edge
            ports. This is very similar to unknown_source_cb().
        '''
        # Send info to SDX Controller
        switch_id = 0  # This is unimportant:
        # it's never used in the translation

        datapath = ev.msg.datapath
        switch_name = self._get_switch_internal_config(datapath.id)['name']
        port = ev.msg.match['in_port']
        pkt = packet.Packet(ev.msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]
        src_address = eth.src
        of_cookie = ev.msg.cookie
        sdx_cookie = self._find_sdx_cookie(of_cookie, datapath.id)

        self.inter_cm_cxn.send_cmd(ICX_L2MULTIPOINT_UNKNOWN_SOURCE,
                                   {"cookie": sdx_cookie,
                                    "data": {"dstswitch": switch_name,
                                             "dstport": port,
                                             "dstaddress": src_address}})

        # New forwarding rule to skip over that address in the future.
        matches = [IN_PORT(port), ETH_SRC(src_address)]
        actions = [Continue()]
        table = LEARNINGTABLE
        priority = PRIORITY_L2MULTIPOINT_LEARNED
        marule = MatchActionLCRule(switch_id, matches, actions)
        results = self._translate_MatchActionLCRule(datapath,
                                                    table,
                                                    of_cookie,
                                                    marule,
                                                    priority)
        for rule in results:
            self.add_flow(datapath, rule)
