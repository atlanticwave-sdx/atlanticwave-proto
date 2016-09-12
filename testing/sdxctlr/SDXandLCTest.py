# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


# Unit tests for the SDXController class

import unittest
import threading
import networkx as nx
import mock
import subprocess
import os
from time import sleep

from shared.UserPolicy import *
from sdxctlr.BreakdownEngine import *
from sdxctlr.TopologyManager import TopologyManager
from sdxctlr.ParticipantManager import ParticipantManager
from sdxctlr.LocalControllerManager import LocalControllerManager
from sdxctlr.SDXController import *
from localctlr.LocalController import *

from shared.JsonUploadPolicy import *
from shared.L2TunnelPolicy import *

FNULL = open(os.devnull, 'w')

TOPO_CONFIG_FILE = 'test_manifests/singleswitchtopo.manifest'
PART_CONFIG_FILE = 'test_manifests/participants.manifest'
JSON_POLICY_FILE = 'test_manifests/example_single_switch_config.json'




class ConnectivityTest(unittest.TestCase):

    @classmethod
    @mock.patch('sdxctlr.SDXController.RestAPI', autospec=True)
    def setUpClass(cls, restapi):
        # Lovingly stolen from the the Local Controller tests.

        print "Set up virtual switch"
        subprocess.check_call(['mn', '-c'], stdout=FNULL, stderr=subprocess.STDOUT)
        subprocess.call(['fuser', '-k', '55767/tcp'], stdout=FNULL, stderr=subprocess.STDOUT)
        subprocess.call(['fuser', '-k', '55767/tcp'], stdout=FNULL, stderr=subprocess.STDOUT)
        subprocess.call(['fuser', '-k', '5555/tcp'], stdout=FNULL, stderr=subprocess.STDOUT)
        subprocess.call(['fuser', '-k', '5555/tcp'], stdout=FNULL, stderr=subprocess.STDOUT)
        subprocess.check_call(['ovs-vsctl', 'add-br', 'br_ovs'])
        subprocess.check_call(['ovs-vsctl', 'add-port', 'br_ovs', 'vi0', '--', 'set', 'Interface', 'vi0', 'type=internal'])
        subprocess.check_call(['ovs-vsctl', 'set', 'bridge', 'br_ovs', 'other-config:datapath-id=0000000000000001'])
        subprocess.check_call(['ovs-vsctl', 'set-controller', 'br_ovs', 'tcp:127.0.0.1:6633'])
        print "Virtual switch is setup\n"


        # Setup RyuControllerInterface, which sets up RyuTranslateInterface
        # Only returns once RyuTranslateInterface has a datapath.
        part = ParticipantManager(PART_CONFIG_FILE)
        topo = TopologyManager(TOPO_CONFIG_FILE)
        lc = LocalControllerManager(TOPO_CONFIG_FILE)
        cls.sdxctlr = SDXController()
        cls.ctlrint = LocalController()

#        cls.ctlrint.start_sdx_controller_connection()
        while len(cls.sdxctlr.connections) == 0:
            print "Waiting for harness connection"
            sleep(1)

#        cls.ctlrint.start_main_loop()


    @classmethod
    def tearDownClass(cls):
        pass

    @mock.patch('sdxctlr.SDXController.RestAPI', autospec=True)
    def atest_add_json_upload(self, restapi):
        
        man = RuleManager()

        # Get a JSON policy from a file
        with open(JSON_POLICY_FILE) as datafile:
            # Based on: https://stackoverflow.com/questions/8369219/how-do-i-read-a-text-file-into-a-string-variable-in-python
            data = json.load(datafile)
            #data = datafile.read().replace('\n', '')
        valid_rule = JsonUploadPolicy('sdonovan', data)

        rule_num = man.add_rule(valid_rule)
        man.remove_rule(rule_num, 'sdonovan')

    @mock.patch('sdxctlr.SDXController.RestAPI', autospec=True)
    def test_L2_tunnel_upload(self, restapi):
        
        man = RuleManager()

        # Example JSON
        l2json =  {"l2tunnel":{
            "starttime":"1985-04-12T23:20:50",
            "endtime":"1985-04-12T23:20:50",
            "srcswitch":"atl-switch",
            "dstswitch":"atl-switch",
            "srcport":1,
            "dstport":2,
            "srcvlan":1492,
            "dstvlan":1789,
            "bandwidth":1}}

        # Get a JSON policy from a file
        l2rule = L2TunnelPolicy('sdonovan', l2json)

        rule_num = man.add_rule(l2rule)
        man.remove_rule(rule_num, 'sdonovan')



                
if __name__ == '__main__':
    unittest.main()
