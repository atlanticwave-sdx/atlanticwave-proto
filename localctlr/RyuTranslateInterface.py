# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


from shared.OpenFlowRule import OpenFlowRule
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.ofprotop import ofproto_v1_3
import threading

class RyuTranslateInterface(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(RyuTranslateInterface, self).__init__(*args, **kwargs)

        self.queue = RyuQueue()

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
            
            if event_type == RyuQueue.ADD:
                # Add a new rule.
                pass

            elif event_type == RyuQueue.REMOVE:
                # Remove a rule.
                pass

    # Handles switch connect event
    @set_ev_cls(ofp_event.EventOFPSwitchEFeattures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        self.datapaths[ev.msg.datapath.id] = ev.msg.datapath
        
        


    # Boilerplate functions
    def add_flow(self, datapath, cookie, table, priority, match, actions, buffer_id=None):
        ''' Ease-of-use wrapper for adding flows. ''' 
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]

        # FIXME
        print "Adding flow : switch   " + str(datapath.id)
        print "            : priority " + str(priority)
        print "            : match    " + str(match)
        print "            : actions  " + str(actions)

        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, cookie=cookie,
                                    table_id=table, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst)
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
