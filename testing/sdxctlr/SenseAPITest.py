# Copyright 2018 - Sean Donovan
# AtlanticWave/SDX Project


# Unit Tests for the SENSEAPI class

import unittest
import threading
import networkx as nx
import mock

from sdxctlr.SenseAPI import *
from sdxctlr.TopologyManager import TopologyManager
from sdxctlr.RuleManager import RuleManager

from shared.L2TunnelPolicy import L2TunnelPolicy

from sdxctlr.RestAPI import RestAPI
DB_FILE = ":memory:"
BASIC_MANIFEST_FILE = "senseapi_manifests/twoswitch-onelc-noncorsa.manifest"

def add_rule(param):
    # For Rule Manager
    print "Add Rule %s" % param

def rm_rule(param):
    # For Rule Manager
    print "Rm  Rule %s" % param
    

class SingletonTest(unittest.TestCase):
    def test_singleton(self):
        tm = TopologyManager(topology_file=BASIC_MANIFEST_FILE)
        rm = RuleManager(DB_FILE,
                         send_user_rule_breakdown_add=add_rule,
                         send_user_rule_breakdown_remove=rm_rule)

        first = SenseAPI(DB_FILE)
        second = SenseAPI()

        self.failUnless(first is second)


class PutGetDeltaTest(unittest.TestCase):
    def setUp(self):
        self.raw_request = "raw_request"
        self.sdx_rule = "SDX RULES!"
        self.model_id  = 3
        self.status = STATUS_COMMITTED
        self.status_created = STATUS_ACTIVATED

    def test_put(self):
        # Make sure _put_delta doesn't blow up
        tm = TopologyManager(topology_file=BASIC_MANIFEST_FILE)
        rm = RuleManager(DB_FILE,
                         send_user_rule_breakdown_add=add_rule,
                         send_user_rule_breakdown_remove=rm_rule)

        api = SenseAPI(DB_FILE)

        #print api._get_all_deltas()
        delta_id = 1
        api._put_delta(delta_id, self.raw_request, self.sdx_rule,
                       self.model_id)
        
    def test_put_get(self):
        # Make sure _put_delta() and _get_delta_by_id() work
        tm = TopologyManager(topology_file=BASIC_MANIFEST_FILE)
        rm = RuleManager(DB_FILE,
                         send_user_rule_breakdown_add=add_rule,
                         send_user_rule_breakdown_remove=rm_rule)

        api = SenseAPI(DB_FILE)

        delta_id = 2
        api._put_delta(delta_id, self.raw_request, self.sdx_rule,
                       self.model_id)
        raw_delta = api._get_delta_by_id(delta_id)

        self.failUnlessEqual(raw_delta['delta_id'], delta_id)
        self.failUnlessEqual(raw_delta['raw_request'], self.raw_request)
        self.failUnlessEqual(raw_delta['sdx_rule'], self.sdx_rule)
        self.failUnlessEqual(raw_delta['model_id'], self.model_id)
        self.failUnlessEqual(raw_delta['status'], STATUS_ACCEPTED)

    def test_get(self):
        # Test _put_delta() and get_delta()
        tm = TopologyManager(topology_file=BASIC_MANIFEST_FILE)
        rm = RuleManager(DB_FILE,
                         send_user_rule_breakdown_add=add_rule,
                         send_user_rule_breakdown_remove=rm_rule)

        api = SenseAPI(DB_FILE)

        delta_id = 3
        api._put_delta(delta_id, self.raw_request, self.sdx_rule,
                       self.model_id, self.status)
        state, phase = api.get_delta(delta_id)

        self.failUnlessEqual(state, STATUS_COMMITTED)
        self.failUnlessEqual(phase, PHASE_COMMITTED)

        delta_id = 4
        api._put_delta(delta_id, self.raw_request, self.sdx_rule,
                       self.model_id, self.status_created)
        state, phase = api.get_delta(delta_id)

        self.failUnlessEqual(state, STATUS_ACTIVATED)
        self.failUnlessEqual(phase, PHASE_RESERVED)

    def test_put_update(self):
        # Test updates on _put_delta() command
        tm = TopologyManager(topology_file=BASIC_MANIFEST_FILE)
        rm = RuleManager(DB_FILE,
                         send_user_rule_breakdown_add=add_rule,
                         send_user_rule_breakdown_remove=rm_rule)

        api = SenseAPI(DB_FILE)

        delta_id = 5
        api._put_delta(delta_id, self.raw_request, self.sdx_rule,
                       self.model_id, self.status)
        raw_delta = api._get_delta_by_id(delta_id)

        self.failUnlessEqual(raw_delta['delta_id'], delta_id)
        self.failUnlessEqual(raw_delta['raw_request'], self.raw_request)
        self.failUnlessEqual(raw_delta['sdx_rule'], self.sdx_rule)
        self.failUnlessEqual(raw_delta['model_id'], self.model_id)
        self.failUnlessEqual(raw_delta['status'], self.status)

        api._put_delta(delta_id, status=self.status_created, update=True)
        raw_delta = api._get_delta_by_id(delta_id)
        #print "    %s" % raw_delta

        self.failUnlessEqual(raw_delta['delta_id'], delta_id)
        self.failUnlessEqual(raw_delta['raw_request'], self.raw_request)
        self.failUnlessEqual(raw_delta['sdx_rule'], self.sdx_rule)
        self.failUnlessEqual(raw_delta['model_id'], self.model_id)
        self.failUnlessEqual(raw_delta['status'], self.status_created)

    def test_put_invalid(self):
        # Test invalid _put_delta commands
        tm = TopologyManager(topology_file=BASIC_MANIFEST_FILE)
        rm = RuleManager(DB_FILE,
                         send_user_rule_breakdown_add=add_rule,
                         send_user_rule_breakdown_remove=rm_rule)

        api = SenseAPI(DB_FILE)

        #   - Put invalid things
        delta_id = 6
        self.failUnlessRaises(SenseAPIError, api._put_delta,
                              delta_id, self.raw_request, self.sdx_rule)
                              # missing one item            
        
        #   - Put duplicate delta
        delta_id = 7
        api._put_delta(delta_id, self.raw_request, self.sdx_rule,
                       self.model_id, self.status)
        self.failUnlessRaises(SenseAPIError, api._put_delta,
                              delta_id, self.raw_request, self.sdx_rule,
                              self.model_id, self.status) 
        
        #   - Put update on delta that doesn't exist
        delta_id = 8
        self.failUnlessRaises(SenseAPIError, api._put_delta,
                              delta_id, self.raw_request, update=True)

        #   - Put empty update in
        delta_id = 9
        api._put_delta(delta_id, self.raw_request, self.sdx_rule,
                       self.model_id, self.status)
        self.failUnlessRaises(SenseAPIError, api._put_delta,
                              delta_id, update=True)


    def test_get_by_id_invalid(self):
        # Test invalid _get_delta_by_id() commands
        #   - invalid deltaid
        tm = TopologyManager(topology_file=BASIC_MANIFEST_FILE)
        rm = RuleManager(DB_FILE,
                         send_user_rule_breakdown_add=add_rule,
                         send_user_rule_breakdown_remove=rm_rule)

        api = SenseAPI(DB_FILE)

        delta_id = 10
        self.failUnlessEqual(api._get_delta_by_id(delta_id),
                              None)
            

    def test_get_invalid(self):
        # Test invalid get_delta() commands
        #   - Invalid delta_id
        tm = TopologyManager(topology_file=BASIC_MANIFEST_FILE)
        rm = RuleManager(DB_FILE,
                         send_user_rule_breakdown_add=add_rule,
                         send_user_rule_breakdown_remove=rm_rule)

        api = SenseAPI(DB_FILE)

        delta_id = 11
        self.failUnlessEqual(api.get_delta(delta_id),
                              (None,None))

class CommitTest(unittest.TestCase):
    def setUp(self):
        self.raw_request = "raw_request"
        self.model_id  = 3
        self.status = STATUS_COMMITTED
        self.status_created = STATUS_ACTIVATED

        
        self.starttime = "1985-04-12T12:23:56"
        self.endtime = "2985-04-12T12:23:56"
        self.srcswitch = "br1"
        self.dstswitch = "br2"
        self.srcport = 1
        self.dstport = 2
        self.srcvlan = 100
        self.dstvlan = 200
        self.bandwidth = 100000
        self.srcendpoint = "atldtn-br1"
        self.dstendpoint = "miadtn-br2"
        
        jsonrule = {"L2Tunnel":{
            "starttime":self.starttime,
            "endtime":self.endtime,
            "srcswitch":self.srcswitch,
            "dstswitch":self.dstswitch,
            "srcport":self.srcport,
            "dstport":self.dstport,
            "srcvlan":self.srcvlan,
            "dstvlan":self.dstvlan,
            "bandwidth":self.bandwidth}}
        self.sdx_rule = L2TunnelPolicy("SENSE", jsonrule)

    def test_build_p2p(self):
        tm = TopologyManager(topology_file=BASIC_MANIFEST_FILE)
        rm = RuleManager(DB_FILE,
                         send_user_rule_breakdown_add=add_rule,
                         send_user_rule_breakdown_remove=rm_rule)

        api = SenseAPI(DB_FILE)

        api._build_point_to_point_rule(self.srcendpoint, self.dstendpoint,
                                       self.srcvlan, self.dstvlan,
                                       self.bandwidth, self.starttime,
                                       self.endtime)
                
    def test_good_check(self):
        tm = TopologyManager(topology_file=BASIC_MANIFEST_FILE)
        rm = RuleManager(DB_FILE,
                         send_user_rule_breakdown_add=add_rule,
                         send_user_rule_breakdown_remove=rm_rule)

        api = SenseAPI(DB_FILE)

        api._check_SDX_rule(self.sdx_rule)
        api.check_point_to_point_rule(self.srcendpoint, self.dstendpoint,
                                      self.srcvlan, self.dstvlan,
                                      self.bandwidth, self.starttime,
                                      self.endtime)


    def test_basic_commit(self):
        tm = TopologyManager(topology_file=BASIC_MANIFEST_FILE)
        rm = RuleManager(DB_FILE,
                         send_user_rule_breakdown_add=add_rule,
                         send_user_rule_breakdown_remove=rm_rule)

        api = SenseAPI(DB_FILE)

        delta_id = 20
        api._put_delta(delta_id, self.raw_request, self.sdx_rule,
                       self.model_id)
        api.commit(delta_id)

        

class CancelTest(unittest.TestCase):
    def setUp(self):
        self.raw_request = "raw_request"
        self.model_id  = 3
        self.status_good = STATUS_COMMITTED
        self.status_created = STATUS_ACTIVATED

        
        self.starttime = "1985-04-12T12:23:56"
        self.endtime = "2985-04-12T12:23:56"
        self.srcswitch = "br1"
        self.dstswitch = "br2"
        self.srcport = 1
        self.dstport = 2
        self.srcvlan = 100
        self.dstvlan = 200
        self.bandwidth = 100000
        self.srcendpoint = "atldtn-br1"
        self.dstendpoint = "miadtn-br2"
        
        jsonrule = {"L2Tunnel":{
            "starttime":self.starttime,
            "endtime":self.endtime,
            "srcswitch":self.srcswitch,
            "dstswitch":self.dstswitch,
            "srcport":self.srcport,
            "dstport":self.dstport,
            "srcvlan":self.srcvlan,
            "dstvlan":self.dstvlan,
            "bandwidth":self.bandwidth}}
        self.sdx_rule = L2TunnelPolicy("SENSE", jsonrule)   

    def test_basic_committed_cancel(self):
        # Calling cancel() on committed deltaid, expect STATUS_GOOD back
        tm = TopologyManager(topology_file=BASIC_MANIFEST_FILE)
        rm = RuleManager(DB_FILE,
                         send_user_rule_breakdown_add=add_rule,
                         send_user_rule_breakdown_remove=rm_rule)

        api = SenseAPI(DB_FILE)

        delta_id = 30
        api._put_delta(delta_id, self.raw_request, self.sdx_rule,
                       self.model_id)
        api.commit(delta_id)

        self.failUnlessEqual(HTTP_GOOD, api.cancel(delta_id))
        self.failUnlessEqual(None, api._get_delta_by_id(delta_id))

    def test_basic_committed_clear(self):
        # Calling clear() on committed deltaid, expect STATUS_GOOD back
        tm = TopologyManager(topology_file=BASIC_MANIFEST_FILE)
        rm = RuleManager(DB_FILE,
                         send_user_rule_breakdown_add=add_rule,
                         send_user_rule_breakdown_remove=rm_rule)

        api = SenseAPI(DB_FILE)

        delta_id = 31
        api._put_delta(delta_id, self.raw_request, self.sdx_rule,
                       self.model_id)
        api.commit(delta_id)

        self.failUnlessEqual(HTTP_GOOD, api.clear(delta_id))
        self.failUnlessEqual(None, api._get_delta_by_id(delta_id))

    def test_basic_uncommitted_cancel(self):
        # Calling cancel() on uncommitted deltaid, expect STATUS_GOOD back
        tm = TopologyManager(topology_file=BASIC_MANIFEST_FILE)
        rm = RuleManager(DB_FILE,
                         send_user_rule_breakdown_add=add_rule,
                         send_user_rule_breakdown_remove=rm_rule)

        api = SenseAPI(DB_FILE)

        delta_id = 32
        api._put_delta(delta_id, self.raw_request, self.sdx_rule,
                       self.model_id)

        self.failUnlessEqual(HTTP_GOOD, api.clear(delta_id))
        self.failUnlessEqual(None, api._get_delta_by_id(delta_id))
    
    def test_cancel_bad_delta(self):
        # Calling cancel() on bad delta, expect STATUS_NOT_FOUND back
        tm = TopologyManager(topology_file=BASIC_MANIFEST_FILE)
        rm = RuleManager(DB_FILE,
                         send_user_rule_breakdown_add=add_rule,
                         send_user_rule_breakdown_remove=rm_rule)

        api = SenseAPI(DB_FILE)

        delta_id = 33

        self.failUnlessEqual(HTTP_NOT_FOUND, api.cancel(delta_id))

    def test_double_clear(self):
        # Calling cancel() first time, expect STATUS_GOOD back
        # Calling cancel() on same deltaid, expect STATUS_NOT_FOUND back
        tm = TopologyManager(topology_file=BASIC_MANIFEST_FILE)
        rm = RuleManager(DB_FILE,
                         send_user_rule_breakdown_add=add_rule,
                         send_user_rule_breakdown_remove=rm_rule)

        api = SenseAPI(DB_FILE)

        delta_id = 34
        api._put_delta(delta_id, self.raw_request, self.sdx_rule,
                       self.model_id)

        self.failUnlessEqual(HTTP_GOOD, api.cancel(delta_id))
        self.failUnlessEqual(None, api._get_delta_by_id(delta_id))
        self.failUnlessEqual(HTTP_NOT_FOUND, api.cancel(delta_id))
        self.failUnlessEqual(None, api._get_delta_by_id(delta_id))



class ModelTest(unittest.TestCase):
    def setup(self):
        pass

    def test_generate_model_basic(self):
        tm = TopologyManager(topology_file=BASIC_MANIFEST_FILE)
        rm = RuleManager(DB_FILE,
                         send_user_rule_breakdown_add=add_rule,
                         send_user_rule_breakdown_remove=rm_rule)

        api = SenseAPI(DB_FILE)

        model = api.generate_model()
        #print "MODEL\n%s\n\n\n" % str(model)
        #import json
        #print "FULL TOPOLOGY\n%s\n\n\n" % json.dumps(tm.get_topology().nodes(
        #    data=True), sort_keys=True, indent=4)
        #print "SIMPLIFIED TOPOLOGY\n%s\n\n\n" % json.dumps(api.simplified_topo.nodes(
        #    data=True), sort_keys=True, indent=4)
#FIXME: What else?
        
if __name__ == '__main__':
    unittest.main()
