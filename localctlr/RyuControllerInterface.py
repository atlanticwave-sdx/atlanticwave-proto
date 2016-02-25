# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


from ControllerInterface import ControllerInterface
from ryu.ofproto import ofproto_v1_3
import Queue
from shared.Singleton import Singleton
from shared.OpenFlowRule import OpenFlowRule

class RyuControllerInterface(ControllerInterface):
    ''' This is a particular implementation of the ControllerInterface class
        that connects using Ryu. It inherits its interface from its parent 
        class. 
        It, by itself, does not interface with Ryu. This is because of how Ryu
        works. The ryu-manager must run each application, so in order to deal
        with that, we use some rather ugly passthroughs. First, we start the
        RyuTranslateInterface that takes commands, translates them to Ryu, and
        creates and sends the FlowMod messages. Second, there is a singleton
        RyuQueue (below) class that both RyuControllerInterface and 
        RyuTranslateInterface can talk to in order to pass messages across 
        without yet another network connection.
    '''


    def __init__(self, *args, **kwargs):
        super(RyuControllerInterface, self).__init__(*args, **kwargs)

        self.queue = RyuQueue()
        
        pass

    def send_command(self, rule):
        if not isinstance(rule, OpenFlowRule):
            raise ControllerInterfaceTypeError("rule is not of type OpenFlowRule: " + type(rule))

        # Add command to queue 
        self.queue.put(rule)

    def remove_rule(self, cookie):
        self.queue.put(cookie)


class RyuQueue(Queue.Queue):
    ''' This is a singleton queue that allows both RyuControllerInterface and
        RyuTranslateInterface to communicate. '''
    __metaclass__ = Singleton

    def __init__(self, maxsize=0):
        super(RyuQueue, self).__init__(maxsize)
