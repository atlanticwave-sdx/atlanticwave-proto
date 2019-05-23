# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


# Unit tests for the SDXController class

import unittest
import threading
import networkx as nx
import mock

from shared.UserPolicy import *
from sdxctlr.BreakdownEngine import *
from sdxctlr.TopologyManager import TopologyManager
from sdxctlr.UserManager import UserManager
from sdxctlr.LocalControllerManager import LocalControllerManager
from sdxctlr.SDXController import *

from shared.L2TunnelPolicy import *

db = ":memory:"
TOPO_CONFIG_FILE = 'test_manifests/topo.manifest'
PART_CONFIG_FILE = 'test_manifests/participants.manifest'
JSON_POLICY_FILE = 'test_manifests/example_config.json'

class RuleStandin(object):
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return "RuleStandin %s" % self.name
    def set_cookie(self, cookie):
        return
    
class UserPolicyStandin(UserPolicy):
    # Use the username as a return value for checking validity.
    def __init__(self, username, json_rule):
        super(UserPolicyStandin, self).__init__(username, json_rule)
        self.valid = username
        self.breakdown = json_rule
        
    def check_validity(self, topology, authorization_func):
        # Verify that topology is a nx.Graph, and authorization_func is ???
        if not isinstance(topology, nx.Graph):
            raise Exception("Topology is not nx.Graph")
        if self.valid == True:
            return True
        raise Exception("NOT VALID")
    
    def breakdown_rule(self, topology, authorization_func):
        # Verify that topology is a nx.Graph, and authorization_func is ???
        print "breakdown_rule called: %s:%s" % (authorization_func, topology)
        if not isinstance(topology, TopologyManager):
            print "- Raising Exception"
            raise Exception("Topology is not nx.Graph")
        if self.valid == True:
            print "- Success"
            return [UserPolicyBreakdown("1.2.3.4",
                                        [RuleStandin("rule1"),
                                         RuleStandin("rule2")])]
        raise Exception("BAD")
    
    def _parse_json(self, json_rule):
        return

    
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

def rmhappy(param):
    pass

no_loop_options = Dict2Obj({'manifest':TOPO_CONFIG_FILE,
                            'database':db,
                            'topo':False,
                            'host':'0.0.0.0',
                            'lcport':5555,
                            'sport':5001,
                            'port':5000,
                            'shib':False})



class SingletonTest(unittest.TestCase):
    @mock.patch('sdxctlr.SDXController.SDXControllerConnectionManager', autospec=True)
    @mock.patch('sdxctlr.SDXController.RestAPI', autospec=True)
    def test_singleton(self, restapi, cxm):
        #part = UserManager(db, PART_CONFIG_FILE)
        #topo = TopologyManager(topology_file=TOPO_CONFIG_FILE)
        #lc = LocalControllerManager(manifest=TOPO_CONFIG_FILE)
        
        firstManager = SDXController(False, no_loop_options)
        secondManager = SDXController()

        self.failUnless(firstManager is secondManager)
        del firstManager
        del secondManager

class AddRuleTest(unittest.TestCase):
    @mock.patch('sdxctlr.SDXController.SDXControllerConnectionManager', autospec=True)
    @mock.patch('sdxctlr.SDXController.RestAPI', autospec=True)
    def test_add_and_remove_no_exception(self, restapi, cxm):
        
        #part = UserManager(db,PART_CONFIG_FILE)
        #topo = TopologyManager(topology_file=TOPO_CONFIG_FILE)
        #lc = LocalControllerManager(manifest=TOPO_CONFIG_FILE)
        sdxctlr = SDXController(False, no_loop_options)
        
        man = RuleManager()#'db','sdxcontroller',rmhappy,rmhappy)
        valid_rule = UserPolicyStandin(True, True)

        sdxctlr._send_breakdown_rule = mock.MagicMock()

        rule_num = man.add_rule(valid_rule)

        man.remove_rule(rule_num, 'sdonovan')
        

class JsonUploadTest(unittest.TestCase):
    
    @mock.patch('sdxctlr.SDXController.SDXControllerConnectionManager', autospec=True)
    @mock.patch('sdxctlr.SDXController.RestAPI', autospec=True)
    def test_L2_tunnel_upload(self, restapi, cxm):
        
        man = RuleManager('db',)

        # Example JSON
        l2json =  {"L2Tunnel":{
            "starttime":"1985-04-12T23:20:50",
            "endtime":"1985-04-12T23:20:50",
            "srcswitch":"br1",
            "dstswitch":"br4",
            "srcport":1,
            "dstport":2,
            "srcvlan":1492,
            "dstvlan":1789,
            "bandwidth":1}}

        # Get a JSON policy from a file
        l2rule = L2TunnelPolicy('sdonovan', l2json)

        rule_num = man.add_rule(l2rule)
        man.remove_rule(rule_num, 'sdonovan')


    @mock.patch('sdxctlr.SDXController.SDXControllerConnectionManager', autospec=True)
    @mock.patch('sdxctlr.SDXController.RestAPI', autospec=True)
    def test_L2_tunnel_two_site_upload(self, restapi, cxm):
        
        man = RuleManager()

        # Example JSON
        l2json =  {"L2Tunnel":{
            "starttime":"1985-04-12T23:20:50",
            "endtime":"1985-04-12T23:20:50",
            "srcswitch":"br2",
            "dstswitch":"br3",
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
