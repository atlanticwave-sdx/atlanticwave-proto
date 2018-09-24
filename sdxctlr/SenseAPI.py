# Copyright 2018 - Sean Donovan
# AtlanticWave/SDX Project

# Some parts are based on the Sense Resource Manager for the OSCARS interface:
# https://bitbucket.org/berkeleylab/sensenrm-oscars/src/d09db31aecbe7654f03f15eed671c0675c5317b5/sensenrm_server.py

from lib.AtlanticWaveModule import AtlanticWaveModule

from shared.L2MultipointPolicy import L2MultipointPolicy
from shared.L2TunnelPolicy import L2TunnelPolicy

from AuthenticationInspector import AuthenticationInspector
from AuthorizationInspector import AuthorizationInspector
from RuleManager import RuleManager
from TopologyManager import TopologyManager, TOPO_EDGE_TYPE
from UserManager import UserManager
from RuleRegistry import RuleRegistry

from threading import Lock

# XML imports


# Flask imports
from flask import Flask, jsonify, abort, make_response, request
from flask_restful import Api, Resource, reqparse, fields, marshal
import ssl

# Other imports
import networkx as nx
from networkx.readwrite import json_graph
import json

# Multithreading
from threading import Thread


# Globals

errors = {
    'NotFound': {
        'message': "A resource with that ID does not exist.",
        'status': 404,
        'extra': "No extra information",
    },
}
        


class SenseAPI(AtlanticWaveModule):
    ''' The SenseAPI is the main interface for SENSE integration. It generates
        the appropriate XML for the current configuration status, and sends 
        updates automatically based on changes in rules and topology as provided
        by the RuleManager and TopologyManager.
    '''

    def __init__(self, loggerprefix='sdxcontroller',
                 host='0.0.0.0', port=5001):
        global app, api, context

        loggerid = loggerprefix + ".sense"
        super(SenseAPI, self).__init__(loggerid)

        # Set up local repositories for rules and topology to perform diffs on.
        self.current_rules = RuleManager().get_rules()
        self.current_topo = TopologyManager().get_topology()
        self.simplified_topo = None
        self.topo_XML = None
        self.delta_XML = None
        self.topolock = Lock()
        self.userid = "SENSE"
        
        # Register update functions
        RuleManager().register_for_rule_updates(self.rule_add_callback,
                                                self.rule_rm_callback)
        TopologyManager().register_for_topology_updates(
            self.topo_change_callback)

        # Flask setup
        #FIXME: SSL
        #context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2) 
        #context.load_verify_locations(capath=ssl_config["capath"])
        #context.load_cert_chain(ssl_config["hostcertpath"],
        #                        ssl_config["hostkeypath"])
        # sss._https_verify_certificates(enable=ssl_config["httpsverify"])
        app = Flask(__name__)
        api = Api(app, errors=errors)
        api.add_resource(ModelsAPI,
            '/sense-rm/api/sense/v1/models',
            endpoint='models')
        api.add_resource(DeltasAPI,
            '/sense-rm/api/sense/v1/deltas',
            endpoint='deltas')
        api.add_resource(DeltaAPI,
            '/sense-rm/api/sense/v1/delta/<string:deltaid>',
            endpoint='delta')
        api.add_resource(CommitsAPI,
            '/sense-rm/api/sense/v1/delta/<string:deltaid>/actions/commit',
            endpoint='commits')
        api.add_resource(ClearAPI,
            '/sense-rm/api/sense/v1/delta/<string:deltaid>/actions/clear',
            endpoint='clear')
        api.add_resource(CancelAPI,
            '/sense-rm/api/sense/v1/delta/<string:deltaid>/actions/cancel',
            endpoint='cancel')
        
        
        

        
        # Connection handling
        #FIXME - Is it inbound or outbound?

        

        self.logger.warning("%s initialized: %s" % (self.__class__.__name__,
                                                    hex(id(self))))

        self._INTERNAL_TESTING_DELETE_FINAL_CHECKIN()

    def _INTERNAL_TESTING_DELETE_FINAL_CHECKIN(self):
        nodes = self.current_topo.nodes()
        print("\n\nNODES WITH DETAILS\n" +
              json.dumps(self.current_topo.nodes(data=True),
                                    indent=4, sort_keys=True))
        print "\n\nEDGES\n" + str(self.current_topo.edges()) + "\n\n\n"
        for node in nodes:
            print "  %s : %s" % (node, self.current_topo[node])
        for node in nodes:
            print "\n%s:%s " % (node, json.dumps(self.current_topo[node],
                                                    indent=4, sort_keys=True))
        self.generate_simplified_topology()
        for node in self.simplified_topo.nodes():
            if self.simplified_topo.node[node]['type'] != 'central':
                self.get_bw_available_on_egress_port(node)
                self.get_vlans_in_use_on_egress_port(node)

        for srcnode in self.simplified_topo.nodes():
            if self.simplified_topo.node[srcnode]['type'] != 'central':
                for dstnode in self.simplified_topo.nodes():
                    if self.simplified_topo.node[dstnode]['type'] != 'central':
                        self.install_point_to_point_rule(srcnode, dstnode,
                                                    100, 200,
                                                    100000,
                                                    "1985-04-12T12:34:56",
                                                    "2985-04-12T12:34:56")
                        self.install_point_to_point_rule(srcnode, dstnode,
                                                    101, 201,
                                                    100000,
                                                    "1985-04-12T12:34:56",
                                                    "2985-04-12T12:34:56")
                        self.install_point_to_point_rule(srcnode, dstnode,
                                                    102, 202,
                                                    100000,
                                                    "1985-04-12T12:34:56",
                                                    "2985-04-12T12:34:56")
                        self.install_point_to_point_rule(srcnode, dstnode,
                                                    103, 203,
                                                    100000,
                                                    "1985-04-12T12:34:56",
                                                    "2985-04-12T12:34:56")
        
    def rule_add_callback(self, rule):
        ''' Handles rules being added. '''
        print "rule_add_callback - %s" % rule

    def rule_rm_callback(self, rule):
        ''' Handles rules being removed. '''
        print "rule_rm_callback - %s" % rule

    def topo_change_callback(self):
        ''' Handles topology changes. 
            FIXME: topologies don't change right now. '''
        pass

    def get_bw_available_on_egress_port(self, node):
        ''' Get the bandwidth available on a given egress port from the original
            network graph. Be sure to update topology before making these 
            requests. '''

        # Access the bandwidth from the original topology.
        print self.simplified_topo.node[node]
        start_node = self.simplified_topo.node[node]['start_node']
        end_node = self.simplified_topo.node[node]['end_node']
        bw_available = self.simplified_topo.node[node]['max_bw']
        bw_in_use = self.current_topo[start_node][end_node]['bw_in_use']

        print "%s: bw_available %s, bw_in_use %s" % (node, bw_available,
                                                     bw_in_use)
        # Return BW on egress port
        return (bw_available - bw_in_use)

    def get_vlans_in_use_on_egress_port(self, node):
        ''' Get the VLANs that are in use on a given egress port. '''

        # Access the bandwidth from the original topology.
        print self.simplified_topo.node[node]
        start_node = self.simplified_topo.node[node]['start_node']
        end_node = self.simplified_topo.node[node]['end_node']
        vlans_in_use = self.current_topo[start_node][end_node]['vlans_in_use']

        print "%s: vlans_in_use %s" % (node, vlans_in_use)

        # Return VLANs in use on egress port
        return vlans_in_use

    def get_vlans_available_on_egress_port(self, node):
        ''' Get VLANs available for SENSE API use. '''
        pass

    def generate_simplified_topology(self):
        ''' Calculates the 'black box' version of the topology, exposing only 
            the outside networks and DTNs as endpoints. The internals are *not*
            exposed, as we handle those ourselves. '''
        
        # Create graph with central node only.
        with self.topolock:
            self.simplified_topo = nx.Graph()
            self.simplified_topo.add_node('central')
            self.simplified_topo.node['central']['type'] = 'central'

            # For each EDGE node (returns true on TOPO_EDGE_TYPE), loop over
            # each connection on the edge node add a connection to the central
            # node.
            for node in self.current_topo.nodes(): # name of node
                print self.current_topo[node]
                t = self.current_topo.node[node]['type']
                if TOPO_EDGE_TYPE(t):
                    for edge in self.current_topo[node]: # edge dictionary
                        new_node = node + "-" + edge
                        self.simplified_topo.add_node(new_node)

                        # Copy over how to access the connection (which two
                        # nodes on the original topology), and the max bandwidth
                        # of the connection.                    
                        self.simplified_topo.node[new_node]['start_node'] = node
                        self.simplified_topo.node[new_node]['end_node'] = edge
                        print self.current_topo[node][edge]
                        bw = self.current_topo[node][edge]['weight']
                        self.simplified_topo.node[new_node]['max_bw'] = bw
                        self.simplified_topo.node[new_node]['type'] = t
        print("\n\nSIMPLIFIED TOPOLOGY\n%s\n\n" %
              json.dumps(self.simplified_topo.nodes(data=True),
                         indent=4, sort_keys=True))
                                                    

    def generate_full_XML(self):
        ''' Generates the full XML of the simplified topology. Deltas are 
            handled separately. '''
        pass

    def generate_delta_XML(self, changetype, change):
        ''' Generates a delta based on a change passed in.
              - Topology change
              - Bandwidth change (up or down)
        '''
        pass

    def send_SENSE_msg(self, msg):
        ''' Sends over a sense message. Handles formatting, and anything else
            necessary. '''
        pass

    def install_point_to_point_rule(self, endpoint1, endpoint2, vlan1, vlan2,
                                    bandwidth, starttime, endtime):
        ''' Installs a point-to-point rule. '''

        # Find the src switch and switch port
        src = self.simplified_topo.node[endpoint1]['start_node']
        srcswitch = self.simplified_topo.node[endpoint1]['end_node']
        srcport = self.current_topo[srcswitch][src][srcswitch]
        print "SRC %s switch %s port %s" % (src, srcswitch, srcport)

        # FInd the dst switch and switch port
        dst = self.simplified_topo.node[endpoint2]['start_node']
        dstswitch = self.simplified_topo.node[endpoint2]['end_node']
        dstport = self.current_topo[dstswitch][dst][dstswitch]
        print "DST %s switch %s port %s" % (dst, dstswitch, dstport)
        
        # Make JSON version
        jsonrule = {"L2Tunnel":{
            "starttime":starttime,
            "endtime":endtime,
            "srcswitch":srcswitch,
            "dstswitch":dstswitch,
            "srcport":srcport,
            "dstport":dstport,
            "srcvlan":vlan1,
            "dstvlan":vlan2,
            "bandwidth":bandwidth}}
        print "\nJSON\n%s" % (json.dumps(jsonrule, indent=4, sort_keys=True))
        
        # Perform check_syntax
        L2TunnelPolicy.check_syntax(jsonrule)

        # Make policy class
        policy = L2TunnelPolicy(self.userid, jsonrule)

        # Install rule
        hash = RuleManager().add_rule(policy)

        #FIXME: What should be returned?
        #FIXME: What to do about Exceptions?
        pass
    
    def install_point_to_multipoint_rule(self, endpointvlantuplelist,
                                         bandwidth,  starttime, endtime):
        ''' Installs a point-to-multipoint rule. '''
        #FIXME: this will need to reworked, but it's useful for prototyping
        # Make JSON version
        endpoints = []
        for (sw, po, vlan) in endpointvlantuplelist:
            endpoints.append({"switch":sw, "port":po, "vlan":vlan})
        jsonrule = {"L2Multipoint":{
            "starttime":starttime,
            "endtime":endtime,
            "bandwidth":bandwidth,
            "endpoints":endpoints}}
        
        # Perform check_syntax
        L2MultipointPolicy.check_syntax(jsonrule)

        # Make policy class
        policy = L2MultipointPolicy(self.userid, jsonrule)

        # Install rule
        hash = RuleManager().add_rule(policy)

        #FIXME: What should be returned?
        #FIXME: What to do about Exceptions?
        pass


    def connection_thread(self):
        pass

    def handle_new_connection(self):
        pass

class SenseAPIResource(Resource):
    ''' Has common pieces for all Resource objects used by the SenseAPI, 
        including logging. '''

    def __init__(self,loggeridsuffix, loggeridprefix='sdxcontroller.sense'):
        loggerid = loggeridprefix + "." + loggeridsuffix
        super(SenseAPIResource, self).__init__()

    def _setup_loggers(self, loggerid, logfilename=None, debuglogfilename=None):
                ''' Internal function for setting up the logger formats. '''
        # Copied from https://github.com/atlanticwave-sdx/atlanticwave-proto/blob/master/lib/AtlanticWaveModule.py#L49
        import logging
        self.logger = logging.getLogger(loggerid)
        self.dlogger = logging.getLogger("debug." + loggerid)
        if logfilename != None:
            formatter = logging.Formatter('%(asctime)s %(name)-12s: %(thread)s %(levelname)-8s %(message)s')
            console = logging.StreamHandler()
            console.setLevel(logging.WARNING)
            console.setFormatter(formatter)
            logfile = logging.FileHandler(logfilename)
            logfile.setLevel(logging.DEBUG)
            logfile.setFormatter(formatter)
            self.logger.setLevel(logging.DEBUG)
            self.logger.addHandler(console)
            self.logger.addHandler(logfile)

        if debuglogfilename != None:
            formatter = logging.Formatter('%(asctime)s %(name)-12s: %(thread)s %(levelname)-8s %(message)s')
            console = logging.StreamHandler()
            console.setLevel(logging.DEBUG)
            console.setFormatter(formatter)
            logfile = logging.FileHandler(debuglogfilename)
            logfile.setLevel(logging.DEBUG)
            logfile.setFormatter(formatter)
            self.dlogger.setLevel(logging.DEBUG)
            self.dlogger.addHandler(console)
            self.dlogger.addHandler(logfile)

    def dlogger_tb(self):
        ''' Print out the current traceback. '''
        from traceback import format_stack
        tbs = format_stack()
        all_tb = "Traceback: id: %s\n" % str(hex(id(self)))
        for line in tbs:
            all_tb = all_tb + line
        self.dlogger.warning(all_tb)



model_fields = {
    'id': fields.Raw,
    'href': fields.Raw,
    'creationTime': fields.Raw,
    'model': fields.Raw
}

delta_fields = {
    'id': fields.Raw,
    'lastModified': fields.Raw,
    'description': fields.Raw,
    'modelId': fields.Raw,
    'reduction': fields.Raw,
    'addition': fields.Raw
}
        
        

        
class ModelsAPI(SenseAPIResource):
    def __init__(self):
        super(ModelsAPI, self).__init__(self.__class__.__name__)
        self.dlogger.DEBUG("__init__() start")
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('current', type=str, default='true')
        self.reqparse.add_argument('summary', type=str, default='false')
        self.reqparse.add_argument('encode', type=str, default='false')
        self.models = None #FIXME
        self.dlogger.DEBUG("__init__() complete")
    
    def get(self):
        self.dlogger.DEBUG("get() start")

        retval = None        #FIXME
        
        self.logger.INFO("get() returning %s" % retval)
        self.dlogger.DEBUG("get() complete")
        return retval
    
    def post(self):
        self.dlogger.DEBUG("post() start")

        args = self.reqparse.parse_args()
        self.logger.INFO("post() args %s" % args)
        retval = {'models': marshal(self.models, model_fields)}, 201 #FIXME
        
        self.logger.INFO("post() returning %s" % retval)
        self.dlogger.DEBUG("post() complete")
        return retval
    
class DeltasAPI(SenseAPIResource):
    def __init__(self):
        super(DeltasAPI, self).__init__(self.__class__.__name__)
        self.dlogger.DEBUG("__init__() start")
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('id', type=str, location='json')
        self.reqparse.add_argument('lastModified', type=str, location='json')
        self.reqparse.add_argument('modelId', type=str, location='json')
        self.reqparse.add_argument('reduction', type=str, location='json')

        self.dlogger.DEBUG("__init__() complete")
    
    def get(self):
        self.dlogger.DEBUG("get() start")
        self.logger.INFO("get() id %s" % deltaid)
        retval = {'deltas': marchal(deltas, delta_fields)}       #FIXME
        
        self.logger.INFO("get() returning %s" % retval)
        self.dlogger.DEBUG("get() complete")
        return retval
    
    def post(self):
        self.dlogger.DEBUG("post() start")

        args = self.reqparse.parse_args()
        self.logger.INFO("post() args %s" % args)
        deltas, mystatus = deltas.processDelta(args)              #FIXME
        self.logger.INFO("post() results %s" % mystatus)
        rstatus = 201
        if int(mystatus) != 200:
            rstatus = mystatus
            
        retval = {'deltas': marshal(deltas, delta_fields)}, rstatus

        self.logger.INFO("post() returning %s" % retval)
        self.dlogger.DEBUG("post() complete")
        return retval
    
class DeltaAPI(SenseAPIResource):
    def __init__(self):
        super(DeltaAPI, self).__init__(self.__class__.__name__)
        self.dlogger.DEBUG("__init__() start")
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('summary', type=str, default='true')
        self.reqparse.add_argument('deltaid', type=str, location='json')
        self.dlogger.DEBUG("__init__() complete")
    
    def get(self, deltaid):
        self.dlogger.DEBUG("get() start")
        self.logger.INFO("get() deltaid %s" % deltaid)
        status, phase = nrmdeltas.getDelta(deltaid)                #FIXME
        self.dlogger.DEBUG("get() %s:%s" % (status, phase))
        retval = {'state': str(phase), 'deltaid': str(deltaid)}, status
        self.logger.INFO("get() returning %s" % retval)
        self.dlogger.DEBUG("get() complete")
        return retval

class CommitsAPI(SenseAPIResource):
    def __init__(self):
        super(CommitsAPI, self).__init__(self.__class__.__name)
        self.dlogger.DEBUG("__init__() start")
        self.dlogger.DEBUG("__init__() complete")

    def put(self, deltaid):
        self.dlogger.DEBUG("put() start")
        self.logger.INFO("put() deltaid %s" % deltaid)
        status = nrmcommits.commit(deltaid)                      #FIXME
        if status:
            self.logger.INFO("put() deltaid %s COMMITTED" % deltaid)
            retval = {'result': "COMMITTED"}, 200
        else:
            self.logger.INFO("put() deltaid %s COMMIT FAILED" % deltaid)
            retval = {'result': "FAILED"}, 404
            
        self.logger.INFO("put() returning %s" % retval)
        self.dlogger.DEBUG("put() complete")
        return retval                         
        
    def get(self):
        self.dlogger.DEBUG("get() start")
        retval = {'result': True}, 200
        self.dlogger.DEBUG("get() complete")
        return retval
        
    def post(self):
        self.dlogger.DEBUG("post() start")
        args = self.reqparse.parse_args()                   #FIXME - reqparse not instantiated... Copied from berkley's version
        #FIXME: this doesn't seem to do the same thing as put()... should it?
        self.dlogger.DEBUG("post() args: %s" % args)
        deltaid = args['id']
        self.logger.INFO("post() deltaid %s" % deltaid)
        retval = {'result': True}, 201
        self.logger.INFO("post() returning %s" % retval)
        self.dlogger.DEBUG("post() complete")
        return retval

class CancelAPI(SenseAPIResource):
    def __init__(self):
        super(CancelAPI, self).__init__(self.__class__.__name)
        self.dlogger.DEBUG("__init__() start")
        self.dlogger.DEBUG("__init__() complete")

    def put(self, deltaid):
        self.dlogger.DEBUG("put() start")
        self.logger.INFO("put() deltaid %s" % deltaid)
        status, resp = nrmcancel.cancel(deltaid)                      #FIXME
        if status:
            self.logger.INFO("put() deltaid %s CANCELLED" % deltaid)
            retval = {'result': "CANCELLED"}, status
        else:
            self.logger.INFO("put() deltaid %s CANCEL FAILED, %s" %
                             (deltaid, resp))
            retval = {'result': "FAILED", 'mesg':str(resp)}, 404
            
        self.logger.INFO("put() returning %s" % retval)
        self.dlogger.DEBUG("put() complete")
        return retval                         
        
    def get(self):
        self.dlogger.DEBUG("get() start")
        retval = {'result': True}, 200
        self.dlogger.DEBUG("get() complete")
        return retval
        
    def post(self, deltaid):
        self.dlogger.DEBUG("post() start")
        #FIXME: this doesn't seem to do the same thing as put()... should it?
        self.logger.INFO("post() deltaid %s" % deltaid)
        retval = {'result': True}, 201
        self.logger.INFO("post() returning %s" % retval)
        self.dlogger.DEBUG("post() complete")
        return retval
        
class ClearAPI(SenseAPIResource):
    def __init__(self):
        super(ClearAPI, self).__init__(self.__class__.__name)
        self.dlogger.DEBUG("__init__() start")
        self.dlogger.DEBUG("__init__() complete")

    def put(self, deltaid):
        self.dlogger.DEBUG("put() start")
        self.logger.INFO("put() deltaid %s" % deltaid)
        status, resp = nrmclear.clear(deltaid)                      #FIXME
        if status:
            self.logger.INFO("put() deltaid %s CLEARED" % deltaid)
            retval = {'result': "CLEARED"}, status
        else:
            self.logger.INFO("put() deltaid %s CLEAR FAILED, %s" %
                             (deltaid, resp))
            retval = {'result': "FAILED", 'mesg':str(resp)}, 404
            
        self.logger.INFO("put() returning %s" % retval)
        self.dlogger.DEBUG("put() complete")
        return retval                         
        
    def get(self):
        self.dlogger.DEBUG("get() start")
        retval = {'result': True}, 200
        self.dlogger.DEBUG("get() complete")
        return retval
        
    def post(self, deltaid):
        self.dlogger.DEBUG("post() start")
        #FIXME: this doesn't seem to do the same thing as put()... should it?
        self.logger.INFO("post() deltaid %s" % deltaid)
        retval = {'result': True}, 201
        self.logger.INFO("post() returning %s" % retval)
        self.dlogger.DEBUG("post() complete")
        return retval

#FIXME: ModelAPI not used, so not copying here.
