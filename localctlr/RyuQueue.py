# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


# Definition of RyuQueue
from shared.Singleton import Singleton
import Queue

class RyuQueue(object):
    ''' This is a singleton queue that allows both RyuControllerInterface and
        RyuTranslateInterface to communicate. '''
    __metaclass__ = Singleton

    REMOVE = "REMOVE"
    ADD = "ADD"

    def __init__(self, maxsize=0):
        self.queue = Queue.Queue(maxsize)

    # Use these for adding and removing, rather than put.
    def add_rule(self, rule, block=True, timeout=None):
        self.queue.put((self.ADD, rule), block, timeout)

    def remove_rule(self, rule, block=True, timeout=None):
        self.queue.put((self.REMOVE, rule), block, timeout)

    def get(self, block=False):
        ''' This returns the tuple (event_type, event).
            event_type is either ADD or REMOVE. '''
        return self.queue.get(block)
        

class RyuCrossPollinate(object):
    ''' Singleton, mostly for testing - 
        see testing/localctlr/RyuTranslateInterfaceTest.py. '''
    __metaclass__ = Singleton

    def __init__(self):
        self.TranslateInterface = None
        self.ControllerInterface = None
