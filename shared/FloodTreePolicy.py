from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals
# Copyright 2017 - Sean Donovan
# AtlanticWave/SDX Project


from builtins import str
from UserPolicy import *
from FloodTreeLCRule import *
import networkx as nx


class FloodTreePolicy(UserPolicy):
    ''' This policy is for creating a tree for broadcast flooding. A spanning
        tree is used for broadcasting, to avoid a) excessive rules, b) 
        controller intervention.

        It requires no information.

        Example Json:
        {"FloodTreePolicy":None}

    '''

    def __init__(self, username, json_rule):
        super(FloodTreePolicy, self).__init__(username,
                                              json_rule)

        # Anythign specific here?
        pass

    def __str__(self):
        return "%s()" % (self.get_policy_name())
    
    @classmethod
    def check_syntax(cls, json_rule):
        try:
            value = json_rule[cls.get_policy_name()]
            if value != None or value != [] or value != {}:
                raise UserPolicyValueError("value json_rule should be None, [], or {}, not %s." % value)
        except Exception as e:
            import os,sys
            exc_type, exc_obj, exc_tb = sys.exc_info()
            filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            lineno = exc_tb.tb_lineno
            print("%s: Exception %s at %s:%d" % (cls.get_policy_name(),
                                                 str(e), filename,lineno))
            raise

    def breakdown_rule(self, tm, ai):
        ''' This is where everything interesting happens. It creates a spanning 
            tree, and takes all the connected ports in the tree, puts them into
            a FloodTreeLCRule. The LC will use the ports to set up appropriate 
            flooding rules.
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
        
        spanning_tree = nx.minimum_spanning_tree(topology)
        
        # For each switch, create an LC rule 
        for switch in switches:
            node = switch['name']
            shortname = topology.node[node]['locationshortname']
            dpid = topology.node[node]['dpid']
            ports = []
            # Get the port on each edge
            for neighbor in spanning_tree.neighbors(node):
                ports.append(spanning_tree[node][neighbor][node])
            
            # Make breakdown
            bd = UserPolicyBreakdown(shortname, [])
            
            rule = FloodTreeLCRule(dpid, ports)
            bd.add_to_list_of_rules(rule)
            self.breakdown.append(bd)

        return self.breakdown

    def check_validity(self, tm, ai):
        #FIXME: This is going to be skipped for now, as we need to figure out what's authorized and what's not.
        return True

    def _parse_json(self, json_rule):
        if type(json_rule) is not dict:
            raise UserPolicyTypeError("json_rule is not a dictionary:\n    %s" % json_rule)
        if self.ruletype not in list(json_rule.keys()):
            raise UserPolicyValueError("%s value not in entry:\n    %s" % (self.ruletype, json_rule)) 

        # Not much to do here. There's no data on startup.

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
