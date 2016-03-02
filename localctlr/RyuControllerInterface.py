# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


from ControllerInterface import ControllerInterface
from ryu.ofproto import ofproto_v1_3
from shared.Singleton import Singleton
from shared.OpenFlowRule import OpenFlowRule
from RyuTranslateInterface import RyuQueue
from ryu.cmd.manager import main

import Queue
from threading import Thread


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

        # Start up Ryu
        # FIXME: need a way to get the path to RyuTranslateInterface better than this
        self.ryu_thread = Thread(target=main,
                                 args=(),
                                 kwargs={'args':["~/atlanticwave-proto/localctlr/RyuTranslateInterface.py"]})
        self.ryu_thread.daemon = True
        self.ryu_thread.start()

        # FIXME: What else?
        pass

    def send_command(self, rule):
        if not isinstance(rule, OpenFlowRule):
            raise ControllerInterfaceTypeError("rule is not of type OpenFlowRule: " + type(rule))

        self.queue.add_rule(rule)

    def remove_rule(self, rule):
        if not isinstance(rule, OpenFlowRule):
            raise ControllerInterfaceTypeError("rule is not of type OpenFlowRule: " + type(rule))

        # FIXME: How to make this cleaner?
        self.queue.remove_rule(rule)


