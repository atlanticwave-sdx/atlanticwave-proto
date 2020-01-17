# Copyright 2019 - Sean Donovan
# AtlanticWave/SDX Project


# Unit tests for shared.LCAction module

import unittest
from shared.LCAction import *
from shared.LCFields import *

class BasicActionTest(unittest.TestCase):
    def test_LCAction(self):
        lcaction1 = LCAction("tester")
        lcaction2 = LCAction("tester")
        lcaction3 = LCAction("tester2")
        self.assertEqual("tester", str(lcaction1))
        self.assertEqual("tester", repr(lcaction1))
        self.assertEqual(lcaction1, lcaction2)
        self.assertNotEqual(lcaction1, lcaction3)
        

    def test_Forward(self):
        obj1 = Forward(3)
        obj2 = Forward(3)
        obj3 = Forward(4)
        self.assertEqual("Forward:3", str(obj1))
        self.assertEqual("Forward:3", repr(obj1))
        self.assertEqual(3, obj1.get())
        self.assertEqual(obj1, obj2)
        self.assertNotEqual(obj1, obj3)

    def test_SetField(self):
        obj1 = SetField(LCField('field',4))
        obj2 = SetField(LCField('field',4))
        obj3 = SetField(LCField('differentfield',4))
        self.assertEqual("SetField:field:4", str(obj1))
        self.assertEqual("SetField:field:4", repr(obj1))
        self.assertEqual(LCField('field',4), obj1.get())
        self.assertEqual(obj1, obj2)
        self.assertNotEqual(obj1, obj3)
        
    def test_WriteMetadata(self):
        obj1 = WriteMetadata(4, 255)
        obj2 = WriteMetadata(4, 255)
        obj3 = WriteMetadata(4, 65535)
        self.assertEqual("WriteMetadata:4 mask 255", str(obj1))
        self.assertEqual("WriteMetadata:4 mask 255", repr(obj1))
        self.assertEqual((4,255), obj1.get())
        self.assertEqual(obj1, obj2)
        self.assertNotEqual(obj1, obj3)

    def test_PushVLAN(self):
        obj1 = PushVLAN()
        obj2 = PushVLAN()
        self.assertEqual("PushVLAN", str(obj1))
        self.assertEqual("PushVLAN", repr(obj1))
        self.assertEqual(obj1, obj2)

    def test_PopVLAN(self):
        obj1 = PopVLAN()
        obj2 = PopVLAN()
        self.assertEqual("PopVLAN", str(obj1))
        self.assertEqual("PopVLAN", repr(obj1))
        self.assertEqual(obj1, obj2)

    def test_Continue(self):
        obj1 = Continue()
        obj2 = Continue()
        self.assertEqual("Continue", str(obj1))
        self.assertEqual("Continue", repr(obj1))
        self.assertEqual(obj1, obj2)

    def test_Drop(self):
        obj1 = Drop()
        obj2 = Drop()
        self.assertEqual("Drop", str(obj1))
        self.assertEqual("Drop", repr(obj1))
        self.assertEqual(obj1, obj2)

if __name__ == '__main__':
    unittest.main()
