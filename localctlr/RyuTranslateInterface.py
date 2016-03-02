# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


from shared.OpenFlowRule import OpenFlowRule
from shared.match import *
from shared.offield import *
from shared.action import *
from shared.instruction import *
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.ofprotop import ofproto_v1_3
import threading

class RyuTranslateInterface(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(RyuTranslateInterface, self).__init__(*args, **kwargs)

        self.queue = RyuQueue()
        self.datapaths = {}

        # Spawn main_loop thread
        self.loop_thread = threading.Thread(target=self.main_loop)
        self.loop_thread.daemon = True
        self.loop_thread.start()

        # Start up the connection to switch?


        # TODO: Reestablish connection? Do I have to do anything?
        
        pass

    def main_loop(self):
        ''' This is the main loop that reads and works with the RyuQueue data
            structure. It loops through, looking for new events. If there is one
            to be processed, process it. 
            Since RyuQueue is a queue structure, we can block on new events.
        '''

        while True:
            event_type, event = self.queue.get(block=True)
            if event.switch_id not in self.datapaths.keys():
                # FIXME - Need to update this for sending errors back
                continue
                
            datapath = self.datapath[event.switch_id]
            match = translate_match(datapath, event.match)
            
            if event_type == RyuQueue.ADD:
                # Convert instruction to Ryu
                instruction = translate_instruction(datapath, event.instruction)
                
                self.add_flow(self.datapath[event.switch_id],
                              event.cookie,
                              event.table,
                              event.priority,
                              match,
                              instruction,
                              event.buffer_id)

            elif event_type == RyuQueue.REMOVE:
                # Remove a rule.
                self.remove_flow(datapath,
                                 event.cookie,
                                 event.table,
                                 match)
            # FIXME - There may need to be more options here. This is just a start.

    # Handles switch connect event
    @set_ev_cls(ofp_event.EventOFPSwitchEFeattures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        self.datapaths[ev.msg.datapath.id] = ev.msg.datapath
        
        


    # Boilerplate functions
    def translate_match(self, datapath, match):
        ''' Translates shared.match.OpenFlowMatch to OFPMatch. '''

        args = {}
        for m in match.fields:
            args[m.get_name()] = m.get()

        return datapath.ofproto_parser.OFPMatch(args)

    def translate_action(self, datapath, action):
        ''' Translates shared.action.OpenFlowAction to OFPAction*. '''
        parser = datapath.ofproto_parser
        
        if isinstance(action, action_OUTPUT):
            if action.max_len.is_optional(action.fields):
                return parser.OFPActionOutput(action.port.get())
            return parser.OFPActionOutput(action.port.get(), action.max_len.get())

        elif isinstance(action, action_SET_FIELD):
            args = {}
            for f in action.fields.keys():
                args[f.get_name()] = f.get()
            return parser.OFPActionSetField(args)


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
            return parser.OFPInstructionActions(ofproto.OFPIT_CLEAR_ACTIONS)

        
                              
    def add_flow(self, datapath, cookie, table, priority, match, instruction, buffer_id=None):
        ''' Ease-of-use wrapper for adding flows. ''' 
        parser = datapath.ofproto_parser

        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, cookie=cookie,
                                    table_id=table, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=instruction)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=instruction)
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


class RyuQueue(Queue.Queue):
    ''' This is a singleton queue that allows both RyuControllerInterface and
        RyuTranslateInterface to communicate. '''
    __metaclass__ = Singleton

    self.REMOVE = "REMOVE"
    self.ADD = "ADD"

    def __init__(self, maxsize=0):
        super(RyuQueue, self).__init__(maxsize)

    # Use these for adding and removing, rather than put.
    def add_rule(self, rule):
        self.put((self.ADD, rule))

    def remove_rule(self, rule):
        self.put((self.REMOVE, rule))
