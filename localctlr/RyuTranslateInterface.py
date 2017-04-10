# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


import logging
import threading
import dataset
import cPickle as pickle
import requests
import json

from shared.MatchActionLCRule import *
from shared.VlanTunnelLCRule import *
from shared.LCAction import *
from shared.LCFields import *
from shared.LCRule import *
from ryu import cfg
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.utils import hex_array
from time import sleep
from RyuControllerInterface import RyuControllerInterface
from InterRyuControllerConnectionManager import *

LOCALHOST = "127.0.0.1"


CONF = cfg.CONF

class TranslatedRuleContainer(object):
    ''' Parent class for holding both LC and Corsa rules '''
    pass

class TranslatedLCRuleContainer(TranslatedRuleContainer):
    ''' Used by RyuTranslateInterface to track translations of LCRules. Contains
        Ryu-friendly objects. Not for use outside RyuTranslateInterface. '''
    def __init__(self, cookie, table, priority, match, instruction,
                 buffer_id=None, idle_timeout=0, hard_timeout=0):
        self.cookie = cookie
        self.table = table
        self.priority = priority
        self.match = match
        self.instruction = instruction
        self.buffer_id = buffer_id
        self.idle_timeout = idle_timeout
        self.hard_timeout = hard_timeout

    def __str__(self):
        return "%s:%s:%s\n%s\n%s\n%s:%s:%s" % (self.cookie, self.table,
                                               self.priority, self.match,
                                               self.instruction, 
                                               self.buffer_id,
                                               self.idle_timeout,
                                               self.hard_timeout)

    def get_cookie(self):
        return self.cookie

    def get_table(self):
        return self.table
    
    def get_priority(self):
        return self.priority
    
    def get_match(self):
        return self.match
    
    def get_instruction(self):
        return self.instruction
    
    def get_buffer_id(self):
        return self.buffer_id
    
    def get_idle_timeout(self):
        return self.idle_timeout
    
    def get_hard_timeout(self):
        return self.hard_timeout

    
class TranslatedCorsaRuleContainer(TranslatedRuleContainer):
    ''' Used by RyuTranslateInterface to track translations of Corsa Rules.
        Contains what is needed to make a REST request. '''
    def __init__(self, url, json, token, list_of_valid_responses):
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
    


class RyuTranslateInterface(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(RyuTranslateInterface, self).__init__(*args, **kwargs)

        self._setup_logger()

        # Configuration file + parsing
        self.name = CONF['atlanticwave']['lcname']
        self.conf_file = CONF['atlanticwave']['conffile']
        self._import_configuration()


        # Start up Database connection
        # DB is in-memory, as this probalby doesn't need to be tracked through
        # reboots. details on the setup:
        # https://dataset.readthedocs.io/en/latest/api.html
        # https://github.com/g2p/bedup/issues/38#issuecomment-43703630
        # https://www.sqlite.org/inmemorydb.html
        # FIXME: May need to reconsider this in the future, especially for
        # optimization (reducing translations is a good step in optimizing).
        dblocation = "sqlite:///:memory:"
        self.db = dataset.connect(dblocation,
                                  engine_kwargs={'connect_args':
                                                 {'check_same_thread':False}})
        # Database Tables
        self.rule_table = self.db['rules']

        #FIXME: Do I want to mirror the RuleManager's config_table?
        

        # Establish connection to RyuControllerInterface
        self.inter_cm = InterRyuControllerConnectionManager()
        self.inter_cm_cxn = self.inter_cm.open_outbound_connection(self.lcip,
                                                                   self.ryu_cxn_port)

        self.datapaths = {}
        self.current_of_cookie = 0

        # Spawn main_loop thread
        self.loop_thread = threading.Thread(target=self.main_loop)
        self.loop_thread.daemon = True
        self.loop_thread.start()

        # Start up the connection to switch?


        # TODO: Reestablish connection? Do I have to do anything?
        
        pass


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
        self.logger = logging.getLogger('localcontroller.ryutranslateinterface')
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(console)
        self.logger.addHandler(logfile)

    def _import_configuration(self):
        ''' Imports configuration parameters from the passed in configuration
            file. '''
        with open(self.conf_file) as data_file:
            data = json.load(data_file)

        # Look at information under the self.name entry, then look at only
        # data relevant to us.
        lcdata = data['localcontrollers'][self.name]
        self.lcip = lcdata['lcip']
        
        ofdata = lcdata['internalconfig']
        self.ryu_cxn_port = ofdata['ryucxninternalport']
        self.corsa_url = ofdata['corsaurl']
        self.corsa_token = ofdata['corsatoken']
        self.corsa_bridge = ofdata['corsabridge']
        self.corsa_bw_in = int(ofdata['corsabwin'])
        self.corsa_bw_out = int(ofdata['corsabwout'])
        self.corsa_rate_limit_bridge = ofdata['corsaratelimiterbridge']
        self.corsa_rate_limit_ports = ofdata['corsaratelimiterports']
        

    def main_loop(self):
        ''' This is the main loop that reads and works with the data coming from
            the Inter-Ryu Connection. It loops through, looking for new events. 
            If there is one to be processed, process it. 
        '''

        # First, wait till we have at least one datapath.
        self.logger.info("Looking for datapath")
        while len(self.datapaths.keys()) == 0:
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
            if switch_id not in self.datapaths.keys():
                # FIXME - Need to update this for sending errors back
                continue
                
            datapath = self.datapaths[switch_id]
            
            if event_type == ICX_ADD:
                self.install_rule(datapath, event)
            elif event_type == ICX_REMOVE:
                self.remove_rule(datapath, event)
                

            # FIXME - There may need to be more options here. This is just a start.

    # Handles switch connect event
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        self.logger.warning("Connection from: " + str(ev.msg.datapath.id) + " for " + str(self))
        self.datapaths[ev.msg.datapath.id] = ev.msg.datapath

    # From the Ryu mailing list: https://sourceforge.net/p/ryu/mailman/message/33584125/
    @set_ev_cls(ofp_event.EventOFPErrorMsg,
                [CONFIG_DISPATCHER, MAIN_DISPATCHER])
    def error_msg_handler(self, ev):
        msg = ev.msg
        self.logger.error('OFPErrorMsg received: type=0x%02x code=0x%02x '
                          'message=%s',
                          msg.type, msg.code, hex_array(msg.data))


    def _translate_MatchActionLCRule(self, datapath, table, of_cookie, marule):
        ''' This translates MatchActionLCRules. There is only one rule generated
            by any given MatchActionLCRule. 
            Returns a list of TranslatedLCRuleContainers
        ''' 
        results = []

        priority = 100 #FIXME
        # Translate all the pieces
        match = self._translate_LCMatch(datapath,
                                        marule.get_matches())
        instruction = self._translate_LCAction(datapath,
                                                marule.get_actions())

        # Make the TranslatedRuleContainer, and return it.
        trc = TranslatedLCRuleContainer(of_cookie, table, priority,
                                      match, instruction)
        results.append(trc)

        return results

    
    def _translate_VlanLCRule(self, datapath, table, of_cookie, vlanrule):
        ''' This translates VlanLCRules. This can generate one or two rules, 
            depending on if this is a bidirectional tunnel (the norm) or not.
            Returns a list of TranslatedLCRuleContainers
        '''
        results = []

        # Create Outbound Rule
        # There are two options here: Corsa or Non-Corsa. Non-Corsa is for
        # regular OpenFlow switches (such as OVS) and is more straight forward.

        if self.corsa_url == "":
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
                       Forward(self.corsa_bw_in)]
            marule = MatchActionLCRule(switch_id, matches, actions)
            results += self._translate_MatchActionLCRule(datapath,
                                                         table,
                                                         of_cookie,
                                                         marule)

            matches = [IN_PORT(self.corsa_bw_out),
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
                matches = [IN_PORT(self.corsa_bw_in),
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
                           Forward(self.corsa_bw_out)]
                marule = MatchActionLCRule(switch_id, matches, actions)
                results += self._translate_MatchActionLCRule(datapath,
                                                             table,
                                                             of_cookie,
                                                             marule)


            # Bandwidth REST rules rely on the REST API. If it changes, then
            # this may need to be modified.
            bridge = self.corsa_rate_limit_bridge
            vlan = str(vlanrule.get_vlan_out())
            bandwidth = vlanrule.get_bandwidth()

            #Find out the request_url
            tunnel_url = (self.corsa_url + "api/v1/bridges/" +
                          bridge + "/tunnels?list=true")
            print "Requesting tunnels from %s" % tunnel_url
            rest_return = requests.get(tunnel_url,
                                       headers={'Authorization':
                                                self.corsa_token},
                                       verify=False) #FIXME: HARDCODED
            for entry in rest_return.json()['list']:
                if (entry['vlan-id'] == vlan and
                    int(entry['port']) in self.corsa_rate_limit_ports):

                    request_url = entry['links']['self']['href']
                    json = [{'op':'replace',
                             'path':'/meter/cir',
                             'value':bandwidth}],
                    valid_responses = [204]

                    results += TranslatedCorsaRuleContainer("patch",
                                                            request_url,
                                                            json,
                                                            self.corsa_token,
                                                            valid_responses)
        
        # Return results to be used.
        return results

    def _translate_LCMatch(self, datapath, matches):
        args = {}
        for m in matches:
            # Add match to list
            args[m.get_name()] = m.get()
            # Add the prereqs to the list too
            for prereq in m.get_prereqs():
                if prereq.get_name() in args.keys():
                    pass
                args[prereq.get_name()] = prereq.get()
                #FIXME: If there's a prereq in conflict (i.e., user specified
                # somethign in the same field, there's a problem) raise an
                # error.
                
        return datapath.ofproto_parser.OFPMatch(**args)

    def _translate_LCAction(self, datapath, actions):
        ''' This translates the user-level actions into OpenFlow-level Actions
            and instructions. Returns an instruction. '''

        parser = datapath.ofproto_parser
        ofproto = datapath.ofproto
        results = []
        
        for action in actions:
            if isinstance(action, Forward):
                results.append(parser.OFPActionOutput(action.get()))
            elif isinstance(action, SetField):
                args = {}
                f = action.get()
                args[f.get_name()] = f.get()
                results.append(parser.OFPActionSetField(**args))
            elif isinstance(action, Continue):
                #FIXME: How to "continue"?
                pass
            elif isinstance(action, Drop):
                # This is an error!
                if len(actions) > 1:
                    #FIXME: raise an error
                    pass
                # To drop, need to clear actions associated with the match.
                return parser.OFPInstructionActions(
                               ofproto.OFPIT_CLEAR_ACTIONS, [])
            elif isinstance(action, SetBandwidth):
                #FIXME: This is hardware specific
                pass

        # For most everything, return an action APPLY_ACTIONS
        return parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                            results)


    def corsa_rest_cmd(self, rc):
        ''' Handles sending of REST commands to Corsa Switches. '''
        verify = False #FIXME: Hardcoded
        if rc.get_function() == "get":
            response = requests.get(rc.get_url(),
                                    json=rc.get_json(),
                                    headers={'Authorization':rc.get_token},
                                    verify=verify)
        elif rc.get_function() == "post":
            response = requests.post(rc.get_url(),
                                      json=rc.get_json(),
                                      headers={'Authorization':rc.get_token},
                                      verify=verify)
        elif rc.get_function() == "get":
            response = requests.patch(rc.get_url(),
                                      json=rc.get_json(),
                                      headers={'Authorization':rc.get_token},
                                      verify=verify)
        else:
            raise ValueError("Function not valid: %s:%s" %
                        (rc.get_function(),
                         rc.get_json()))

        if response.status_code not in rc.get_valid_responses():
            raise Error("REST command failed %s:%s\n    %s\n    %s" %
                        (rc.get_function(),
                         rc.get_json(),
                         response.status_code,
                         response.json()))

    def add_flow(self, datapath, rc):
        ''' Ease-of-use wrapper for adding flows. ''' 
        parser = datapath.ofproto_parser

        if rc.get_buffer_id() != None:
            mod = parser.OFPFlowMod(datapath=datapath,
                                    cookie=rc.get_cookie(),
                                    table_id=rc.get_table(),
                                    buffer_id=rc.get_buffer_id(),
                                    priority=rc.get_priority(),
                                    match=rc.get_match(),
                                    instructions=[rc.get_instruction()],
                                    idle_timeout=rc.get_idle_timeout(), 
                                    hard_timeout=rc.get_hard_timeout())
        else:
            mod = parser.OFPFlowMod(datapath=datapath,
                                    cookie=rc.get_cookie(),
                                    table_id=rc.get_table(),
                                    # No buffer
                                    priority=rc.get_priority(),
                                    match=rc.get_match(),
                                    instructions=[rc.get_instruction()],
                                    idle_timeout=rc.get_idle_timeout(), 
                                    hard_timeout=rc.get_hard_timeout())

        datapath.send_msg(mod)

    def remove_flow(self, datapath, rc):
        #BASE ON: https://github.com/sdonovan1985/netassay-ryu/blob/672a31228ab08abe55c19e75afa52490e76cbf77/base/mcm.py#L283
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        command = ofproto.OFPFC_DELETE
        out_group = ofproto.OFPG_ANY
        out_port = ofproto.OFPP_ANY
        
        cookie = rc.get_cookie()
        table = rc.get_table()
        match = rc.get_match()

        mod = parser.OFPFlowMod(datapath=datapath, cookie=cookie, 
                                table_id=table, command=command,
                                out_group=out_group, out_port=out_port,
                                match=match)
        datapath.send_msg(mod)



        

    def install_rule(self, datapath, sdx_rule):
        ''' The main loop calls this to handle adding a new rule.
            This function handles the translation from the SDX-provided rule to
            OpenFlow rules that the switch can actually work with. '''

        # FIXME: this is where translation from LC/SDX interface to the near OF
        #interface should happen
        
        # Verify input
        if not isinstance(sdx_rule, LCRule):
            raise TypeError("lcrule %s is not of type LCRule: %s" %
                            (sdx_rule, type(sdxrule)))


        # Get a cookie based on the SDX Controller cookie
        of_cookie = self._get_new_OF_cookie(sdx_rule.get_cookie())

        # Convert rule into instructions for Ryu. Switch through the different
        # types of supported LCRules for individual translation.
        switch_rules = None
        switch_table = None
        if isinstance(sdx_rule, MatchActionLCRule):
            if sdx_rule.get_ingress == True:
                # Ingress rules are applied right before being sent to the
                # destination network.
                switch_table = 2 #FIXME: magic number
            else:
                # Egress rules are applied immediately after leaving the source
                # network.
                switch_table = 1 #FIXME: magic number

            switch_rules = self._translate_MatchActionLCRule(datapath,
                                                             switch_table,
                                                             of_cookie,
                                                             sdx_rule)
            
        elif isinstance(sdx_rule, VlanTunnelLCRule):
            # VLAN rules happen before anything else. 
            switch_table = 0 #FIXME: magic number
            switch_rules = self._translate_VlanLCRule(datapath,
                                                      switch_table,
                                                      of_cookie,
                                                      sdx_rule)

        if switch_rules == None or switch_table == None:
            #FIXME: This shouldn't happen...
            pass
        
        # Save off instructions to local database.
        self._install_rule_in_db(sdx_rule.get_cookie(), of_cookie,
                                 sdx_rule, switch_rules, switch_table)

        # Send instructions to the switch.
        for rule in switch_rules:
            if type(rule) == TranslatedLCRuleContainer:
                self.add_flow(datapath, rule)
            elif type(rule) == TranslatedCorsaRuleContainer:
                self.corsa_rest_cmd(rule)


    def remove_rule(self, datapath, sdx_cookie):
        ''' The main loop calls this to handle removing an existing rule.
            This function removes the existing OpenFlow rules associated with
            a given sdx_cookie. '''

        # Remove a rule.
        # Find the OF cookie based on the SDX Cookie
        of_cookie = self._find_OF_cookie(sdx_cookie)

        # Get the Rules based on the it.
        (swcookie, sdxrule, swrules, table) = self._get_rule_in_db(sdx_cookie)
                
        # Remove flows
        for rule in swrules:
            if type(rule) == TranslatedLCRuleContainer:
                self.remove_flow(datapath, rule)
            elif type(rule) == TranslatedCorsaRuleContainer:
                # Currently, don't have to do anything here.
                pass

        # Remove rule infomation from database
        self._remove_rule_in_db(sdx_cookie)
                

    def _install_rule_in_db(self, sdxcookie, switchcookie,
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

        #FIXME: Checking to make sure it's not already there?
        self.rule_table.insert({'sdxcookie':sdxcookie,
                                'switchcookie':switchcookie,
                                'sdxrule':pickle.dumps(sdxrule),
                                'switchrules':pickle.dumps(switchrules),
                                'switchtable':switchtable})

    def _remove_rule_in_db(self, sdx_cookie):
        ''' This removes a rule from the DB. This makes life a lot easier and
            provides a central point to handle DB interactions. '''
        #FIXME: Make sure it does exist.
        self.rule_table.delete(sdxcookie=sdx_cookie)

    def _get_rule_in_db(self, sdx_cookie):
        ''' This returns a rule from the DB. This makes life a lot easier and 
            provides a central point to handle DB interactions. 
            Returns a tuple:
            (switchcookie, sdxrule, switchrules, switchtable) '''
        result = self.rule_table.find_one(sdxcookie=sdx_cookie)
        if result == None:
            return (None, None, None, None)
        return (result['switchcookie'],
                pickle.loads(str(result['sdxrule'])),
                pickle.loads(str(result['switchrules'])),
                result['switchtable'])
        
        

    def _get_new_OF_cookie(self, sdx_cookie):
        ''' Creates a new cookie that can be used by OpenFlow switches. 
            Populates a local database with information so that cookie can be
            looked up for rule removal. '''
        if self.rule_table.find_one(sdxcookie=sdx_cookie) != None:
            # FIXME: This shouldn't happen...
            pass
        
        of_cookie = self.current_of_cookie
        self.current_of_cookie += 1
        
        return of_cookie

    def _find_OF_cookie(self, sdx_cookie):
        ''' Looks up OpenFlow cookie in local database based on a provided
            sdx_cookie. '''
        result = self.rule_table.find_one(sdxcookie=sdx_cookie)
        if result == None:
            return None
        return result['switchcookie']
