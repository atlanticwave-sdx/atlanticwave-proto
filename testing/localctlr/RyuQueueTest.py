# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


# Unit tests for LocalController class

import unittest
#import mock
from time import sleep
from localctlr.RyuTranslateInterface import RyuQueue


class SingletonTest(unittest.TestCase):
    def test_singleton(self):
        firstQueue = RyuQueue()
        secondQueue = RyuQueue()

        self.failUnless(firstQueue is secondQueue)

class QueueingTest(unittest.TestCase):
    def test_single_queue(self):
        queue = RyuQueue()

        queue.add_rule("Add")
        sleep(0.1)
        event_type, event = queue.get()

        self.failUnlessEqual(event_type, RyuQueue.ADD)
        self.failUnlessEqual(event, "Add")

class QueueingTest2(unittest.TestCase):
    def test_multiple_queue(self):
        queue = RyuQueue()

        queue.add_rule("Add")
        queue.remove_rule("Remove")
        event_type1, event1 = queue.get()
        event_type2, event2 = queue.get()

        self.failUnlessEqual(event_type1, RyuQueue.ADD)
        self.failUnlessEqual(event1, "Add")
        self.failUnlessEqual(event_type2, RyuQueue.REMOVE)
        self.failUnlessEqual(event2, "Remove")

class QueueingTest3(unittest.TestCase):
    def test_maxlen(self):
        queue = RyuQueue(3)

        queue.add_rule("1", False)
        queue.add_rule("2", False)
        queue.add_rule("3", False)
        
        return
        
        try:

            queue.add_rule("4", False)
        except Full:
            pass
        else:
            self.fail("Did not see error")



if __name__ == '__main__':
    unittest.main()
