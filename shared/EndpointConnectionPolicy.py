# Copyright 2017 - Sean Donovan
# AtlanticWave/SDX Project


from UserPolicy import *
from L2TunnelPolicy import *
from datetime import datetime
import networkx as nx
from shared.constants import *
from math import ceil


class EndpointConnectionPolicy(UserPolicy):
    ''' This policy is for connecting endpoints easily via L2 tunnels. It it 
        based on the L2TunnelPolicy, but requires less information provided by
        the user.

        It requires the following information to create a connection:
          - Deadline
          - Src endpoint
          - Dst endpoint
          - Data-Quantity

        Internally, we care about start time, end time, and bandwidth, however 
        this may not be something that a domain scientists will understand or
        care about. As such, translating from their external representation to
        what we care about is easy: some division and adjusting for some leeway
        will determine an end time.
   
        FIXME: Should this be more generous in options? That is, if the users
        actually know what the start and end times should, allow them to create
        those? 
   
        FIXME: Recurrant items too!

        Example Json:
        {"endpointconnection":{
            "deadline":"1985-04-12T23:20:50",
            "srcendpoint":"atlh1",
            "dstendpoint":"miah2",
            "dataquantity":57000000000}}
        Time is RFC3339 formated offset from UTC, if any, is after the seconds
        dataquantity is number of bytes that need to be transferred, so ~57GB
          is seen here.

        Side effect of coming from JSON, everything's unicode. Need to handle 
        parsing things into the appropriate types (int, for instance).    
    '''
    rulename = 'endpointconnection'
    buffer_time_sec = 300
    buffer_bw_percent = 1.05

    def __init__(self, username, json_rule):
        # From JSON
        self.deadline = None
        self.src = None
        self.dst = None
        self.data = None


        # Derived values:
        self.bandwidth = None
        self.intermediate_vlan = None
        self.fullpath = None

        super(EndpointConnectionPolicy, self).__init__(username,
                                                       "EndpointConnection",
                                                       json_rule)

        print "Passed: %s:%s:%s:%s:%s:%s:%s" % (self.deadline,
                                                self.src,
                                                self.dst,
                                                self.data,
                                                self.bandwidth,
                                                self.intermediate_vlan,
                                                self.fullpath)
        # Second
        pass

    @staticmethod
    def check_syntax(json_rule):
        try:
            deadline = datetime.strptime(json_rule[EndpointConnectionPolicy.rulename]['deadline'],
                                         rfc3339format)
            src = json_rule[EndpointConnectionPolicy.rulename]['srcendpoint']
            dst = json_rule[EndpointConnectionPolicy.rulename]['dstendpoint']
            data = json_rule[EndpointConnectionPolicy.rulename]['dataquantity']

            if type(data) != int:
                raise UserPolicyTypeError("data is not an int: %s:%s" %
                                          (str(data), type(data)))
            #FIXME: checking on src and dst to see if they're strings?
        except e:
            raise

    def breakdown_rule(self, tm, ai):
        # There is a lot of logic borrowed from L2TunnelPolicy's version of
        # breakdown_rule, but there are some significant differences.
        self.breakdown = []
        topology = tm.get_topology()
        authorization_func = ai.is_authorized
        
        # First, find out the bandwidth requirements
        total_time = (datetime.strptime(self.deadline, rfc3339format) - 
                  datetime.now()).total_seconds()
        if total_time == EndpointConnectionPolicy.buffer_time_sec or total_time == 0:
            # This adjustment is to prevent 0 denominators in the next formulas
            total_time += 1
            
        self.bandwidth = int(ceil(max(self.data/(total_time - EndpointConnectionPolicy.buffer_time_sec),
                                      (self.data/total_time)*EndpointConnectionPolicy.buffer_bw_percent)))

        # Second, get the path, and reserve bw and a VLAN on it
        self.fullpath = tm.find_valid_path(self.src, self.dst, self.bandwidth)
        if self.fullpath == None:
            raise UserPolicyError("There is no available path between %s and %s for bandwidth %s" % (self.src, self.dst, self.bandwidth))
        # Switchpath is the path between endpoint switches. self.src and
        # self.dst are hosts, not switches, so they're not useful for certain
        # things.
        self.switchpath = self.fullpath[1:-1]

        self.intermediate_vlan = tm.find_vlan_on_path(self.switchpath)
        if self.intermediate_vlan == None:
            raise UserPolicyError("There are no available VLANs on path %s for rule %s" % (self.fullpath, self))
            
        # We reserve the VLAN on all points *except* the end points, as the
        # endpoints have their own VLAN. Reserver the BW on the full path,
        # however
        tm.reserve_vlan_on_path(self.switchpath, self.intermediate_vlan)
        tm.reserve_bw_on_path(self.fullpath, self.bandwidth)
        
        # Third, build the breakdown rules for the path.
        # This section is heavily based on the L2TunnelPolicy.breakdown_rule()

        # Single switch case:
        if len(self.switchpath) == 1:
            location = self.switchpath[0]
            shortname = topology.node[location]['locationshortname']
            switch_id = topology.node[location]['dpid']
            inedge  = topology.edge[location][self.src]
            outedge = topology.edge[location][self.dst]
            inport  = inedge[location]
            outport = outedge[location]
            invlan  = topology.node[self.src]['vlan']
            outvlan = topology.node[self.dst]['vlan']
            bandwidth = self.bandwidth

            bd = UserPolicyBreakdown(shortname, [])

            rule = VlanTunnelLCRule(switch_id, inport, outport, invlan, outvlan,
                                    True, bandwidth)
            bd.add_to_list_of_rules(rule)
            self.breakdown.append(bd)
            return self.breakdown



        # Multi-switch case, endpoints:
        src_switch = self.switchpath[0]
        dst_switch = self.switchpath[-1]
        src_edge = topology.edge[src_switch][self.src]
        dst_edge = topology.edge[dst_switch][self.dst]
        src_port = src_edge[src_switch]
        dst_port = dst_edge[dst_switch]
        src_vlan = int(topology.node[self.src]['vlan'])
        dst_vlan = int(topology.node[self.dst]['vlan'])
        srcpath = self.switchpath[1]
        dstpath = self.switchpath[-2]
        for location, inport, invlan, path in [(src_switch, src_port,
                                                src_vlan, srcpath),
                                               (dst_switch, dst_port,
                                                dst_vlan, dstpath)]:
            shortname = topology.node[location]['locationshortname']
            switch_id = topology.node[location]['dpid']
            bandwidth = self.bandwidth
            
            bd = UserPolicyBreakdown(shortname, [])

            # get edge
            edge = topology.edge[location][path]
            outport = edge[location]


            rule = VlanTunnelLCRule(switch_id, inport, outport, 
                                    invlan, self.intermediate_vlan,
                                    True, bandwidth)

            bd.add_to_list_of_rules(rule)

            self.breakdown.append(bd)

        # Multi-switch case, midpoints:
        for (prevnode, node, nextnode) in zip(self.switchpath[0:-2],
                                              self.switchpath[1:-1],
                                              self.switchpath[2:]):

            shortname = topology.node[node]['locationshortname']
            switch_id = topology.node[node]['dpid']
            bandwidth = self.bandwidth

            bd = UserPolicyBreakdown(shortname, [])

            # get edges
            prevedge = topology.edge[prevnode][node]
            nextedge = topology.edge[node][nextnode]

            inport = prevedge[node]
            outport = nextedge[node]

            rule = VlanTunnelLCRule(switch_id, inport, outport,
                                    self.intermediate_vlan,
                                    self.intermediate_vlan,
                                    True, bandwidth)            

            bd.add_to_list_of_rules(rule)

            # Add the four new rules created above to the breakdown
            self.breakdown.append(bd)
        
        # Return the breakdown, now that we've finished.
        return self.breakdown


    def check_validity(self, topology, authorization_func):
        #FIXME: This is going to be skipped for now, as we need to figure out what's authorized and what's not.
        return True

    def _parse_json(self, json_rule):
        if type(json_rule) is not dict:
            raise UserPolicyTypeError("json_rule is not a dictionary:\n    %s" % json_rule)
        if EndpointConnectionPolicy.rulename not in json_rule.keys():
            raise UserPolicyValueError("%s value not in entry:\n    %s" % ('rules', json_rule))        

        self.deadline = str(json_rule[EndpointConnectionPolicy.rulename]['deadline'])
        self.src = str(json_rule[EndpointConnectionPolicy.rulename]['srcendpoint'])
        self.dst = str(json_rule[EndpointConnectionPolicy.rulename]['dstendpoint'])
        self.data = int(json_rule[EndpointConnectionPolicy.rulename]['dataquantity'])




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
        tm.unreserve_vlan_on_path(self.switchpath, self.intermediate_vlan)
        tm.unreserve_bw_on_path(self.fullpath, self.bandwidth)
        
