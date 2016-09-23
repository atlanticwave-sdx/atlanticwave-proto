# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


from shared.OpenFlowRule import OpenFlowRule
from shared.Singleton import Singleton
from shared.match import *
from shared.offield import *
from shared.action import *
from shared.instruction import *
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
from time import sleep
from RyuControllerInterface import RyuControllerInterface
from InterRyuControllerConnectionManager import *

import logging
import threading

ADD = "ADD"
REMOVE = "REMOVE"

class RyuTranslateInterface(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(RyuTranslateInterface, self).__init__(*args, **kwargs)

        self._setup_logger()

        # Establish connection to RyuControllerInterface
        self.inter_cm = InterRyuControllerConnectionManager.instance()
        #FIXME: Hardcoded!
        self.inter_cm_cxn = self.inter_cm.open_outbound_connection("127.0.0.1", 55767)

        self.datapaths = {}

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
                
            datapath = self.datapaths[event.switch_id]
            match = self.translate_match(datapath, event.match)
            
            if event_type == ADD:
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

            elif event_type == REMOVE:
                # Remove a rule.
                self.remove_flow(datapath,
                                 event.cookie,
                                 event.table,
                                 match)
            # FIXME - There may need to be more options here. This is just a start.

    # Handles switch connect event
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        #print "Connection from: " + str(ev.msg.datapath.id) + " for " + str(self)
        self.datapaths[ev.msg.datapath.id] = ev.msg.datapath

    # From the Ryu mailing list: https://sourceforge.net/p/ryu/mailman/message/33584125/
    @set_ev_cls(ofp_event.EventOFPErrorMsg,
                [CONFIG_DISPATCHER, MAIN_DISPATCHER])
    def error_msg_handler(self, ev):
        msg = ev.msg
        self.logger.error('OFPErrorMsg received: type=0x%02x code=0x%02x '
                          'message=%s',
                          msg.type, msg.code, ryu.utils.hex_array(msg.data))


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

