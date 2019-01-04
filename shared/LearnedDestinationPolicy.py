# Copyright 2017 - Sean Donovan
# AtlanticWave/SDX Project


from UserPolicy import *
from datetime import datetime
from shared.constants import *
from LearnedDestinationLCRule import *
import networkx as nx

class LearnedDestinationPolicy(UserPolicy):
    ''' This policy is for a distributed learning switch model. Traditional 
        OpenFlow learning switches involve a surprising amount of forwarding to
        the controller. At 100Gbps, this is simply too much. As such, we've 
        created a learning switch model that minimizes the amount of traffic 
        forwarded. Part of this is to create paths between endpoints easily.

        LearnedDestinationPolicy is the mechanism for when there is a known path
        and this will represent the connection between two given endpoints.

        It requires the following information to create a learned destination:
          - Dst Switch
          - Dst Port 
          - Dst Address

        Example Json:
        {"LearnedDestination":{
            "dstswitch":"mia-switch",
            "dstport":7,
            "dstaddress":"aa:bb:cc:dd:ee:ff"}}

        Dst Address is the destination address. Currently, using MAC address, but
        could be changed to use an IP address.        

        Side effect of coming from JSON, everything's unicode. Need to handle 
        parsing things into the appropriate types (int, for instance).
    '''

    def __init__(self, username, json_rule):
        self.dst_switch = None
        self.dst_port = None
        self.dst_address = None

        super(LearnedDestinationPolicy, self).__init__(username,
                                                       json_rule)

        # Anything specific here?
        pass

    def __str__(self):
        return "%s(%s,%s,%s)" % (self.get_policy_name(), self.dst_switch,
                                 self.dst_port, self.dst_address)

    
    @classmethod
    def check_syntax(cls, json_rule):
        try:
            # Make sure the times are the right format
            # https://stackoverflow.com/questions/455580/json-datetime-between-python-and-javascript
            jsonstring = cls.get_policy_name()
            dst_switch = json_rule[jsonstring]['dstswitch']
            dst_port = int(json_rule[jsonstring]['dstport'])
            dst_address = json_rule[jsonstring]['dstaddress']

            if ((dst_port < 0) or
                (dst_port > 24)):
                raise UserPolicyValueError("dst_port is out of range %d" %
                                           dst_port)
        except Exception as e:
            import os
            exc_type, exc_obj, exc_tb = sys.exc_info()
            filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            lineno = exc_tb.tb_lineno
            print "%s: Exception %s at %s:%d" % (self.get_policy_name(),
                                                 filename,lineno)
            raise
            
    def breakdown_rule(self, tm, ai):
        ''' This is a bit complicated, so a bit of explanation first.
            To break down this rule, we need to install rules into all switches
            that forward to our destination address using shortest paths. To do
            this, we'll need to get a list of all switches, and then start 
            creating paths. As we create paths, they will also cover *other*
            switches, so we won't have to actually go through the process for 
            those other switches of determing shortest paths and creating 
            duplicate rules.
              - Get list of switches, create (empty) list of switches covered
              - For switch in switches:
                - If in list of covered switches, skip
                - Else, find shortest path
                - for each node along path, 
                    - see if that switch is in list of switches covered. If it 
                      is on the list, skip
                    - else, create and add rule to list of rules, and add switch
                      to list of covered switches
        '''
        self.breakdown = []
        topology = tm.get_topology()
        authorization_func = ai.is_authorized
        switches = []
        for (name, data) in topology.nodes(data=True):
            if data['type'] == "switch":
                switch = data
                switch['name'] = name
                switches.append(switch)
        covered = []

        for sw in switches:
            node = sw['name']
            switch_id = topology.node[node]['dpid']
            shortname = topology.node[node]['locationshortname']
            bd = UserPolicyBreakdown(shortname, [])

            # Special case: destination switch
            if node == self.dst_switch:
                lcr = LearnedDestinationLCRule(switch_id,
                                               self.dst_address,
                                               self.dst_port)
                bd.add_to_list_of_rules(lcr)
                self.breakdown.append(bd)
                covered.append(node)
                continue

            # All other switches
            path = nx.shortest_path(topology,
                                    source=node,
                                    target=self.dst_switch)
            next_node = path[1]

            out_port = topology.edge[node][next_node][node]
            lcr = LearnedDestinationLCRule(switch_id,
                                           self.dst_address,
                                           out_port)
            bd.add_to_list_of_rules(lcr)
            self.breakdown.append(bd)
            covered.append(node)

        # Return the breakdown, now that we've finished.
        return self.breakdown

    
    def check_validity(self, tm, ai):
        #FIXME: This is going to be skipped for now, as we need to figure out what's authorized and what's not.
        return True

    def _parse_json(self, json_rule):
        jsonstring = self.ruletype
        if type(json_rule) is not dict:
            raise UserPolicyTypeError("json_rule is not a dictionary:\n    %s" % json_rule)
        if jsonstring not in json_rule.keys():
            raise UserPolicyValueError("%s value not in entry:\n    %s" % ('rules', json_rule))        

        self.dst_switch = str(json_rule[jsonstring]['dstswitch'])
        self.dst_port = int(json_rule[jsonstring]['dstport'])
        self.dst_address = str(json_rule[jsonstring]['dstaddress'])

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

        pass

        




