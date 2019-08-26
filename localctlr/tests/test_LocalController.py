# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


# Unit tests for LocalController class

import unittest
import mock
import subprocess
import os
from localctlr.LocalController import *
from RemoteControllerHarness import RemoteControllerHarness
from time import sleep

FNULL = open(os.devnull, 'w')

#https://www.blog.pythonlibrary.org/2014/02/14/python-101-how-to-change-a-dict-into-a-class/
class Dict2Obj(object):
    """
    Turns a dictionary into a class
    """
 
    #----------------------------------------------------------------------
    def __init__(self, dictionary):
        """Constructor"""
        for key in dictionary:
            setattr(self, key, dictionary[key])

TOPO_CONFIG_FILE = os.path.dirname(os.path.realpath(__file__)) +'/rtitest.manifest'

options = Dict2Obj({'database':":memory:",
                    'manifest':TOPO_CONFIG_FILE,
                    'name':'atl',
                    'host':'127.0.0.1',
                    'sdxport':5555})

class LocalControllerTest(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Taken and modified from  RyuControllerInterfaceTest.py

        cls.logger = logging.getLogger(cls.__class__.__name__)
        formatter = logging.Formatter('%(asctime)s %(name)-12s: %(thread)s %(levelname)-8s %(message)s')
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        console.setFormatter(formatter)
        cls.logger.setLevel(logging.DEBUG)
        cls.logger.addHandler(console)

        cls.logger.debug("Beginning %s" % cls.__name__)

        # Setup the virtual switch
        cls.logger.debug( "Set up virtual switch")
        #subprocess.check_call(['mn', '-c'], stdout=FNULL, stderr=subprocess.STDOUT)
        sleep(1)
        #subprocess.call(['fuser', '-k', '55767/tcp'], stdout=FNULL, stderr=subprocess.STDOUT)
        #subprocess.call(['fuser', '-k', '55767/tcp'], stdout=FNULL, stderr=subprocess.STDOUT)
        #subprocess.call(['fuser', '-k', '5555/tcp'], stdout=FNULL, stderr=subprocess.STDOUT)
        #subprocess.call(['fuser', '-k', '5555/tcp'], stdout=FNULL, stderr=subprocess.STDOUT)
        subprocess.check_call(['ovs-vsctl', 'add-br', 'br_ovs'])
        subprocess.check_call(['ovs-vsctl', 'add-port', 'br_ovs', 'vi0', '--', 'set', 'Interface', 'vi0', 'type=internal'])
        subprocess.check_call(['ovs-vsctl', 'set', 'bridge', 'br_ovs', 'protocols=OpenFlow13'])
        subprocess.check_call(['ovs-vsctl', 'set', 'bridge', 'br_ovs', 'other-config:datapath-id=0000000000000001'])

        subprocess.check_call(['ovs-vsctl', 'set-controller', 'br_ovs', 'tcp:127.0.0.1:6633'])
        cls.logger.debug("Virtual switch is setup\n")


        # Setup RyuControllerInterface, which sets up RyuTranslateInterface
        # Only returns once RyuTranslateInterface has a datapath.
        cls.logger.debug("LocalControllerTest.setUpClass - Options:\n%s\n" % options)
        cls.harness = RemoteControllerHarness()
        cls.ctlrint = LocalController(True, options)

#        cls.ctlrint.start_sdx_controller_connection()
        while cls.harness.is_connected() == False:
            cls.logger.debug("Waiting for harness connection")
            sleep(1)

       # sleep(20)
#        cls.ctlrint.start_main_loop()

    @classmethod
    def tearDownClass(cls):
        # Delete virtual switch
        # FIXME: whenever this is called, there is an error: "cannot switch to a different thread"
        subprocess.check_call(['ovs-vsctl', 'del-port', 'vi0'])
        subprocess.check_call(['ovs-vsctl', 'del-br', 'br_ovs'])
        sleep(5)
        cls.logger.debug("Ending %s" % cls.__name__)
#        subprocess.call(['fuser', '-k', '55767/tcp'], stdout=FNULL, stderr=subprocess.STDOUT)
#        subprocess.call(['fuser', '-k', '5555/tcp'], stdout=FNULL, stderr=subprocess.STDOUT)
#        subprocess.call(['fuser', '-k', '55767/tcp'], stdout=FNULL, stderr=subprocess.STDOUT)
#        subprocess.call(['fuser', '-k', '5555/tcp'], stdout=FNULL, stderr=subprocess.STDOUT)
        pass

    def call_test_rule_installation(self, num=None, test5=None, test6=None, 
                                    test7=None, test8=None, test9=None, 
                                    test10=None):
        # nose isn't that smart, since it has "test" in the name, it tries to 
        # run it as a test. This breaks things. So, workaround.
        if num == None:
            return
        if test5 == None or test6 == None:
            argcount = 2 # self, num
            if test5 != None:
                argcount += 1
            if test6 != None:
                argcount += 1

            raise(TypeError("call_test_rule_installation() takes at least 4 arguments (%d given)" % argcount))

        sleep(1)
        #self.logger.debug("test_rule_installation_" + str(num))
        self.logger.debug("LC: %s" % (self.ctlrint))
        self.logger.debug("SENDING NEW COMMAND: %s" % self.harness.examples[num])
        self.harness.send_new_command(self.harness.examples[num])
        sleep(1) # To make sure the rule changes have propogated.
                 # 0.1 second isn't enough
        output = subprocess.check_output(['ovs-ofctl', '-O', 'OpenFlow13','dump-flows', 'br_ovs'])
        self.logger.debug("INSTALL OUTPUT: %s" % output)
        lines = output.split('\n')

        self.harness.send_rm_command(self.harness.examples[num])
        sleep(1) # To make sure the rule changes have propogated.
        output = subprocess.check_output(['ovs-ofctl', '-O', 'OpenFlow13','dump-flows', 'br_ovs'])
        self.logger.debug("REMOVE OUTPUT: %s" % output)
        rmlines = output.split('\n')

        # Installation tests
        for line in lines:
            #int "CHECKING LINE: %s" % line
            if "priority=100" not in line:
                continue
            self.logger.debug("MATCHED LINE:\n     %s" % line)
            count = 0
            for e in line.split(','):
                self.logger.debug("%d:%s" % (count, e))
                count += 1
            self.failUnlessEqual(line.split(',')[5].strip(), test5)
            self.failUnlessEqual(line.split(',')[6].strip(), test6)
            if test7 != None:
                self.failUnlessEqual(line.split(',')[7].strip(), test7)
            if test8 != None:
                self.failUnlessEqual(line.split(',')[8].strip(), test8)
            if test9 != None:
                self.failUnlessEqual(line.split(',')[9].strip(), test9)
            if test10 != None:
                self.failUnlessEqual(line.split(',')[10].strip(), test10)

        # Removal
        for line in rmlines:
            self.failUnless("priority=100" not in line)
                
            
    def test_rule_installation_0(self):
        self.logger.warning("BEGIN %s" % (self.id()))
        self.call_test_rule_installation(0, 
                                         "priority=100",
                                         "dl_dst=00:00:00:00:00:00 actions=set_field:00:00:00:00:00:02->eth_dst")
    def test_rule_installation_1(self):
        self.logger.warning("BEGIN %s" % (self.id()))
        self.call_test_rule_installation(1, 
                                         "priority=100",
                                         "ip",
                                         "nw_src=1.2.3.4 actions=set_field:2.3.4.5->ip_src")
    def test_rule_installation_2(self):
        self.logger.warning("BEGIN %s" % (self.id()))
        self.call_test_rule_installation(2,
                                         "priority=100",
                                         "ip",
                                         "dl_dst=00:00:00:00:00:03",
                                         "nw_src=3.4.5.6 actions=set_field:00:00:00:00:00:04->eth_src")
    def test_rule_installation_3(self):
        self.logger.warning("BEGIN %s" % (self.id()))
        self.call_test_rule_installation(3, 
                                         "priority=100",
                                         "ip",
                                         "dl_dst=00:00:00:00:00:05",
                                         "nw_src=4.5.6.7 actions=set_field:00:00:00:00:00:04->eth_src",
                                         "set_field:5.6.7.8->ip_dst")

    def test_rule_installation_4(self):
        self.logger.warning("BEGIN %s" % (self.id()))
        self.call_test_rule_installation(4,
                                         "priority=100",
                                         "tcp actions=output:1")
                                         




if __name__ == '__main__':
    unittest.main()
