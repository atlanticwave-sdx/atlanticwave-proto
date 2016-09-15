# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


from UserPolicy import *
from datetime import datetime
import networkx as nx

# For building rules, may need to change in the future with a better intermediary
from shared.offield import *
from shared.match import *
from shared.action import *
from shared.instruction import *
from shared.OpenFlowRule import * 


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
        Times are RFC3339 formated offset from UTC, if any, is after the seconds.
        Bandwidth is in Mbit/sec

        Side effect of coming from JSON, everything's unicode. Need to handle 
        parsing things into the appropriate types (int, for instance).
    '''

    def __init__(self, username, json_rule):
        self.start_time = None
        self.end_time = None
        self.src_switch = None
        self.dst_switch = None
        self.src_port = None
        self.dst_port = None
        self.src_vlan = None
        self.dst_vlan = None
        self.bandwidth = None
        super(L2TunnelPolicy, self).__init__(username, json_rule)

        # Anything specific here?
        pass

    @staticmethod
    def check_syntax(json_rule):
        try:
            rfc3339format = "%Y-%m-%dT%H:%M:%S%z"
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
            bandwidth = json_rule['l2tunnel']['bandwidth']

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
            
    def breakdown_rule(self, topology, authorization_func):
        self.breakdown = []
        # Get a path from the src_switch to the dst_switch form the topology
        #FIXME: This needs to be updated to get *multiple* options
        fullpath = nx.shortest_path(topology,
                                    source=self.src_switch,
                                    target=self.dst_switch)
        nodes = topology.nodes(data=True)
        edges = topology.edges(data=True)

        import json
        print "NODES:"
        print json.dumps(nodes, indent=2)
        print "\n\nEDGES:"
        print json.dumps(edges, indent=2)
        
        # Get a VLAN to use
        #FIXME: how to figure this out? Do we need better access to the topology manager?
        intermediate_vlan = self.src_vlan

        # Special case: Single node:
        if len(fullpath) == 1:
            if (self.src_switch != self.dst_switch):
                raise UserPolicyValueError("Path length is 1, but switches are different: fullpath %s, src_switch %s, dst_switch %s" % (fullpath, src_switch, dst_switch))
                
            location = self.src_switch
            switch_id = topology.node[location]['dpid']
            inport = self.src_port
            outport = self.dst_port
            invlan = self.src_vlan
            outvlan = self.dst_vlan

            priority = 100 #FIXME
            cookie = 1234 #FIXME
            table = 0 #FIXME

            bd =  UserPolicyBreakdown(topology.node[location]['lcip'])

            # Inbound
            match = OpenFlowMatch([IN_PORT(inport),
                                   VLAN_VID(invlan)])
            actions = [action_OUTPUT(outport),
                       action_SET_FIELD(VLAN_VID(outvlan))]
            instruction = instruction_WRITE_ACTIONS(actions)
            rule = OpenFlowRule(match, instruction, table,
                                priority, cookie, switch_id)
            bd.add_to_list_of_rules(rule)

            # Outbound
            match = OpenFlowMatch([IN_PORT(outport),
                                   VLAN_VID(outvlan)])
            actions = [action_OUTPUT(inport),
                       action_SET_FIELD(VLAN_VID(invlan))]
            instruction = instruction_WRITE_ACTIONS(actions)
            rule = OpenFlowRule(match, instruction, table,
                                priority, cookie, switch_id)
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
        srcpath = fullpath[1]   # Next one after src
        dstpath = fullpath[-2]  # One prior to dst
        for location, inport, invlan, path in [(self.src_switch, self.src_port,
                                                self.src_vlan, srcpath),
                                               (self.dst_switch, self.dst_port,
                                                self.dst_vlan, dstpath)]:
            bd =  UserPolicyBreakdown(topology.node[location]['lcip'])
            switch_id = topology.node[location]['dpid']
            priority = 100 #FIXME
            cookie = 1234 #FIXME
            table = 0 #FIXME

            # get edge
            edge = topology.edge[location][path]
            outport = edge[path]

            # Inbound
            match = OpenFlowMatch([IN_PORT(inport),
                                   VLAN_VID(invlan)])
            actions = [action_OUTPUT(outport),
                       action_SET_FIELD(VLAN_VID(intermediate_vlan))]
            instruction = instruction_WRITE_ACTIONS(actions)
            rule = OpenFlowRule(match, instruction, table,
                                priority, cookie, switch_id)
            bd.add_to_list_of_rules(rule)

            # Outbound
            match = OpenFlowMatch([IN_PORT(outport),
                                   VLAN_VID(intermediate_vlan)])
            actions = [action_OUTPUT(inport),
                       action_SET_FIELD(VLAN_VID(invlan))]
            instruction = instruction_WRITE_ACTIONS(actions)
            rule = OpenFlowRule(match, instruction, table,
                                priority, cookie, switch_id)
            bd.add_to_list_of_rules(rule)
            self.breakdown.append(bd)
        
        
        # Loop through the intermediary nodes in the path. Python's smart, so
        # the slicing that's happening just works, even if there are only two
        # locations in the path. Magic!
        for (prevnode, node, nextnode) in zip(fullpath[0:-2], 
                                              fullpath[1:-1], 
                                              fullpath[2:]):
            # Need inbound and outbound rules for the VLAN that's being used,
            # Don't need to modify packet.
            #  - on inbound, match on the switch, port, and intermediate VLAN
            #               action set fwd
            #  - on outbound, match on the switch, port, and intermediate VLAN
            #               action set fwd
            bd =  UserPolicyBreakdown(topology.node[location]['lcip'])

            switch_id = topology.node[location]['dpid']
            priority = 100 #FIXME
            cookie = 1234 #FIXME
            table = 0 #FIXME

            # get edges
            prevedge = topology.node[location][prevnode]
            nextedge = topology.node[location][nextnode]

            for inport, outport in [(prevedge[node], prevedge[prevnode]),
                                    (nextedge[node], nextedge[nextnode])]:
                # Inbound
                match = OpenFlowMatch([IN_PORT(inport),
                                       VLAN_VID(intermediate_vlan)])
                actions = [action_OUTPUT(outport)]
                instruction = instruction_WRITE_ACTIONS(actions)
                rule = OpenFlowRule(match, instruction, table,
                                    priority, cookie, switch_id)
                bd.add_to_list_of_rules(rule)

                # Outbound
                match = OpenFlowMatch([IN_PORT(outport),
                                       VLAN_VID(intermediate_vlan)])
                actions = [action_OUTPUT(inport)]
                instruction = instruction_WRITE_ACTIONS(actions)
                rule = OpenFlowRule(match, instruction, table,
                                    priority, cookie, switch_id)
                bd.add_to_list_of_rules(rule)

            # Add the four new rules created above to the breakdown
            self.breakdown.append(bd)
            

        return self.breakdown

    
    def check_validity(self, topology, authorization_func):
        #FIXME: This is going to be skipped for now, as we need to figure out what's authorized and what's not.
        return True

    def _parse_json(self, json_rule):
        if type(json_rule) is not dict:
            raise UserPolicyTypeError("json_rule is not a dictionar:y\n    %s" % json_rule)
        if 'l2tunnel' not in json_rule.keys():
            raise UserPolicyValueError("%s value not in entry:\n    %s" % ('rules', json_rule))        

        # Borrowing parsing from:
        # https://stackoverflow.com/questions/455580/json-datetime-between-python-and-javascript
        rfc3339format = "%Y-%m-%dT%H:%M:%S"
        self.start_time = datetime.strptime(json_rule['l2tunnel']['starttime'],
                                            rfc3339format)
        self.end_time =   datetime.strptime(json_rule['l2tunnel']['endtime'],
                                            rfc3339format)
        # Make sure end is after start and after now.
        #FIXME

        self.src_switch = json_rule['l2tunnel']['srcswitch']
        self.dst_switch = json_rule['l2tunnel']['dstswitch']
        self.src_port = json_rule['l2tunnel']['srcport']
        self.dst_port = json_rule['l2tunnel']['dstport']
        self.src_vlan = json_rule['l2tunnel']['srcvlan']
        self.dst_vlan = json_rule['l2tunnel']['dstvlan']
        self.bandwidth = json_rule['l2tunnel']['bandwidth']

        #FIXME: Really need some type verifications here.
    
        
        





