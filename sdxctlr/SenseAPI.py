# Copyright 2018 - Sean Donovan
# AtlanticWave/SDX Project

# Some parts are based on the Sense Resource Manager for the OSCARS interface:
# https://bitbucket.org/berkeleylab/sensenrm-oscars/src/d09db31aecbe7654f03f15eed671c0675c5317b5/sensenrm_server.py

from lib.AtlanticWaveManager import AtlanticWaveManager

from shared.L2MultipointPolicy import L2MultipointPolicy
from shared.L2TunnelPolicy import L2TunnelPolicy

from AuthenticationInspector import AuthenticationInspector
from AuthorizationInspector import AuthorizationInspector
from RuleManager import RuleManager
from TopologyManager import TopologyManager, TOPO_EDGE_TYPE
from UserManager import UserManager
from RuleRegistry import RuleRegistry

from threading import Lock
import cPickle as pickle
import rdflib


# Flask imports
from flask import Flask, jsonify, abort, make_response, request
from flask_restful import Api, Resource, reqparse, fields, marshal
import ssl

# Other imports
import networkx as nx
from networkx.readwrite import json_graph
import json
import zlib
import base64
import uuid

# Multithreading
from threading import Thread

# Timing
from datetime import datetime, timedelta, tzinfo
from shared.constants import rfc3339format, MAXENDTIME
sensetimeformat = "%Y-%m-$dT%H:%M:%S.000000-0000"

# Globals
errors = {
    'NotFound': {
        'message': "A resource with that ID does not exist.",
        'status': 404,
        'extra': "No extra information",
    },
}

# HTTP status codes:
HTTP_GOOD           = 200
HTTP_CREATED        = 201
HTTP_ACCEPTED       = 202
HTTP_NO_CONTENT     = 204
HTTP_NOT_MODIFIED   = 304
HTTP_BAD_REQUEST    = 400
HTTP_FORBIDDEN      = 403     # RETURNED BY FLASK-RESTFUL ONLY
HTTP_NOT_FOUND      = 404
HTTP_NOT_ACCEPTABLE = 406
HTTP_CONFLICT       = 409
HTTP_SERVER_ERROR   = 500     # RETURNED BY FLASK-RESTFUL ONLY

# SENSE status codes
STATUS_ACCEPTING    = "Accepting"
STATUS_ACCEPTED     = "Accepted"
STATUS_COMMITTING   = "Committing"
STATUS_COMMITTED    = "Committed"
STATUS_ACTIVATING   = "Activating"
STATUS_ACTIVATED    = "Activated"
STATUS_FAILED       = "Failed"

# PHASE definition
PHASE_RESERVED        = "PHASE_RESERVED"
PHASE_COMMITTED       = "PHASE_COMMITTED"

# URN info
baseurn = "urn:ogf:network:"
fullurn = baseurn + "atlanticwave-sdx.net"
awaveurn = "urn:ogf:network:atlanticwave-sdx.net"

SERVICE_DOMAIN_L2_TUNNEL = "l2switching"
SERVICE_DOMAIN_AWAVE = "AtlanticWaveSDX"



class SenseAPIError(Exception):
    pass

class SenseAPIB64Error(SenseAPIError):
    ''' For Base64-related errors. Usually debug errors. '''
    pass

class SenseAPIClientError(SenseAPIError):
    ''' Catch all for Client-side errors. Likley has subclasses. '''
    pass

class SenseAPIArgumentError(SenseAPIClientError):
    ''' For errors with arguments being passed in. '''
    pass

        


class SenseAPI(AtlanticWaveManager):
    ''' The SenseAPI is the main interface for SENSE integration. It generates
        the appropriate XML for the current configuration status, and sends 
        updates automatically based on changes in rules and topology as provided
        by the RuleManager and TopologyManager.
    '''
    # Delta Database entries:
    # {"delta_id":delta_id,
    #  "raw_request": raw_addition (pickled in DB),
    #  "sdx_rule": sdx_rule (pickled in DB),
    #  "status": status code (see list, below),
    #  "last_modified": last modified time,
    #  "timestamp": initial timestamp of the delta,
    #  "model_id": Model ID,
    #  "hash": Hash returned when installing a rule to the RuleManager}

    # Model Database entries:
    # {"model_id": Model ID (UUID),
    #  "model_data": XML that was sent over,
    #  "model_raw_info": raw topology information (pickled in DB),
    #  "timestamp": Timestamp of model}

    def __init__(self, db_filename, loggerprefix='sdxcontroller',
                 host='0.0.0.0', port=5002):
        global app, api, context

        loggerid = loggerprefix + ".sense"
        super(SenseAPI, self).__init__(loggerid)

        # For FLASK
        self.host = host
        self.port = port
        self.urlbase = "http://%s:%s" % (host, port)

        # SENSE Service constants
        self.SVC_SENSE    = "ServiceDomain:l2switching"
        self.SVC_NONSENSE = "ServiceDomain:AWaveServices"
        
        # Set up local repositories for rules and topology to perform diffs on.
        self.current_rules = RuleManager().get_rules()
        self.current_topo = TopologyManager().get_topology()
        self.simplified_topo = None
        self.list_of_services = None
        self.topo_XML = None
        self.delta_XML = None
        self.topolock = Lock()
        self.userid = "SENSE"

        # Start database
        db_tuples = [('delta_table','delta'), ('model_table', 'model')]
        self._initialize_db(db_filename, db_tuples, True)
        self.delta_table.delete() #FIXME: these shouldn't be needed.
        self.model_table.delete() #FIXME: these shouldn't be needed.
        
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
            endpoint='models',
            resource_class_kwargs={'urlbase':self.urlbase})
        api.add_resource(DeltasAPI,
            '/sense-rm/api/sense/v1/deltas',
            endpoint='deltas',
            resource_class_kwargs={'urlbase':self.urlbase})
        api.add_resource(DeltaAPI,
            '/sense-rm/api/sense/v1/deltas/<string:deltaid>',
            endpoint='delta',
            resource_class_kwargs={'urlbase':self.urlbase})
        api.add_resource(CommitsAPI,
            '/sense-rm/api/sense/v1/deltas/<string:deltaid>/actions/commit',
            endpoint='commits',
            resource_class_kwargs={'urlbase':self.urlbase})

        
        self.generate_simplified_topology()
                
        # Connection handling
        #FIXME - Is it inbound or outbound?

        api_thread = Thread(target=self.api_process)
        api_thread.daemon = True
        api_thread.start()
        self.logger.critical("Opening socket %s:%s" % (self.host, self.port))

        self.logger.warning("%s initialized: %s" % (self.__class__.__name__,
                                                    hex(id(self))))




        
        self.__print_all_deltas()
        #self.__print_topology_details(self.simplified_topo)
        self.__print_topology_details(self.current_topo)
        print "Neighbors of Miadtn: %s" % self.current_topo['miadtn']
        print "Neighbors of br1   : %s" % self.current_topo['br1']
        print "Neighbors of br2   : %s" % self.current_topo['br2']
        print "br1 neighbor list  : %s" % self.current_topo['br1'].keys()
        print "br2 neighbor list  : %s" % self.current_topo['br2'].keys()
        for n in self.current_topo['br1'].keys():
            print "br1-%s:  %s" % (n, self.current_topo['br1'][n]['br1'])
        for n in self.current_topo['br2'].keys():
            print "br2-%s:  %s" % (n, self.current_topo['br2'][n]['br2'])
        print "\n\n"

        model, newbool = self.get_latest_model()
        print "get_latest_model %s, %s" % (newbool, model['model'])
        print "\n\n"
        model, newbool = self.get_latest_model()
        print "get_latest_model %s, %s" % (newbool, model['model'])
        
        print "\n\n"
        print "simplified_topo:\n"
        self.__print_topology_details(self.simplified_topo)
        print "\n\n\n\n"
        #self._INTERNAL_TESTING_DELETE_FINAL_CHECKIN()

    def api_process(self):
        app.run(host=self.host, port=self.port)
        #FIXME: need SSL, threaded, debug

    def __print_topology_details(self, topo):
        #DEBUGING ONLY, SHOULD DELETE
        # Pass either topo - current_topo, simplified_topo - and print out
        # the details of the nodes and the edges
        print("\n\nNODES WITH DETAILS\n%s" %
              json.dumps(topo.nodes(data=True), indent=4, sort_keys=True))
        print("\n\nEDGES WITH DETAILS\n%s\n\n\n" %
              json.dumps(topo.edges(data=True), indent=4, sort_keys=True))

    def __print_all_deltas(self):
        deltas = self.get_all_deltas()

        print "\n\n&&&&& DELTAS &&&&&"
        for d in deltas:
            print d
        print "&&&&&        &&&&&\n\n"
        

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
                                                    "2985-04-12T12:34:56",
                                                    1)
                        self.install_point_to_point_rule(srcnode, dstnode,
                                                    101, 201,
                                                    100000,
                                                    "1985-04-12T12:34:56",
                                                    "2985-04-12T12:34:56",
                                                    2)
                        self.install_point_to_point_rule(srcnode, dstnode,
                                                    102, 202,
                                                    100000,
                                                    "1985-04-12T12:34:56",
                                                    "2985-04-12T12:34:56",
                                                    3)
                        self.install_point_to_point_rule(srcnode, dstnode,
                                                    103, 203,
                                                    100000,
                                                    "1985-04-12T12:34:56",
                                                    "2985-04-12T12:34:56",
                                                    4)

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
        start_node = self.simplified_topo.node[node]['start_node']
        end_node = self.simplified_topo.node[node]['end_node']
        bw_available = self.simplified_topo.node[node]['max_bw']
        bw_in_use = self.current_topo[start_node][end_node]['bw_in_use']

        self.dlogger.debug("get_bw_available_on_egress_port: %s" %
                           self.simplified_topo.node[node])
        self.dlogger.debug("  %s: bw_available %s, bw_in_use %s" %
                           (node, bw_available, bw_in_use))
        
        # Return BW on egress port
        return (bw_available - bw_in_use)

    def get_vlans_in_use_on_egress_port(self, node):
        ''' Get the VLANs that are in use on a given egress port. '''

        # Access the bandwidth from the original topology.
        start_node = self.simplified_topo.node[node]['start_node']
        end_node = self.simplified_topo.node[node]['end_node']
        vlans_in_use = self.current_topo[start_node][end_node]['vlans_in_use']

        self.dlogger.debug("get_vlans_in_use_on_egress_port: %s" %
                           self.simplified_topo.node[node])
        self.dlogger.debug("  %s: vlans_in_use %s" % (node, vlans_in_use))

        # Return VLANs in use on egress port
        return vlans_in_use

    def get_vlans_available_on_egress_port(self, node):
        ''' Get VLANs available for SENSE API use. 
            Take in a node name
            Returns a string with the available VLANs.
        '''

        # Get available VLANs
        raw_available_vlans = self.simplified_topo.node[node]['available_vlans']
        available_vlans = TopologyManager().get_available_vlan_list(
            raw_available_vlans)

        # Get VLANs in use
        in_use = self.get_vlans_in_use_on_egress_port(node)
        
        # Get difference
        # https://www.geeksforgeeks.org/python-intersection-two-lists/
        diff = set(available_vlans).difference(in_use)

        # Simplify to text
        sortedlist = sorted(diff)
        index = 0
        begin = None
        current = None
        text_vlan = ""

        while index < len(sortedlist):
            begin = sortedlist[index]
            current = begin

            index += 1

            while (index < len(sortedlist) and
                   current + 1 == sortedlist[index]):
                current += 1
                index += 1

            if begin == current:
                text_vlan += "%d" % current
            else:
                text_vlan += "%d-%d" % (begin, current)

            if index < len(sortedlist):
                text_vlan += ","

        # Return text
        return text_vlan
    
    def generate_list_of_services(self):
        ''' Generates a list of external facing services based on endpoints. 
            Any service that has at least one endpoint at the end of the 
            controlled network is included in the list.

            Each element in the list is quite simple:
              {"service":"servicename",
               "bandwidth":bandwidth in bits per second,
               "starttime":start time string,
               "endtime":end time string
               "endpoints": [ list of endpoint tuples]}

            An endpoint tuple looks as follows:
              ("endpointname",VLAN number)

            The servicename includes the Service Domain.
            The endpointname include the switch/port combo.
            Neither include the URN.
            starttime and endtime are in the SENSE format.
        
            Requires the simplified topology to be generated. '''
        self.current_rules = RuleManager().get_rules()
        self.list_of_services = []
        
        # Get exterior ports - from the simplified_topology
        exterior_nodes = self.simplified_topo.nodes()
        exterior_nodes.remove('central')

        print "\nEXTERIOR NODES: %s" % exterior_nodes
        print "\nRULES: %s\n\n" % self.current_rules
        
        # Loop through rules

        for r in self.current_rules:
            rule = RuleManager().get_raw_rule(r[0])
            potential_endpoints = rule.get_endpoints()
            # - Loop through endpoints
            endpoints = []
            print "\n RULE: %s" % rule
            for (e, f, v) in potential_endpoints:
                print "   endpoint: %s, %s, %d" % (e, f, v)
                # -- check if rule ends on an exterior port
                if (("%s-%s" % (e,f)) in exterior_nodes):
                    # -- if it does, save off name
                    endpoints.append(("%s-%s" % (e,f), v))
                elif (("%s-%s" % (f,e)) in exterior_nodes):
                    endpoints.append(("%s-%s" % (f,e), v))
            # - if list is not empty, then continue. If empty, next rule
            if len(endpoints) == 0:
                continue
            
            # - get start and end times
            start_time = rule.get_start_time()
            stop_time = rule.get_stop_time()
            # - if now < start_time or now > stop_time, don't care about
            #   the rule
            start_datetime = datetime.strptime(start_time, rfc3339format)
            stop_datetime =  datetime.strptime(stop_time,  rfc3339format)
            now = datetime.now()
            if (now < start_datetime or
                now > stop_datetime):
                continue
            
            # - get it's bandwidth
            bandwidth = rule.get_bandwidth()

            # - get the user
            user = rule.get_user()
            
            # - create service name:
            #   Get the rule_hash from the rule
            rule_hash = rule.get_rule_hash()
            #   if user is self.userid, then give back uuid
            if user == self.userid:
                # -- find the delta in the local database to get the UUID
                delta = self._get_delta_by_rule_hash(rule_hash)
                # -- Put together service name.
                service_name = "%s:conn+%s" % (self.SVC_SENSE,
                                               delta)
                
            #   if user is other, then make up name
            else:
                service_name = "%s:conn+%s" % (self.SVC_NONSENSE,
                                               rule_hash)
            
            # - create new service dictionary
            svc_dict = {"service":service_name,
                        "bandwidth":bandwidth,
                        "starttime":start_time,
                        "endtime":stop_time,
                        "endpoints":endpoints}
            # - add new dictionary to self.list_of_services
            self.list_of_services.append(svc_dict)
        return
    
    def generate_simplified_topology(self):
        ''' Calculates the 'black box' version of the topology, exposing only 
            the outside networks and DTNs as endpoints. The internals are *not*
            exposed, as we handle those ourselves. '''
        
        # Create graph with central node only.
        with self.topolock:
            self.current_topo = TopologyManager().get_topology()     # Update!
            self.simplified_topo = nx.Graph()
            self.simplified_topo.add_node('central')
            self.simplified_topo.node['central']['type'] = 'central'

            # For each EDGE node (returns true on TOPO_EDGE_TYPE), loop over
            # each connection on the edge node add a connection to the central
            # node.
            for node in self.current_topo.nodes(): # name of node
                #print self.current_topo[node]
                t = self.current_topo.node[node]['type']
                alias = None
                if 'alias' in self.current_topo.node[node].keys():
                    alias = self.current_topo.node[node]['alias']
                if TOPO_EDGE_TYPE(t):
                    for edge in self.current_topo[node]: # edge dictionary
                        new_node = node + "-" + edge
                        self.simplified_topo.add_node(new_node)
                        self.simplified_topo.add_edge(new_node, 'central')

                        # Copy over how to access the connection (which two
                        # nodes on the original topology), and the max bandwidth
                        # of the connection.                    
                        self.simplified_topo.node[new_node]['start_node'] = node
                        self.simplified_topo.node[new_node]['end_node'] = edge
                        #print self.current_topo[node][edge]
                        bw = self.current_topo[node][edge]['weight']
                        self.simplified_topo.node[new_node]['max_bw'] = bw
                        vlans = self.current_topo[node][edge]['available_vlans']
                        self.simplified_topo.node[new_node]['available_vlans'] = vlans
                        self.simplified_topo.node[new_node]['type'] = t
                        if alias != None:
                            self.simplified_topo.node[new_node]['alias'] = alias

    def generate_model(self):
        ''' Generates a model of the simplified topology. '''
        
        # Boilerplate prefixes
        output  = "model: @prefix sd: <http://schemas.ogf.org/nsi/2013/12/services/definitions#> ."
        output += "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n"
        output += "@prefix owl: <http://www.w3.org/2002/07/owl#> .\n"
        output += "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n"
        output += "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n"
        output += "@prefix nml: <http://schemas.ogf.org/nml/2013/03/base#> .\n"
        output += "@prefix mrs: <http://schemas.ogf.org/mrs/2013/12/topology#> .\n\n\n"

        
        # Get all endpoints and active services
        endpoints = ""
        list_of_endpoints = []
        self.generate_simplified_topology()
        self.generate_list_of_services()


        for ep in self.simplified_topo.neighbors('central'):
            # For each endpoint:
            #  - Get endpoint name
            node = self.simplified_topo.node[ep]
            epname = "%s:%s" % (fullurn, ep)
            list_of_endpoints.append(epname)
            
            #  - Definition of VLANs available on said endpoint
            # FIXME: does this need to remove in-use VLANs?
            vlan_name = "%s:vlan_range" % epname
            vlan_def  = "<%s>\n" %vlan_name
            vlan_def += "                a nml:LabelGroup, owl:NamedIndividual ;\n"
            vlan_def += "                nml:labeltype <http://schemas.ogf.org/nml/2012/10/ethernet#vlan> ;\n"
            vlan_def += "                nml:values \"%s\" .\n\n" % self.get_vlans_available_on_egress_port(ep)

            #  - Bandwidth on a given port
            bw_name = "%s:BandwidthService" % epname
            available_bw = self.get_bw_available_on_egress_port(ep)
            bw_def  = "<%s>\n" % bw_name
            bw_def += "                a mrs:BandwidthService ;\n"
            bw_def += "                mrs:availableCapacity \"%d\"^^xsd:long ;\n" % available_bw
            bw_def += "                mrs:reservableCapacity \"%d\"^^xsd:long ;\n" % available_bw
            bw_def += "                mrs:maximumCapacity \"%d\"^^xsd:long ;\n" % node["max_bw"]
            bw_def += "                mrs:unit \"bps\" ;\n"
            bw_def += "                nml:belongsTo <%s> .\n\n" % epname
            
            #  - Definition of Link structure
            link_def  = "<%s>\n" % epname
            link_def += "                a nml:BidirectionalPort, owl:NamedIndividual ;\n"
            link_def += "                nml:belongsTo <%s:l2switching>, <%s> ;\n" % (fullurn, fullurn)
            link_def += "                nml:hasLabelGroup <%s> ;\n" % vlan_name
            link_def += "                nml:hasService <%s> ;\n" % bw_name
            if 'alias' in node.keys():
                link_def += "                nml:isAlias <%s> ;\n" % node['alias']
            link_def += "                nml:name \"%s\" .\n\n" % ep

            endpoints += vlan_def
            endpoints += bw_def
            endpoints += link_def

        # Add services and all the various related bits.
        services = ""
        for s in self.list_of_services:
            # - Pull out bandwidth and service name
            bandwidth = s['bandwidth']
            servicename = s['service']
            starttime = s['starttime']
            endtime = s['endtime']
            per_service_endpoints = []

            # - Loop through all service endpoints
            for e in s['endpoints']:
                (endpointname, vlannum) = e
                service_str = "%s::%s:resource+links-connection_1:vlan+%d" % (
                    fullurn, servicename, vlannum)

                # -- Add VLAN label for virtual port
                services += "<%s::%s:vlanport+%d:label+%d>\n" % (
                    fullurn, endpointname, vlannum, vlannum)
                services += "        a nml:Label ;\n"
                services += "        nml:belongsTo <%s::%s:vlanport+%d> ;\n" % (
                    fullurn, endpointname, vlannum)
                services += "        nml:existsDuring <%s:existsDuring> ;\n" % (
                    service_str)
                services += "        nml:labeltype <http://schemas.ogf.org/nml/2012/10/ethernet#vlan> ;\n"
                services += "        nml:value %d .\n\n" % vlannum
                
                # -- Add bandwidth on virtual port
                services += "<%s::%s:vlanport+%d:service+bw>\n" % (
                    fullurn, endpointname, vlannum)
                services += "        a mrs:BandwidthService ;\n"
                services += "        mrs:reservableCapacity \"%d\"^^xsd:long ;\n" % (bandwidth)
                services += "        mrs:type \"guaranteedCapped\" ;\n"
                services += "        mrs:unit \"bps\" ;\n"
                services += "        nml:belongsTo <%s::%s:vlanport+%d> ;\n" % (
                    fullurn, endpointname, vlannum)
                services += "        nml:existsDuring <%s:existsDuring> .\n\n" % (
                    service_str)
                
                # -- Add service lifetime
                services += "<%s:existsDuring>\n" % service_str
                services += "        a nml:Lifetime ;\n"
                services += "        nml:end \"%s\" ;\n" % endtime
                services += "        nml:start \"%s\" .\n\n" % starttime
                
                # -- Add virtual port
                services += "<%s::%s:vlanport+%d>\n" % (
                    fullurn, endpointname, vlannum)
                services += "        a nml:BidirectionalPort ;\n"
                services += "        nml:belongsTo <%s>,<%s:%s> ;\n" % (
                    service_str, fullurn, endpointname)
                services += "        nml:encoding <http://schemas.ogf.org/nml/2012/10/ethernet> ;\n"
                services += "        nml:existsDuring <%s:existsDuring> ;\n" % (
                    service_str)
                services += "        nml:hasLabel <%s::%s:vlanport+%d:label+%d> ;\n" % (
                    fullurn, endpointname, vlannum, vlannum)
                services += "        nml:hasService <%s::%s:vlanport+%d:service+bw> ;\n" % (
                    fullurn, endpointname, vlannum)
                services += "        nml:name \"UNKNOWN\" .\n\n"
                # -- Add virtual port to list_of_endpoints
                list_of_endpoints.append("%s:%s:vlanport+%d" % (
                    fullurn, endpointname, vlannum))
                per_service_endpoints.append("%s:%s:vlanport+%d" % (
                    fullurn, endpointname, vlannum))
                
            # - Add service
            endpoints_str = ""
            for entry in per_service_endpoints[:-1]:
                endpoints_str += "<%s>, " % entry
            endpoints_str += "<%s> ;" % per_service_endpoints[-1]
            
            services += "<%s>\n" % service_str
            services += "        a mrs:switchingSubnet ;\n"
            services += "        nml:belongsTo <%s> ;\n" % fullurn
            services += "        nml:encoding <http://schemas.ogf.org/nml/2012/10/ethernet> ;\n"
            services += "        nml:existsDuring <%s:existsDuring> ;\n" % (
                service_str)
            services += "        nml:hasBidirectionalPort %s\n" % endpoints_str
            services += "        nml:labelSwapping true ;\n"
            services += "        nml:labelType <http://schemas.ogf.org/nml/2012/10/ethernet#vlan> .\n\n"
        
        # Add topology (acts as switch)
        endpoints_str = ""
        for entry in list_of_endpoints[:-1]:
            endpoints_str += "<%s>, " % entry
        endpoints_str += "<%s> ;" % list_of_endpoints[-1]

        topology = "<%s>\n" % fullurn
        topology += "                a nml:Topology, owl:NamedIndividual ;\n"
        #        topology += "                nml:belongsTo" #Fixme: who?
        topology += "                nml:hasBidirectionalPort %s\n" % endpoints_str
        topology += "                nml:hasService <%s:l2switching> ;\n" % fullurn
        topology += "                nml:name \"AtlanticWave/SDX\" .\n\n"

        # Add L2 service domain
        service_domain  = "<%s:%s>\n" % (fullurn, self.SVC_SENSE)
        service_domain += "                 a nml:SwitchingService, owl:NamedIndividual ;\n"
        service_domain += "                 nml:encoding <http://schemas.ogf.org/nml/2012/10/ethernet#vlan> ;\n"
        service_domain += "                 nml:hasBidirectionalPort %s\n" % endpoints_str
        service_domain += "                 nml:labelSwaping \"false\" .\n\n"

        # Add AWave service domain
        #FIXME

        output += service_domain
        output += topology
        output += services
        output += endpoints

        return output


    def send_SENSE_msg(self, msg):
        ''' Sends over a sense message. Handles formatting, and anything else
            necessary. '''
        pass

    def install_point_to_point_rule(self, endpoint1, endpoint2, vlan1, vlan2,
                                    bandwidth, starttime, endtime, delta_id):
        ''' Installs a point-to-point rule. '''
        # Build policy
        policy = self._build_point_to_point_rule(endpoint1, endpoint2,
                                                 vlan1, vlan2, bandwidth,
                                                 starttime, endtime)
        
    def _install_policy(self, delta_id, policy):
        # Install rule
        self.dlogger.debug("_install_policy: %s:%s" % (delta_id, policy))
        hashval = RuleManager().add_rule(policy)

        # Push hash into DB
        self._put_delta(delta_id, hashval=hashval, status=STATUS_ACTIVATED,
                        update=True)

    def _remove_policy(self, delta):
        # Remove the rule
        # - Extract the username
        # - Extract the hash
                    
        username = self.userid
        rule_hash = delta['hash']
        RuleManager().remove_rule(rule_hash, username)

    def check_point_to_point_rule(self, endpoint1, endpoint2, vlan1, vlan2,
                                   bandwidth, starttime, endtime):
        ''' Checks to see if a rule will be valid before installing. '''
        # Build policy
        policy = self._build_point_to_point_rule( endpoint1, endpoint2,
                                                 vlan1, vlan2, bandwidth,
                                                 starttime, endtime)
        return self._check_SDX_rule(policy)
    
    def _check_SDX_rule(self, policy):
        ''' Helper function, so this function can be used in other locations.'''
        # Install rule
        try:
            RuleManager().test_add_rule(policy)
        except Exception as e:
            # This means that the rule cannot be added, for whatever reason.
            # That's fine!
            self.logger.INFO("check_point_to_point_rule() failed %e" % e)
            self.logger.INFO("    %s, %s, %s, %s" % (endpoint1, endpoint2,
                                                     vlan1, vlan2))
            self.logger.INFO("    %s, %s, %s" % (bandwidth, startime, endtime))
            return False
        else:
            return True
        

    def _build_point_to_point_rule(self, endpoint1, endpoint2, vlan1, vlan2,
                                   bandwidth, starttime, endtime):
        # Find the src switch and switch port
        src = self.simplified_topo.node[endpoint1]['start_node']
        srcswitch = self.simplified_topo.node[endpoint1]['end_node']
        srcport = self.current_topo[srcswitch][src][srcswitch]

        # Find the dst switch and switch port
        dst = self.simplified_topo.node[endpoint2]['start_node']
        dstswitch = self.simplified_topo.node[endpoint2]['end_node']
        dstport = self.current_topo[dstswitch][dst][dstswitch]
        
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
        
        # Perform check_syntax
        L2TunnelPolicy.check_syntax(jsonrule)

        # Make policy class
        policy = L2TunnelPolicy(self.userid, jsonrule)

        return policy 
    
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

    def get_latest_model(self):
        ''' Gets the latest model. 
            Returns tuple of the dictionary (described below), and bool whether
            the dictionary is new or not: (dictionary, new?)
             {'id': UUID of model,
              'href': address of model,
              'creationTime': timestamp of model,
              'model': the model itself}
        '''

        # Dictionary components
        model_id = None
        href = None
        creation_time = None
        model = None

        # Control components
        need_new_model = False
        retnew = False

        
        # Check DB: if there is a latest one, already inserted, use it.
        result = self.model_table.find_one(order_by=['timestamp'])

        if result != None:
            model_id = result['model_id']
            href = "%s/sense-rm/api/sense/v1/models/%s" % (self.urlbase,
                                                           model_id)
            creation_time = result['timestamp']
            model = result['model_data']

        # Now, do we need a new model? Two reasons for this:
        #  - There wasn't a model in the DB
        #  - The latest model in the DB is stale, based on changes to either
        #    the topology or to the rules that are installed
        if creation_time == None:
            need_new_model = True
        else:
            # Get the most recent time that there was a change
            topo_update_time = TopologyManager().get_last_modified_timestamp()
            rule_update_time = RuleManager().get_last_modified_timestamp()
            parsed_creation = datetime.strptime(creation_time, rfc3339format)
            parsed_topo = datetime.strptime(topo_update_time, rfc3339format)
            parsed_rule = datetime.strptime(rule_update_time, rfc3339format)

            # Check if model is stale
            if (parsed_creation < parsed_topo or
                parsed_creation < parsed_rule):
                need_new_model = True
            
        if need_new_model:
            # Generate the model
            model = self.generate_model()
            raw_model = self.simplified_topo
            
            # Get creation time
            creation_time = datetime.now().strftime(rfc3339format)
            
            # Get ID
            model_id = str(uuid.uuid5(uuid.NAMESPACE_URL,
                                      creation_time))

            # Insert it into the DB
            self._put_model(model_id, model, raw_model, creation_time)
            retnew = True

        # Return the correct format
        retdict = {'id':model_id,
                  'href':href,
                  'creationTime':creation_time,
                  'model':model}
        return (retdict, retnew)
    
    def process_deltas(self, args):
        # Parse the args
        self.dlogger.debug("process_delta() begin with args: %s" % args)
        self.__print_all_deltas()
        
        keys = args.keys()
        if ('id' not in keys or
            'lastModified' not in keys or
            'modelId' not in keys):
            raise SenseAPIArgumentError("Missing id, lastModified, or modelId: %s" %
                                        keys)
        if not ('reduction' in keys !=
                'addition' in keys): # poor man's xor - we only want one.
            raise SenseAPIArgumentError("Missing reduction or addition: %s" %
                                        keys)
        
        delta_id = args['id']
        last_modified = args['lastModified']
        model_id = args['modelId']

        if 'reduction' in keys and len(args['reduction']) > 0:
            try:
                reduction = self._decode_b64_gunzip(args['reduction'])
            except Exception as e:
                self.dlogger.error("Decoding error on Reduction: %s:%s" %
                                   (e, args['reduction']))
                return None, HTTP_BAD_REQUEST
                                   
            addition = None #FIXME: is this true? I don't think so.
        else:
            reduction = None
            try:
                addition = self._decode_b64_gunzip(args['addition'])
            except Exception as e:
                self.dlogger.error("Decoding error on Reduction: %s:%s" %
                                   (e, args['reduction']))
                return None, HTTP_BAD_REQUEST
        
        # If reduction:
        #  - parse reduction
        #  - check to make sure it's a valid delta
        #  - call cancel if a valid reduction is received,
        #    - cancel will deal with removing the delta from flows and DB
        #  - Return status
        delta = None
        status = None
        if reduction != None:
            try:
                parsed_reduction = self._parse_delta_reduction(reduction)
            except SenseAPIClientError as e:
                self.dlogger.error("process_deltas: Received \"%s\"" % e)
                return None, HTTP_BAD_REQUEST
            self.logger.info("Reduction %s to be removed" % parsed_reduction)
            delta = self._get_delta_by_id(parsed_reduction)
            #print "delta_by_id      = %s" % delta
            if delta == None:
                # Doesn't exist anymore 
                return None, HTTP_NOT_FOUND
            status = self.delete(parsed_reduction)
            retdelta = self._convert_delta(delta)
            self.logger.info("Reduction %s deleted %s" % (parsed_reduction,
                                                           status))

        # If addition:
        #  - parse addition
        #  - See if it's possible (BW, VLANs, etc.)
        #  - If possible, save off this new delta and return good status
        #  - If not possible, return failed status - raises errors
        else:
            try:
                parsed_addition_policy = self._parse_delta_addition(addition)
            except SenseAPIClientError as e:
                self.dlogger.error("process_deltas: Received %s" % e)
                return None, HTTP_BAD_REQUEST
            bd = RuleManager().test_add_rule(parsed_addition_policy)
            status = HTTP_ACCEPTED
            try:
                self._put_delta(delta_id, args, parsed_addition_policy,
                                model_id, status)
            except SenseAPIError as e:
                self.dlogger.error("process_deltas: Received %s" % e)
                return None, HTTP_CONFLICT                
            delta = self._get_delta_by_id(delta_id)
            retdelta = self._convert_delta(delta)

        self.dlogger.debug("process_deltas: returning %s,%s" % (retdelta,
                                                                status)) 
        return retdelta, status

    def _parse_delta_addition(self, raw_addition):
        # This is based on part of nrmDelta.processDelta() from senserm_oscars's
        # sensrm_delta.py.
        # Parses the raw_addition, and returns back the rule that will make the
        # addition.
        #
        # ASSUMPTION: only one rule is being added with each addition. Changes
        # would be needed if multiple rules are in each addition.
        #FIXME: anything else that needs to be returned back?

        endpoints = []
        starttime = None
        endtime = None
        bandwidth = 100*8000000 # 100mbps
        policy = None

        gr = rdflib.Graph()
        try:
            result = gr.parse(data=raw_addition, format='ttl')
            #FIXME: check the result
        except Exception as e:
            self.dlogger.error(
                "_parse_delta_addition: Error on parsing graph: %s" % e)
            self.dlogger.error("  Addition: %s" % raw_addition)
            raise SenseAPIClientError("Addition unparsable %s:%s" %
                                      (e, raw_addition))
            
        # Build up list of important information:
        #  - endpoints (switch, port, VLAN)
        #  - start and end times
        #  - bandwidth
        for s,p,o in gr:
            if awaveurn in str(s):
                # bandwidth - First as "vlanport" or "vlantag" is also in string
                if "service+bw" in str(s):
                    if "reservableCapacity" in str(p):
                        bandwidth = int(o)
                
                # endpoints
                elif "vlanport" in str(s) or "vlantag" in str(s):
                    # VLAN
                    if "value" in str(p):
                        vlan = int(o)
                        
                        # Endpoint name
                        epname = s.split("::")[1].split(":+:")[0]
                        #Wow that's messy
                    
                        # Look up switch from port name
                        ep, switchname = str(epname).split('-')
                        port = self.current_topo[switchname][ep][switchname]
                        endpoint = {}
                        endpoint['switch'] = switchname
                        endpoint['port'] = port
                        endpoint['vlan'] = vlan
                        endpoints.append(endpoint)

                # starttime and endtime
                elif "lifetime" in str(s):
                    if "start" in str(p):
                        starttime = o
                    if "end" in str(p):
                        endtime = o


        # Normalized the picked out information:
        #  - start and end times may not be selected, so select for them
        if starttime != None:
            starttime = datetime.strptime(starttime,
                                          rfc3339format)
        else:
            starttime = datetime.now().strftime(rfc3339format)

        if endtime != None:
            endtime = datetime.strptime(endtime,
                                        rfc3339format)
        else:
            endtime = MAXENDTIME
        #FIXME: Need to validate 

        # Create AWave/SDX rules for the delta information
        #  - if 2 endpoints, L2TunnelPolicy
        #  - if >2 endpoints, L2MultipointPolicy
        if len(endpoints) < 2:
            raise SenseAPIClientError("There are fewer than 2 endpoints: %s" %
                                      endpoints)
        elif len(endpoints) == 2:
            try:
                rule = {L2TunnelPolicy.get_policy_name():
                        {"starttime":starttime,
                         "endtime":endtime,
                         "srcswitch":endpoints[0]['switch'],
                         "dstswitch":endpoints[1]['switch'],
                         "srcport":endpoints[0]['port'],
                         "dstport":endpoints[1]['port'],
                         "srcvlan":endpoints[0]['vlan'],
                         "dstvlan":endpoints[1]['vlan'],
                         "bandwidth":bandwidth}}
                policy = L2TunnelPolicy(self.userid, rule)
            except Exception as e:
                self.dlogger.error(
                    "_parse_delta_addition: Error on L2TunnelPolicy creation - %s:%s:%s:%s" %
                    (starttime, endtime, bandwidth, endpoints))
                raise SenseAPIClientError(
                    "Invalid parameters for L2TunnelPolicy - %s:%s:%s:%s" %
                    (starttime, endtime, bandwidth, endpoints))

        elif len(endpoints) > 2:
            try:
                rule = {L2MultipointPolicy.get_policy_name():
                        {"starttime":starttime,
                         "endtime":endtime,
                         "bandwidth":bandwidth,
                         "endpoints":endpoints}}
                policy = L2MultipointPolicy(self.userid, rule)
            except Exception as e:
                self.dlogger.error(
                    "_parse_delta_addition: Error on L2MultipointPolicy creation - %s:%s:%s:%s" %
                    (starttime, endtime, bandwidth, endpoints))
                raise SenseAPIClientError(
                    "Invalid parameters for L2MultipointPolicy - %s:%s:%s:%s" %
                    (starttime, endtime, bandwidth, endpoints))
                
                

        # Return the new Policy
        return policy

    def _parse_delta_reduction(self, raw_reduction):
        # This is basically the same as nrmDelta.processDeltaReduction() from
        # senserm_oscars's senserm_delta.py.
        # Parses the raw_reduction, and returns back the deltaid that should be
        # cancelled.
        cancelID = ""
        gr = rdflib.Graph()
        
        try:
            result = gr.parse(data=raw_reduction, format='ttl')
            #FIXME: check the result
        except Exception as e:
            self.dlogger.error(
                "_parse_delta_reduction: Error on parsing graph: %s" % e)
            self.dlogger.error("  Reduction: %s" % raw_reduction)
            raise SenseAPIClientError("Reduction unparsable %s:%s" %
                                      (e, raw_reduction))

        for s,p,o in gr:
            if awaveurn in str(s):
                if "existsDuring" in str(s):
                    subj2 = s.split("conn+")
                    subj3 = subj2[1].split(":")
                    cancelID = subj3[0]
                    return cancelID
        return cancelID
            
    def get_delta(self, deltaid):
        ''' Get the delta.
            Returns:
              - (state, phase) - if deltaid is valid
              - (None, None) - if deltaid is invalid        
        '''
        #FIXME: does this need to exist?
        # Get from the DB based on the deltaid -
        delta = self._get_delta_by_id(deltaid)
        # If found, Pull out phase and state to return
        if delta != None:
            status = delta['status']
            phase = PHASE_RESERVED
            if status == STATUS_ACTIVATED:
                phase = PHASE_COMMITTED #FIXME?
            self.dlogger.debug("get_delta: %s %s" % (status, phase))
            return status, phase
        #FIXME: If not found, return ........
        return None, None
    
    def commit(self, deltaid):
        ''' Commits the specified deltaid.
            Returns:
              - HTTP_GOOD if everything is committed.
              - HTTP_NOT_FOUND if delta is not found.
              - HTTP_CONFLICT if delta cannot be committed.
        '''
    
        self.dlogger.debug("commit(): Attempting to commit deltaid %s" %
                           deltaid)
        # Get the delta information
        delta = self._get_delta_by_id(deltaid)
        
        # Check if still possible
        if delta == None:
            self.dlogger.debug("commit: Delta %s does not exist." % deltaid)
            return HTTP_NOT_FOUND
        rules_all_valid = True
        if not self._check_SDX_rule(delta['sdx_rule']):
            rules_all_valid = False

        # If not possible, reject, and send alternatives?
        if rules_all_valid == False:
            return HTTP_CONFLICT
            
        # If possible, Install rule
        self.dlogger.debug("commit(): Calling _install_policy")
        self._install_policy(deltaid, delta['sdx_rule'])

        return HTTP_GOOD
    
    def delete(self, deltaid):
        ''' deletes a specified deltaid.
            Returns:
              - HTTP_NO_CONTENT if successfully deleted
              - HTTP_NOT_FOUND if delta is not found
        '''
        # Does it exist?
        delta = self._get_delta_by_id(deltaid)
        if delta != None:
            # Delete deltaid from DB
            self.delta_table.delete(delta_id=deltaid)
            # If delta is installed,
            if delta['status'] == STATUS_ACTIVATED:
                self._remove_policy(delta)
            return HTTP_NO_CONTENT
        return HTTP_NOT_FOUND
    

    def _get_current_time(self):
        ''' Helper function, 
            Returns:
              - String of properly formatted time for timestamps. '''
        # Based on https://bitbucket.org/berkeleylab/sensenrm-oscars/src/d09db31aecbe7654f03f15eed671c0675c5317b5/sensenrm_cancel.py's get_time() function.
        tZERO = timedelta(0)
        class UTC(tzinfo):
          def utcoffset(self, dt):
            return tZERO
          def tzname(self, dt):
            return "UTC"
          def dst(self, dt):
            return tZERO
        utc = UTC()
        
        dt = datetime.now(utc)
        fmt_datetime = dt.strftime('%Y-%m-%dT%H:%M:%S')
        tz = dt.utcoffset()
        if tz is None:
            fmt_timezone = "+00:00"
            #fmt_timezone = "Z"
        else:
            fmt_timezone = "+00:00"
        time_iso8601 = fmt_datetime + fmt_timezone
        return time_iso8601
    
    def _get_delta_by_id(self, delta_id):
        ''' Helper function, just pulls a delta based on the ID.
            Returns:
              - None if delta id doesn't exist
              - Dictionary containing delta. See comment at top of SenseAPI 
                definition for keys. 
        '''
        raw_delta = self.delta_table.find_one(delta_id=unicode(delta_id))
        if raw_delta == None:
            return None
        
        # Unpickle the pickled values and rebuild dictionary to return
        delta = {'delta_id':raw_delta['delta_id'],
                 'raw_request':pickle.loads(str(raw_delta['raw_request'])),
                 'sdx_rule':pickle.loads(str(raw_delta['sdx_rule'])),
                 'status':raw_delta['status'],
                 'last_modified':raw_delta['last_modified'],
                 'timestamp':raw_delta['timestamp'],
                 'model_id':raw_delta['model_id'],
                 'hash':raw_delta['hash']}

        self.dlogger.debug("_get_delta_by_id() on %s successful" % delta_id)
        return delta

    def _get_delta_by_rule_hash(self, rule_hash):
        ''' Helper function, just pulls a delta based on the rule hash (from the
            RuleManager).
            Returns:
              - None if rule_hash doesn't exist
              - Dictionary containing delta. See comment at top of SenseAPI
                definition for keys.
        '''
        raw_delta = self.delta_table.find_one(hash=unicode(rule_hash))
        if raw_delta == None:
            return None
        
        # Unpickle the pickled values and rebuild dictionary to return
        delta = {'delta_id':raw_delta['delta_id'],
                 'raw_request':pickle.loads(str(raw_delta['raw_request'])),
                 'sdx_rule':pickle.loads(str(raw_delta['sdx_rule'])),
                 'status':raw_delta['status'],
                 'last_modified':raw_delta['last_modified'],
                 'timestamp':raw_delta['timestamp'],
                 'model_id':raw_delta['model_id'],
                 'hash':raw_delta['hash']}

        self.dlogger.debug("_get_delta_by_rule_hash() on %s successful" %
                           rule_hash)
        return delta

    def get_all_deltas(self):
        ''' Gets a list of all deltas and returns in the following format:
            {'id': Delta ID,
             'lastModified': Last modified time,
             'description': Not actually sure what that is,
             'modelID': model ID,
             'reduction': Reduction section of the raw_request,
             'addition': Addition section of the raw_request}
        '''

        deltas = self.delta_table.find()
        parsed_deltas = []

        if deltas == None:
            return parsed_deltas

        # Convert to Endpoint-friendly
        for delta in deltas:
            d = self._convert_delta(delta, True)
            parsed_deltas.append(d)
        return parsed_deltas

    def _convert_delta(self, delta, unpickle=False):
        ''' Helper to convert DB's form to what the endpoints are expecting. '''
        print "\n\nCONVERT_DELTA\n%s\n\n\n" % delta
        raw_request = delta['raw_request']
        if unpickle:
            raw_request = pickle.loads(str(raw_request))
        print "\n\nRAW REQUEST!\n%s\n\n" % raw_request
        reduction = raw_request['reduction']
        addition = raw_request['addition']
            
        d = {'id':delta['delta_id'],
             'lastModified':delta['last_modified'],
             'description':None,
             'modelId':delta['model_id'],
             'reduction':reduction,
             'addition':addition}
        return d
                        
    def _put_delta(self, delta_id, raw_request=None, sdx_rule=None,
                   model_id=None, status=None, hashval=None,
                   update=False):
        ''' Helper Function, just puts delta into DB. 
            Overwrites older versions for updates (when update=True). 
            status isn't required for creating: default of HTTP_CREATED will 
            be used.
            Returns Nothing.
            Raises errors.
        '''
        raw_delta = self._get_delta_by_id(delta_id)
        last_modified = self._get_current_time()
        delta = None

        self.dlogger.info("_put_delta() for delta_id %s, update = %s" %
                          (delta_id, update))
        
        # if it's a new entry (update=False)
        #   - There is no existing rule with delta_id==delta_id
        #   - Make sure everything is filled in
        #   - Build dictionary to be inserted into table, including timestamp
        #     and last_modified
        if update == False:
            if raw_delta != None:
                raise SenseAPIError(
                    "Delta with ID %s already exists" % delta_id)
            if status == None:
                status = STATUS_ACCEPTED
            if (raw_request == None or
                sdx_rule == None or
                model_id == None or
                status == None):
                raise SenseAPIError(
                    "Delta %s requires all fields (%s, %s, %s, %s)" %
                      (delta_id, raw_request, sdx_rule, model_id, status))
            delta = {'delta_id':delta_id,
                     'raw_request':pickle.dumps(raw_request),
                     'sdx_rule':pickle.dumps(sdx_rule),
                     'status':status,
                     'last_modified':last_modified,
                     'timestamp':last_modified, #Both of these will be the same
                     'model_id':model_id,
                     'hash':hashval}
            # insert dictionary into DB
            self.dlogger.debug("Inserting delta %s" % delta_id)                
            self.delta_table.insert(delta)
            
        # else, it's an update (update=True)
        #   - Make sure there is an existing rule with delta_id==delta_id
        #   - Build dictionary to be inserted into table, including
        #     last_modified
        else:
            if raw_delta == None:
                raise SenseAPIError(
                    "No delta with ID %s exists, cannot update." % delta_id)
            delta = {'delta_id':delta_id,
                     'last_modified':last_modified}
            
            rows = []
            if raw_request != None:
                delta['raw_request'] = pickle.dumps(raw_request)
                rows.append('raw_request')
            if sdx_rule != None:
                delta['sdx_rule'] = pickle.dumps(sdx_rule)
                rows.append('sdx_rule')
            if status != None:
                delta['status'] = status
                rows.append('status')
            if model_id != None:
                delta['model_id'] = model_id
                rows.append('model_id')
            if hashval != None:
                delta['hash'] = hashval
                rows.append('hash')

            if len(rows) == 0:
                raise SenseAPIError(
                    "Updates require one or more parts updated")
                                    
            self.dlogger.debug("Updating delta %s with rows %s" % (delta_id,
                                                                   rows))
            self.delta_table.update(delta, ['delta_id'])

        self.dlogger.debug("_put_delta() successful with ID %s. Update? %s" %
                           (delta_id, update))

    def _get_model_by_id(self, model_id):
        ''' Helper function, just retrieves models based on model_id.
            Returns:
              - None if model_id does not exists.
              - Dictionary containing model. See top of SenseAPI definition for
                keys.
        '''
        raw_model = self.model_table.find_one(model_id=str(model_id))
        if raw_model == None:
            return None
        
        # Unpickle the pickled values and rebuild dictionary to return
        model = {'model_id':raw_model['model_id'],
                 'model_data':raw_model['model_data'],
                 'model_raw_info':pickle.loads(str(
                     raw_model['model_raw_info'])),
                 'timestamp':raw_model['timestamp']}

        self.dlogger.debug('_get_model_by_id() on %s successful' % model_id)
        return model
    
    def _put_model(self, model_id, model_xml, model_raw_info, timestamp=None):
        ''' Helper function, just puts model into DB. No updates allowed. 
            Returns nothing.
            Raises errors.
        '''
        # Check to see if a model with model_id already exists, if so, raise
        # an error.
        if model_id == None:
            raise SenseAPIError("Model ID is necessary.")
        if self._get_model_by_id(model_id) != None:
            raise SenseAPIError("Model with ID %s already exists", model_id)
        
        # Make sure all fields are filled in
        if model_xml == None or model_raw_info == None:
            raise SenseAPIError("Model needs both model_xml and model_raw_info. (%s, %s)" %
                                (model_xml, model_raw_info))
        
        # Build dictionary to be inserted into table, including timestamp
        if timestamp == None:
            timestamp = self._get_current_time()
            
        model = {'model_id':model_id,
                 'model_data':model_xml,
                 'model_raw_info':pickle.dumps(model_raw_info),
                 'timestamp':timestamp}

        # Insert dictionary into DB
        self.dlogger.debug("Inserting model %s" % model_id)
        self.model_table.insert(model)
    
    def _find_alternative(self, deltaid):
        # Used to find alternative times/VLANs.
        #FIXME: How to do this?

        pass

    def _encode_gzip_b64(self, data):
        ''' Helper function that handles gziping then encoding into base64 
            string.
            Based on https://bitbucket.org/berkeleylab/sensenrm-oscars/src/d09db31aecbe7654f03f15eed671c0675c5317b5/sensenrm_server.py?at=master&fileviewer=file-view-default
        '''
        gzip_compress = zlib.compressobj(9, zlib.DEFLATED, zlib.MAX_WBITS | 16)
        gzipped_data = gzip_compress.compress(data) + gzip_compress.flush()
        b64_gzip_data = base64.b64encode(gzipped_data).decode()
        return b64_gzip_data

    def _decode_b64_gunzip(self, data):
        ''' Helper function that handles decoding then unzipping data.
            Based on https://bitbucket.org/berkeleylab/sensenrm-oscars/src/d09db31aecbe7654f03f15eed671c0675c5317b5/sensenrm_server.py?at=master&fileviewer=file-view-default
        '''
        try:
            unzipped_data = zlib.decompress(base64.b64decode(data),
                                        16+zlib.MAX_WBITS)
            return unzipped_data
        except Exception as e:
            self.dlogger.error("_decode_b64_gunzip() error: %s" % e)
            self.dlogger.error("   Data: %s" % data)
            raise SenseAPIB64Error("Error decoding or decompressing: %s\n%s" %
                                   (str(e), data))
    


class SenseAPIResource(Resource):
    ''' Has common pieces for all Resource objects used by the SenseAPI, 
        including logging. '''

    def __init__(self, urlbase,
                 loggeridsuffix, loggeridprefix='sdxcontroller.sense'):
        loggerid = loggeridprefix + "." + loggeridsuffix
        self._setup_loggers(loggerid)
        self.urlbase = urlbase
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
        
        

        
class ModelsAPI(SenseAPIResource):#FIXME
    def __init__(self, urlbase):
        super(ModelsAPI, self).__init__(urlbase, self.__class__.__name__)
        self.dlogger.debug("__init__() start")
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('current', type=str, default='true')
        self.reqparse.add_argument('summary', type=str, default='false')
        self.reqparse.add_argument('encode', type=str, default='false')
        self.model, newbool = SenseAPI().get_latest_model()
        self.dlogger.debug("__init__() complete")
    
    def get(self):
        self.dlogger.debug("get() start")

        retval = marshal(self.model, model_fields)
        self.logger.info("get() returning %s" % retval)
        self.dlogger.debug("get() complete")
        return retval
    
    def post(self):
        self.dlogger.debug("post() start")

        args = self.reqparse.parse_args()
        self.logger.info("post() args %s" % args)
        retval = {'models': marshal(self.models, model_fields)}, 201 #FIXME
        
        self.logger.info("post() returning %s" % retval)
        self.dlogger.debug("post() complete")
        return retval
    
class DeltasAPI(SenseAPIResource):
    def __init__(self, urlbase):
        super(DeltasAPI, self).__init__(urlbase, self.__class__.__name__)
        self.dlogger.debug("__init__() start")
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('id', type=str, location='json')
        self.reqparse.add_argument('lastModified', type=str, location='json')
        self.reqparse.add_argument('modelId', type=str, location='json')
        self.reqparse.add_argument('reduction', type=str, location='json')
        self.reqparse.add_argument('addition', type=str, location='json')
        self.deltas = SenseAPI().get_all_deltas()

        self.dlogger.debug("__init__() complete")
    
    def get(self):
        self.dlogger.debug("get() start")
        retval = {'deltas': marshal(self.deltas, delta_fields)}
        
        self.logger.info("get() returning %s" % retval)
        self.dlogger.debug("get() complete")
        return retval
    
    def post(self):
        self.dlogger.debug("post() start")

        args = self.reqparse.parse_args()
        self.logger.info("post() args %s" % args)
        deltas, mystatus = SenseAPI().process_deltas(args)
        self.logger.info("post() results %s" % mystatus)
        self.dlogger.info("post() deltas %s" % deltas)
        rstatus = HTTP_CREATED
        if int(mystatus) != HTTP_GOOD:
            rstatus = mystatus
            
        retval = {'deltas': marshal(deltas, delta_fields)}, rstatus

        self.logger.info("post() returning %s" % str(retval))
        self.logger.debug("post() complete")
        return retval
    
class DeltaAPI(SenseAPIResource):
    def __init__(self, urlbase):
        super(DeltaAPI, self).__init__(urlbase, self.__class__.__name__)
        self.dlogger.debug("__init__() start")
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('summary', type=str, default='true')
        # Removed, as deltaid is in the URL
        #self.reqparse.add_argument('deltaid', type=str, location='json')
        self.dlogger.debug("__init__() complete")
    
    def get(self, deltaid):
        self.dlogger.debug("get() start")
        self.logger.info("get() deltaid %s" % deltaid)
        status, phase = SenseAPI().get_delta(deltaid)
        self.dlogger.debug("get() %s:%s" % (status, phase))
        retval = {'state': str(phase), 'deltaid': str(deltaid)}, status
        self.logger.info("get() returning %s" % str(retval))
        self.dlogger.debug("get() complete")
        return retval

    def delete(self, deltaid):
        self.dlogger.debug("delete() start")
        self.logger.info("delete() deltaid %s" % deltaid)
        status = SenseAPI().delete(deltaid)
        retval = None
        if int(status) == HTTP_NO_CONTENT:
            retval = status
        elif int(status) == HTTP_NOT_FOUND:
            retval = {"error": "conflict",
                      "error_description": "Delta ID %s not found" % deltaid,
                      "error_uri": None} #FIXME: this should be a real URI
        else:
            retval = {"error": "%s" % status,
                      "error_description": "Failure %s" % status,
                      "error_uri": None} #FIXME: this should be a real URI

        self.logger.info("delete() returning %s" % retval)
        self.dlogger.debug("delete() complete")
        return retval

class CommitsAPI(SenseAPIResource):
    def __init__(self, urlbase):
        super(CommitsAPI, self).__init__(urlbase, self.__class__.__name__)
        self.dlogger.debug("__init__() start")
        self.dlogger.debug("__init__() complete")

    def post(self, deltaid):
        self.dlogger.debug("post() start")
        self.logger.info("post() deltaid %s" % deltaid)
        resp = SenseAPI().commit(deltaid)
        retval = {'result': True}, resp
        self.logger.info("post() returning %s" % str(retval))
        self.dlogger.debug("post() complete")
        return retval

