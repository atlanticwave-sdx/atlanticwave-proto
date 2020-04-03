# Copyright 2017 - Sean Donovan
# AtlanticWave/SDX Project


from UserPolicy import *
from datetime import datetime
from shared.constants import *
from EdgePortLCRule import *
from ManagementSDXRecoverRule import *
import networkx as nx

class ManagementSDXRecoverPolicy(UserPolicy):
    ''' This policy is used during initialization of the LocalController to let 
        it know which ports of it are edge ports. This is necessary for proper
        learning of new paths to occur without redundant "new destination" 
        messages coming in from switch-to-switch ports. 

        It requires the following information at intialization:
          - Switch

        Example Json:
        {"EdgePort":{
            "switch":"mia-switch"}}
    
        The vast majority of the work is handled by the breakdown_rule() function
        which uses the topology to determine which ports are actually the edge 
        ports.    
    ''' 

    def __init__(self, username, json_rule):
        self.switch = None

        super(ManagementSDXRecoverPolicy, self).__init__(username,
                                             json_rule)

        # Anything specific here?
        pass

    def __str__(self):
        return "%s(%s)" % (self.get_policy_name(), self.switch)
    
    @classmethod
    def check_syntax(cls, json_rule):
        try:
            # Make sure the times are the right format
            # https://stackoverflow.com/questions/455580/json-datetime-between-python-and-javascript
            # 'switch' is the LocalController NAME!
            switch = json_rule[cls.get_policy_name()]['switch']

        except Exception as e:
            import os
            exc_type, exc_obj, exc_tb = sys.exc_info()
            filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            lineno = exc_tb.tb_lineno
            print "%s: Exception %s at %s:%d" % (self.get_policy_name(),
                                                 str(e), filename,lineno)
            raise
            
    def breakdown_rule(self, tm, ai):
        ''' There are two stages to breaking down these rules:
              - determine edge ports for the local switch
              - create EdgePortLCRules for each edge port
            To determine which ports are edge port, we look at each port and see
            what type the neighbor is. If they are a "switch" type, then that's
            an internal port, otherwise, it's an edge port.
        '''
        print "-----CW-breakdown_rule(self, tm, ai):-------"
        self.breakdown = []
        topology = tm.get_topology()
        authorization_func = ai.is_authorized
        switch_id = topology.node[self.switch]['dpid']
        shortname = topology.node[self.switch]['locationshortname']
        bd = UserPolicyBreakdown(shortname, [])
        msr = ManagementSDXRecoverRule(switch_id)
        bd.add_to_list_of_rules(msr)

        for i in bd.get_list_of_rules():
            print 
        
        self.breakdown.append(bd)
        return self.breakdown

    
    def check_validity(self, tm, ai):
        #FIXME: This is going to be skipped for now, as we need to figure out what's authorized and what's not.
        return True

    def _parse_json(self, json_rule):
        jsonstring = self.ruletype

        #print "rule type:" + str(jsonstring)
        #print "json_rule.keys():" 
        #for i in json_rule.keys():
        #    print i
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

        





