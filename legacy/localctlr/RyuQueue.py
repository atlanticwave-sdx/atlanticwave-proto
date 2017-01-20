# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


# Definition of RyuQueue
from lib.Singleton import Singleton
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
        print "Adding to queue"
        self.queue.put((self.ADD, rule), block, timeout)
        print "Added  to queue"

    def remove_rule(self, rule, block=True, timeout=None):
        self.queue.put((self.REMOVE, rule), block, timeout)

    def get(self, block=True):
        ''' This returns the tuple (event_type, event).
            event_type is either ADD or REMOVE. '''
        print "Getting from queue"
        val = self.queue.get(block)
        print "Got     from queue"
        return val
        
    def _clear(self):
        while not self.queue.empty():
            self.queue.get(False)
        

class RyuCrossPollinate(object):
    ''' Singleton, mostly for testing - 
        see testing/localctlr/RyuTranslateInterfaceTest.py. '''
    __metaclass__ = Singleton

    def __init__(self):
        self.TranslateInterface = None
        self.ControllerInterface = None
