# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project

from UserPolicy import *
from datetime import datetime
from shared.constants import *
from shared.L2MultipointEndpointLCRule import L2MultipointEndpointLCRule
from shared.L2MultipointFloodLCRule import L2MultipointFloodLCRule

jsonstring = "l2multipoint"

class L2MultipointPolicy(UserPolicy):
    ''' This policy is for network administrators to create L2 multipoint LANs, 
        similar to MetroEthernet's E-LAN

        It requires the following information to create a tunnel:
          - Start time
          - End time
          - List of switch-port-vlan dictionaries
          - Maximum Bandwidth on a given link

        Example Json:
        {"l2multipoint":{
            "starttime":"1985-04-12T23:20:50",
            "endtime":"1985-04-12T23:20:50+0400",
            "endpoints": [ {"switch":"mia-switch", "port":5, "vlan":286},
                           {"switch":"atl-switch", "port":3, "vlan":1856},
                           {"switch":"gru-switch", "port":4, "vlan":3332} ],
            "bandwidth":1000}}
        Times are RFC3339 formated offset from UTC, if any, is after the seconds
        Bandwidth is in Mbit/sec

        Side effect of coming from JSON, everything's unicode. Need to handle 
        parsing things into the appropriate types (int, for instance).
    '''

    print jsonstring
    def __init__(self, username, json_rule):
        print 8
        self.start_time = None
        self.stop_time = None
        self.bandwidth = None
        self.endpoints = []

        # Derived values
        self.intermediate_vlan = None
        self.tree = None
        
        print 9
        super(L2MultipointPolicy, self).__init__(username,
                                                 "L2Multipoint",
                                                 json_rule)

        print 10
        # Anything specific here?
        pass

    @staticmethod
    def check_syntax(json_rule):
        try:
            # Make sure the times are the right format
            # https://stackoverflow.com/questions/455580/json-datetime-between-python-and-javascript

            starttime = datetime.strptime(json_rule[jsonstring]['starttime'],
                                         rfc3339format)
            endtime = datetime.strptime(json_rule[jsonstring]['endtime'],
                                         rfc3339format)
            bandwidth = int(json_rule[jsonstring]['bandwidth'])


            delta = endtime - starttime
            if delta.total_seconds() < 0:
                raise UserPolicyValueError("Time ends before it begins: begin %s, end %s" % (starttime, endtime))

            # Parse out the endpoints and check them individually
            for endpoint in json_rule[jsonstring]['endpoints']:
                switch = str(endpoint['switch'])
                port = int(endpoint['port'])
                vlan = int(endpoint['vlan'])

                if ((port < 0) or (port > 24)):
                    raise UserPolicyValueError("port is out of range %d: %s" %
                                               (port, str(endpoint)))
                if ((vlan < 0) or (vlan > 4090)):
                    raise UserPolicyValueError("vlan is out of range %d: %s" %
                                               (vlan, str(endpoint)))


        except e:
            raise
            
    def breakdown_rule(self, tm, ai):
        self.breakdown = []
        topology = tm.get_topology()
        authorization_func = ai.is_authorized

        # Get the tree between all nodes and reserve resources
        nodes = [d["switch"] for d in self.endpoints]
        self.tree = tm.find_valid_steiner_tree(self, nodes)
        self.intermediate_vlan = tm.find_vlan_on_tree(self.tree)
        if self.intermediate_vlan == None:
            raise UserPolicyError("There are no available VLANs on path %s for rule %s" % (self.fullpath, self))
        tm.reserve_vlan_on_path(self.fullpath, self.intermediate_vlan)
        tm.reserve_bw_on_path(self.fullpath, self.bandwidth)

        
        #nodes = topology.nodes(data=True)
        #edges = topology.edges(data=True)
        #import json
        #print "NODES:"
        #print json.dumps(nodes, indent=2)
        #print "\n\nEDGES:"
        #print json.dumps(edges, indent=2)

        # Endpoints need to have their traffic converted onto the intermediate
        # VLAN on ingress and put back onto their own VLAN on Egress. Further,
        # the end points are where we perform bandwidth limiting (if the
        # switch supports it.
        # If it's a known destination, the learning switch functionality will
        # take care of forwarding (see LearnedDestinationPolicy.py for details).
        # For Unknown Destinations, however it's more difficult. This is where
        # the tree comes in. We flood along the tree, and on the return path,
        # the new destination will become known, then will forward directly.
        
        covered_nodes = []
        # Endpoints
        for (node, port, vlan) in self.endpoints:
            if node in covered_nodes:
                continue
            location = node
            shortname = topology.node[location]['locationshortname']
            switch_id = topology.node[location]['dpid']
            intermediate_vlan = self.intermediate_vlan
            bandwidth = self.bandwidth
            flooding_ports = []
            endpoint_ports_and_vlans = []

            # for endpoint ports, add to endpoint_ports_and_vlans and
            # covered_endpoints
            endpoint_ports_and_vlans = [(d['port'],d['vlan']) for
                                         d in self.endpoints
                                         if d['switch'] == node]
            endpoint_ports = [d['port'] for d in self.endpoints
                              if d['switch'] == node]
            # for non-endpoint ports, add to flooding_ports
            connected_ports = []
            for neighbor in topology.neighbors(node):
                # edge[node][neighbor] gets the edge structure, the [node] at the
                # end gives us the port on 'node'. Replacing it with [neighbor]
                # would give us the port on 'neighbor'.
                connected_ports.append(topology.edge[node][neighbor][node])
            for p in connected_ports:
                if p in endpoint_ports:
                    continue
                flooding_ports.append(port)
    
            # Make breakdown
            bd = UserPolicyBreakdown(shortname, [])

            rule = L2MultipointEndpointLCRule(switch_id, flooding_ports,
                                              endpoints_ports_and_vlans,
                                              intermediate_vlan, bandwidth)

            bd.add_to_list_of_rules(rule)
            self.breakdown.append(bd)
            covered_nodes.append(node)

        # Interior nodes
        for node in self.tree.nodes():
            # Endpoint nodes can be skipped
            if node in covered_nodes:
                continue 
            location = node
            shortname = topology.node[location]['locationshortname']
            switch_id = topology.node[location]['dpid']
            intermediate_vlan = self.intermediate_vlan
            flooding_ports = []

            # Flooding ports are all ports on the Steiner Tree (which is a subset
            # of the full topology)
            for neighbor in self.tree.neighbors():
                flooding_ports.append(topology.edge[node][neighbor][node])

            # Make breakdown
            bd = UserPolicyBreakdown(shortname, [])

            rule = L2MultpointFloodLCRule(switch_id, flooding_ports,
                                          intermediate_vlan)

            bd.add_to_list_of_rules(rule)
            self.breakdown.append(bd)
            covered_nodes.append(node)
        
        # Return the breakdown, now that we've finished.
        return self.breakdown

    
    def check_validity(self, tm, ai):
        #FIXME: This is going to be skipped for now, as we need to figure out what's authorized and what's not.
        return True

    def _parse_json(self, json_rule):
        if type(json_rule) is not dict:
            raise UserPolicyTypeError("json_rule is not a dictionary:\n    %s" % json_rule)
        if jsonstring not in json_rule.keys():
            raise UserPolicyValueError("%s value not in entry:\n    %s" % ('rules', json_rule))        

        self.start_time = json_rule['l2tunnel']['starttime']
        self.stop_time =  json_rule['l2tunnel']['endtime']
        self.bandwidth = int(json_rule['l2tunnel']['bandwidth'])
        # Make sure end is after start and after now.
        #FIXME

        for endpoint in json_rule[jsonstring]['endpoints']:
                switch = str(endpoint['switch'])
                port = int(endpoint['port'])
                vlan = int(endpoint['vlan'])
                #FIXME: Verifications? This is implemented so that it's easy to
                #add verification, not for ease of filling out self.endpoints
                self.endpoints.append({"switch":switch,
                                       "port":port,
                                       "vlan":vlan})


        #FIXME: Really need some type verifications here.
    
        
    
    def pre_add_callback(self, tm, ai):
        ''' This is called before a rule is added to the database. For instance,
            if certain resources need to be locked down or rules authorized,
            this can do it. May not need to be implemented. '''
        pass

    def pre_remove_callback(self, tm, ai):
        ''' This is called before a rule is removed from the database. For 
            instance, if certain resources need to be released, this can do it.
            May not need to be implemented. '''
        # Release VLAN and BW in use
        tm.unreserve_vlan_on_path(self.fullpath, self.intermediate_vlan)
        tm.unreserve_bw_on_path(self.fullpath, self.bandwidth)
        




