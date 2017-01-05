# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


from shared.OpenFlowRule import OpenFlowRule
from shared.Singleton import Singleton
from shared.match import *
from shared.offield import *
from shared.action import *
from shared.instruction import *
from ryu import cfg
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.utils import hex_array
from time import sleep
from RyuControllerInterface import RyuControllerInterface
from InterRyuControllerConnectionManager import *

import logging
import threading

LOCALHOST = "127.0.0.1"


CONF = cfg.CONF


class RyuTranslateInterface(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(RyuTranslateInterface, self).__init__(*args, **kwargs)

        self._setup_logger()

        # Configuration information
        self.lcip = CONF['atlanticwave']['lcip']
        self.ryu_cxn_port = CONF['atlanticwave']['ryu_cxn_port']
        

        # Establish connection to RyuControllerInterface
        self.inter_cm = InterRyuControllerConnectionManager()
        #FIXME: Hardcoded!
        self.inter_cm_cxn = self.inter_cm.open_outbound_connection(self.lcip,
                                                                   self.ryu_cxn_port)

        self.datapaths = {}
        self.of_cookies = {}
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

    def main_loop(self):
        ''' This is the main loop that reads and works with the data coming from
            the Inter-Ryu Connection. It loops through, looking for new events. 
            If there is one to be processed, process it. 
        '''

        # First, wait till we have at least one datapath.
        while len(self.datapaths.keys()) == 0:
            print "Waiting " + str(self.datapaths)
            sleep(1)

        # Send message over to the Controller Interface to let it know that
        # we have at least one switch.
        self.inter_cm_cxn.send_cmd(ICX_DATAPATHS,
                                   str(self.datapaths))
        

        while True:

            # FIXME - This is static: only installing rules right now.
            event_type, event = self.inter_cm_cxn.recv_cmd()
            if event.switch_id not in self.datapaths.keys():
                # FIXME - Need to update this for sending errors back
                continue
                
            datapath = self.datapaths[rule.switch_id]
            
            if event_type == ICX_ADD:
                # Parse event
                #FIXME
                # Call handling function
                self.install_rule(datapath, rule)
            elif event_type == ICX_REMOVE:
                # Parse event
                #FIXME
                # Call handling function
                self.remove_rule(datapath, sdx_cookie)
                

            # FIXME - There may need to be more options here. This is just a start.

    # Handles switch connect event
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        print "Connection from: " + str(ev.msg.datapath.id) + " for " + str(self)
        self.datapaths[ev.msg.datapath.id] = ev.msg.datapath

    # From the Ryu mailing list: https://sourceforge.net/p/ryu/mailman/message/33584125/
    @set_ev_cls(ofp_event.EventOFPErrorMsg,
                [CONFIG_DISPATCHER, MAIN_DISPATCHER])
    def error_msg_handler(self, ev):
        msg = ev.msg
        self.logger.error('OFPErrorMsg received: type=0x%02x code=0x%02x '
                          'message=%s',
                          msg.type, msg.code, hex_array(msg.data))


    # Boilerplate functions
    def translate_match(self, datapath, match):
        ''' Translates shared.match.OpenFlowMatch to OFPMatch. '''

        args = {}
        for m in match.fields:
            args[m.get_name()] = m.get()

        return datapath.ofproto_parser.OFPMatch(**args)

    def translate_action(self, datapath, action):
        ''' Translates shared.action.OpenFlowAction to OFPAction*. '''
        parser = datapath.ofproto_parser
        
        if isinstance(action, action_OUTPUT):
            if action.max_len.is_optional(action.fields):
                return parser.OFPActionOutput(action.port.get())
            return parser.OFPActionOutput(action.port.get(), action.max_len.get())

        elif isinstance(action, action_SET_FIELD):
            args = {}
            for f in action.fields:#.keys():
                args[f.get_name()] = f.get()
            return parser.OFPActionSetField(**args)


    def translate_instruction(self, datapath, instruction):
        ''' Translates shared.instruction.OpenFlowInstruction to 
            OFPInstruction*. '''
        parser = datapath.ofproto_parser
        ofproto = datapath.ofproto

        if isinstance(instruction, instruction_GOTO_TABLE):
            return parser.OFPInstructionGotoTable(instruction.table_id.get())
            
        elif isinstance(instruction, instruction_WRITE_METADATA):
            return parser.OFPInstructionWriteMetadata(instruction.metadata.get(),
                                                      instruction.metadata_mask.get())

        elif isinstance(instruction, instruction_WRITE_ACTIONS):
            actions = []
            for action in instruction.actions:
                actions.append(self.translate_action(datapath, action))
                 
            return parser.OFPInstructionActions(ofproto.OFPIT_WRITE_ACTIONS,
                                                actions)


        elif isinstance(instruction, instruction_APPLY_ACTIONS):
            actions = []
            for action in instruction.actions:
                actions.append(self.translate_action(datapath, action))
                
            return parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                                actions)

        elif isinstance(instruction, instruction_CLEAR_ACTIONS):
            # FIXME: The empty list is due to a bug in ofproto_v1_3_parser.py:2758
            return parser.OFPInstructionActions(ofproto.OFPIT_CLEAR_ACTIONS,[])




    def _translate_to_OF(self, lcrule):
        ''' This translates from LCRules to OFRules. All the following functions
            are helpers for this. '''

        # Verify input
        if not isinstance(lcrule, LCRule):
            raise TypeError("lcrule %s is not of type LCRule: %s" %
                            (lcrule, type(lcrule)))

        # Switch based on actual type
        results = None
        if type(lcrule) == MatchActionLCRule:
            results = self._translate_MatchActionLCRule(lcrule)

        elif type(lcrule) == VlanTunnelLCRule:
            results = self._translate_VlanTunnelLCRule(lcrule)

        # Return translated rule.
        return results

    def _translate_MatchActionLCRule(self, marule):
        matchlist = []
        actionlist = []

        # Translate all the matches
        xlated_match = self._translate_LCMatch(marule.get_matches(),
                                               marule.get_ingress())

        # Translate all the actions
        xlated_actions = self._translate_LCAction(marule.get_actions(),
                                                  marule.get_ingress())

        # Build the instruction
        instruction = instruction_APPLY_ACTIONS(xlated_actions)
        table = None #FIXME
        priority = None #FIXME
        cookie = None #FIXME
        switch_id = marule.get_switch_id()

        # Build the OpenFlowRule
        rule = OpenFlowRule(xlated_match, instruction, FIXME)
        

                
        pass
        
    def _translate_VlanLCRule(self, vlanrule):
        # Create outbound rule

        # If bidirectional, create inbound rule

        #FIXME: Bandwidth management stuff
        

        pass

    def _translate_LCMatch(self, lcmatches, ingress):
        # for each match:

        # Augment the matches with all the prereqs
        # If there's a prereq in conflict (i.e., user specified somethign in the 
        # same field, there's a problem, raise an error).

        
        pass


    def _translate_LCAction(self, lcactions, ingress):
        # for each action:
        
        # translate to appropriate action type.
        pass

    def _translate_LCField(self, type, value):
        # Figure out the correct class, and fill it in
        pass        

        
                              
    def add_flow(self, datapath, cookie, table, priority, match, instruction, 
                 buffer_id=None, idle_timeout=0, hard_timeout=0):
        ''' Ease-of-use wrapper for adding flows. ''' 
        parser = datapath.ofproto_parser

        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, cookie=cookie,
                                    table_id=table, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=instruction,
                                    idle_timeout=idle_timeout, 
                                    hard_timeout=hard_timeout)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, cookie=cookie,
                                    table_id=table, priority=priority,
                                    match=match, instructions=instruction,
                                    idle_timeout=idle_timeout, 
                                    hard_timeout=hard_timeout)

        datapath.send_msg(mod)

    def remove_flow(self, datapath, cookie, table, match):
        #BASE ON: https://github.com/sdonovan1985/netassay-ryu/blob/672a31228ab08abe55c19e75afa52490e76cbf77/base/mcm.py#L283
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        command = ofproto.OFPFC_DELETE
        out_group = ofproto.OFPG_ANY
        out_port = ofproto.OFPP_ANY

        mod = parser.OFPFlowMod(datapath=datapath, cookie=cookie, 
                                table_id=table, command=command,
                                out_group=out_group, out_port=out_port,
                                match=match)
        datapath.send_msg(mod)


    def _get_new_OF_cookie(self, sdx_cookie):
        ''' Creates a new cookie that can be used by OpenFlow switches. 
            Populates a local database with information so that cookie can be
            looked up for rule removal. '''
        if sdx_cookie in self.of_cookies.keys():
            # FIXME: This shouldn't happen...
            pass
        
        of_cookie = self.current_of_cookie
        self.current_of_cookie += 1
        
        self.of_cookies[sdx_cookie] = of_cookie
        return of_cookie

    def _find_OF_cookie(self, sdx_cookie):
        ''' Looks up OpenFlow cookie in local database based on a provided
            sdx_cookie. '''
        if sdx_cookie not in self.of_cookies.keys():
            return None
        return self.of_cookies[sdx_cookie]

    def _rm_OF_cookie(self, sdx_cookie):
        ''' Removes OpenFlow cookie based on the sdx_cookie. '''
        if sdx_cookie not in self.of_cookies.keys():
            # FIXME: This shouldn't happen...
        del self.of_cookies[sdx_cookie]

    def install_rule(self, datapath, rule):
        ''' The main loop calls this to handle adding a new rule.
            This function handles the translation from the SDX-provided rule to
            OpenFlow rules that the switch can actually work with. '''

        # FIXME: this is where translation from LC/SDX interface to the near OF
        #interface should happen
        # FIXME: OpenFlow Cookie generation - The rule's 

        # Get a cookie based on the SDX Controller cookie
        of_cookie = self._get_new_OF_cookie(rule.cookie)

        # Convert rule into instructions for Ryu

        # Save off instructions to local database.

        # Send instructions to the switch.




                
                
        # Convert instruction to Ryu
        instructions = [self.translate_instruction(datapath, 
                                                   event.instruction)]
                
        self.add_flow(datapath,
                      event.cookie,
                      event.table,
                      event.priority,
                      match,
                      instructions)
                      # event.buffer_id)

        pass

    def remove_rule(self, datapath, sdx_cookie):
        ''' The main loop calls this to handle removing an existing rule.
            This function removes the existing OpenFlow rules associated with
            a given sdx_cookie. '''

        # Remove a rule.
        # Find the OF cookie based on the SDX Cookie
        of_cookie = self._find_OF_cookie(rule.sdx_cookie)

        # Get the Rules based on the 
        
        # Remove flows

        # Remove OF cookie
        self._rm_OF_cookie(rule.sdx_cookie)

        # Remove rule infomation from database


                

                
        self.remove_flow(datapath,
                         event.cookie,
                         event.table,
                         match)
        pass
                
