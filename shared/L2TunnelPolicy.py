# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


from UserPolicy import *
from datetime import datetime
from shared.constants import *
from shared.VlanTunnelLCRule import VlanTunnelLCRule


class L2TunnelPolicy(UserPolicy):
    ''' This policy is for network administrators to create L2 tunnels, similar 
        to NSI tunnels.
        It requires the following information to create a tunnel:
          - Start time
          - End time
          - Src Switch
          - Dst Switch
          - Src Port
          - Dst Port 
          - Src VLAN
          - Dst VLAN
          - Bandwidth

        Example Json:
        {"l2tunnel":{
            "starttime":"1985-04-12T23:20:50",
            "endtime":"1985-04-12T23:20:50+0400",
            "srcswitch":"atl-switch",
            "dstswitch":"mia-switch",
            "srcport":5,
            "dstport":7,
            "srcvlan":1492,
            "dstvlan":1789,
            "bandwidth":1}}
        Times are RFC3339 formated offset from UTC, if any, is after the seconds
        Bandwidth is in Mbit/sec

        Side effect of coming from JSON, everything's unicode. Need to handle 
        parsing things into the appropriate types (int, for instance).
    '''

    def __init__(self, username, json_rule):
        self.start_time = None
        self.stop_time = None
        self.src_switch = None
        self.dst_switch = None
        self.src_port = None
        self.dst_port = None
        self.src_vlan = None
        self.dst_vlan = None
        self.bandwidth = None

        # Derived values
        self.intermediate_vlan = None
        self.fullpath = None
        
        super(L2TunnelPolicy, self).__init__(username, "L2Tunnel", json_rule)

        # Anything specific here?
        pass

    @staticmethod
    def check_syntax(json_rule):
        try:
            # Make sure the times are the right format
            # https://stackoverflow.com/questions/455580/json-datetime-between-python-and-javascript

            starttime = datetime.strptime(json_rule['l2tunnel']['starttime'],
                                         rfc3339format)
            endtime = datetime.strptime(json_rule['l2tunnel']['endtime'],
                                         rfc3339format)
            src_switch = json_rule['l2tunnel']['srcswitch']
            dst_switch = json_rule['l2tunnel']['dstswitch']
            src_port = int(json_rule['l2tunnel']['srcport'])
            dst_port = int(json_rule['l2tunnel']['dstport'])
            src_vlan = int(json_rule['l2tunnel']['srcvlan'])
            dst_vlan = int(json_rule['l2tunnel']['dstvlan'])
            bandwidth = int(json_rule['l2tunnel']['bandwidth'])

            delta = endtime - starttime
            if delta.total_seconds() < 0:
                raise UserPolicyValueError("Time ends before it begins: begin %s, end %s" % (starttime, endtime))

            if ((src_port < 0) or
                (src_port > 24)):
                raise UserPolicyValueError("src_port is out of range %d" %
                                           src_port)
            if ((dst_port < 0) or
                (dst_port > 24)):
                raise UserPolicyValueError("dst_port is out of range %d" %
                                           dst_port)
            if ((src_vlan < 0) or
                (src_vlan > 4090)):
                raise UserPolicyValueError("src_vlan is out of range %d" %
                                           src_vlan)
            if ((dst_vlan < 0) or
                (dst_vlan > 4090)):
                raise UserPolicyValueError("src_vlan is out of range %d" %
                                           src_vlan)            

        except e:
            raise
            
    def breakdown_rule(self, tm, ai):
        self.breakdown = []
        topology = tm.get_topology()
        authorization_func = ai.is_authorized
        # Get a path from the src_switch to the dst_switch form the topology
        #FIXME: This needs to be updated to get *multiple* options
        self.fullpath = tm.find_valid_path(self.src_switch,
                                           self.dst_switch,
                                           self.bandwidth)
        if self.fullpath == None:
            raise UserPolicyError("There is no available path between %s and %s for bandwidth %s" % (self.src_switch, self.dst_switch, self.bandwidth))

        #nodes = topology.nodes(data=True)
        #edges = topology.edges(data=True)
        #import json
        #print "NODES:"
        #print json.dumps(nodes, indent=2)
        #print "\n\nEDGES:"
        #print json.dumps(edges, indent=2)
        
        # Get a VLAN to use
        # Topology manager should be able to provide this for us. 
        self.intermediate_vlan = tm.find_vlan_on_path(self.fullpath)
        if self.intermediate_vlan == None:
            raise UserPolicyError("There are no available VLANs on path %s for rule %s" % (self.fullpath, self))
        tm.reserve_vlan_on_path(self.fullpath, self.intermediate_vlan)
        tm.reserve_bw_on_path(self.fullpath, self.bandwidth)

        # Special case: Single node:
        if len(self.fullpath) == 1:
            if (self.src_switch != self.dst_switch):
                raise UserPolicyValueError("Path length is 1, but switches are different: fullpath %s, src_switch %s, dst_switch %s" % (self.fullpath, src_switch, dst_switch))
                
            location = self.src_switch
            shortname = topology.node[location]['locationshortname']
            switch_id = topology.node[location]['dpid']
            inport = self.src_port
            outport = self.dst_port
            invlan = self.src_vlan
            outvlan = self.dst_vlan
            bandwidth = self.bandwidth

            bd = UserPolicyBreakdown(shortname, [])

            rule = VlanTunnelLCRule(switch_id, inport, outport, invlan, outvlan,
                                    True, bandwidth)
            bd.add_to_list_of_rules(rule)
            self.breakdown.append(bd)
            return self.breakdown

        
        # Create breakdown rule for this node

        # First and last are different, due to the VLAN translation necessary
        # on the outbound path, handle them separately.
        #  - on inbound, match on the switch, port, and local VLAN
        #               action set VLAN to intermediate, fwd
        #  - on outbound, match on the switch, port, intermediate VLAN
        #               action set VLAN to local VLAN, fwd
        srcpath = self.fullpath[1]   # Next one after src
        dstpath = self.fullpath[-2]  # One prior to dst
        for location, inport, invlan, path in [(self.src_switch, self.src_port,
                                                self.src_vlan, srcpath),
                                               (self.dst_switch, self.dst_port,
                                                self.dst_vlan, dstpath)]:
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
        
        
        # Loop through the intermediary nodes in the path. Python's smart, so
        # the slicing that's happening just works, even if there are only two
        # locations in the path. Magic!
        for (prevnode, node, nextnode) in zip(self.fullpath[0:-2], 
                                              self.fullpath[1:-1], 
                                              self.fullpath[2:]):
            # Need inbound and outbound rules for the VLAN that's being used,
            # Don't need to modify packet.
            #  - on inbound, match on the switch, port, and intermediate VLAN
            #               action set fwd
            #  - on outbound, match on the switch, port, and intermediate VLAN
            #               action set fwd
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

    
    def check_validity(self, tm, ai):
        #FIXME: This is going to be skipped for now, as we need to figure out what's authorized and what's not.
        return True

    def _parse_json(self, json_rule):
        if type(json_rule) is not dict:
            raise UserPolicyTypeError("json_rule is not a dictionary:\n    %s" % json_rule)
        if 'l2tunnel' not in json_rule.keys():
            raise UserPolicyValueError("%s value not in entry:\n    %s" % ('rules', json_rule))        

        self.start_time = json_rule['l2tunnel']['starttime']
        self.stop_time =  json_rule['l2tunnel']['endtime']
        # Make sure end is after start and after now.
        #FIXME

        self.src_switch = str(json_rule['l2tunnel']['srcswitch'])
        self.dst_switch = str(json_rule['l2tunnel']['dstswitch'])
        self.src_port = int(json_rule['l2tunnel']['srcport'])
        self.dst_port = int(json_rule['l2tunnel']['dstport'])
        self.src_vlan = int(json_rule['l2tunnel']['srcvlan'])
        self.dst_vlan = int(json_rule['l2tunnel']['dstvlan'])
        self.bandwidth = int(json_rule['l2tunnel']['bandwidth'])

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
        




