# Copyright 2017 - Sean Donovan
# AtlanticWave/SDX Project


from UserPolicy import *
from datetime import datetime
from shared.constants import *
from EdgePortLCRule import *
import networkx as nx

jsonstring = "edgeport"

class EdgePortPolicy(UserPolicy):
    ''' This policy is used during initialization of the LocalController to let 
        it know which ports of it are edge ports. This is necessary for proper
        learning of new paths to occur without redundant "new destination" 
        messages coming in from switch-to-switch ports. 

        It requires the following information at intialization:
          - Switch

        Example Json:
        {"edgeport":{
            "switch":"mia-switch"}}
    
        The vast majority of the work is handled by the breakdown_rule() function
        which uses the topology to determine which ports are actually the edge 
        ports.    
    ''' 

    def __init__(self, username, json_rule):
        self.switch = None

        super(EdgePortPolicy, self).__init__(username,
                                             "EdgePort",
                                             json_rule)

        # Anything specific here?
        pass

    @staticmethod
    def check_syntax(json_rule):
        try:
            # Make sure the times are the right format
            # https://stackoverflow.com/questions/455580/json-datetime-between-python-and-javascript

            switch = json_rule[jsonstring]['switch']

        except e:
            raise
            
    def breakdown_rule(self, tm, ai):
        ''' There are two stages to breaking down these rules:
              - determine edge ports
              - create EdgePortLCRules for each edge port
            To determine which ports are edge port, we look at each port and see
            what type the neighbor is. If they are a "switch" type, then that's
            an internal port, otherwise, it's an edge port.
        '''

        self.breakdown = []
        topology = tm.get_topology()
        authorization_func = ai.is_authorized
        switches = [d for d in topology.nodes(data=True) if
                    d['type'] == "switch"]

        for sw in switches:
            neighbors = topology.neighbors(sw['name'])
            edges = []
            for n in neighbors:
                if topology[n]['type'] == "switch":
                    next
                # Add port to list
                edges.append(topology.edge[n][sw['name']])

            if len(edges) > 0:
                switch_id = sw['dpid']
                shortname = sw['locationshortname']
                bd = UserPolicyBreakdown(shortname, [])

                for e in edges:
                    epr = EdgePortLCRule(switch_id, e)
                    bd.add_to_list_of_rules(epr)

                self.breakdown.append(bd)
        
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

        self.switch = str(json_rule[jsonstring]['switch'])

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

        




