# Copyright 2017 - Sean Donovan
# AtlanticWave/SDX Project


from UserPolicy import *
from datetime import datetime
from shared.constants import rfc3339format
from shared.SDXMatches import *
from shared.SDXActions import *


class SDXPolicy(UserPolicy):
    ''' This policy is a parent for creating "SDX Rules" on from a network. Both
        SDXIngressPolicy and SDXEgressPolicy inherent from this.
        An "SDX Rule" is an arbitrary network manipulation based on a limited
        number of Matches and Actions. 

       It requires the following information:
         - Start time
         - End time
         - Switch
         - List of Matches  
         - List of Actions

       Example JSON:
       {"sdxXXgress":{
            "starttime":"1985-04-12T23:20:50",
            "endtime":"1985-04-12T23:20:50+0400",
            "switch":"atl-switch",
            "matches": [<list of SDXMatches>],
            "actions": [<list of SDXActions]}}
        Times are RFC3339 formated offset from UTC, if any, is after the seconds

        Side effect of coming from JSON, everything's unicode. Need to handle 
        parsing things into the appropriate types (int, for instance).
    '''
    
    def __init__(self, username, rulename, json_rule, jsonstring,
                 valid_matches, valid_actions):
        self.start_time = None
        self.stop_time = None
        self.switch = None
        self._jsonstring = jsonstring
        self._valid_matches = valid_matches
        self._valid_actions = valid_actions
        self.matches = []
        self.actions = []

        super(SDXPolicy, self).__init__(username, rulename, json_rule)

        # Anything specific here?
        pass

    @staticmethod
    def check_syntax(json_rule):
        try:
            # Make sure the times are the right format
            # https://stackoverflow.com/questions/455580/json-datetime-between-python-and-javascript

            starttime = datetime.strptime(json_rule[self._jsonstring]['starttime'],
                                         rfc3339format)
            endtime = datetime.strptime(json_rule[self._jsonstring]['endtime'],
                                         rfc3339format)
            delta = endtime - starttime
            if delta.total_seconds() < 0:
                raise UserPolicyValueError("Time ends before it begins: begin %s, end %s" % (starttime, endtime))

            # Check that switch is good?
            switch = json_rule[self._jsonstring]['switch']
            #FIXME - Is there anything that can be done about this?

            # Make sure matches and actions make sense
            matches_json = json_rule[self._jsonstring]['matches']
            actions_json = json_rule[self._jsonstring]['actions']
            matches = []
            actions = []

            if type(matches_json) != list:
                raise UserPolicyTypeError("matches is not a list %s: %s" %
                                          (type(matches_json), matches))
            if type(actions_json) != list:
                raise UserPolicyTypeError("actions is not a list %s: %s" %
                                          (type(actions_json), actions))

            for match_entry in matches_json:
                if type(match_entry) != dict:
                    raise UserPolicyTypeError("match is not a list %s: %s" %
                                              (type(match_entry), match_entry))
                if len(match_entry.keys()) != 1:
                    raise UserPolicyValueError("match has more than one key %s: %s : %s" %
                                               (len(match_entry.keys()),
                                                match_entry.keys(),
                                                match_entry))
                m = match_entry.keys()[0]
                v = match_entry[m]

                # Check to confirm that it is a valid Match type
                if m not in self._valid_matches:
                    raise UserPolicyValueError("%s is not a valid SDX  match type: %s" %
                                               (m, self._valid_matches))

                # This is somewhat magical. It first looks up the match class
                # type based on the match type (m), and then creates an object
                # based on the value
                # Like I said, magic.
                match = SDXMatch.lookup_match_type(m)(v)
                matches.append(match)

            for action_entry in actions_json:
                if type(action_entry) != dict:
                    raise UserPolicyTypeError("action is not a list %s: %s" %
                                              (type(action_entry),
                                               action_entry))
                if len(action_entry.keys()) != 1:
                    raise UserPolicyValueError("action has more than one key %s: %s : %s" %
                                               (len(action_entry.keys()),
                                                action_entry.keys(),
                                                action_entry))
                a = action_entry.keys()[0]
                v = action_entry[a]

                # Check to confirm that it is a valid action type
                if a not in self._valid_actions:
                    raise UserPolicyValueError("%s is not a valid SDX action type: %s" %
                                               (a, self._valid_actions))
                
                # Same magic as above
                action = SDXAction.lookup_action_type(a)(v)
                actions.append(action)
        except e:
            raise

    def check_validity(self, tm, ai):
        #FIXME: This is going to be skipped for now, as we need to figure out what's authorized and what's not.
        return True

    def _parse_json(self, json_rule):
        if type(json_rule) is not dict:
            raise UserPolicyTypeError("json_rule is not a dictionary:\n    %s" % json_rule)
        if self._jsonstring not in json_rule.keys():
            raise UserPolicyValueError("%s value not in entry:\n    %s" % ('rules', json_rule))
        
        self.start_time = json_rule[self._jsonstring]['starttime']
        self.end_time = json_rule[self._jsonstring]['endtime']

        self.switch = json_rule[self._jsonstring]['switch']
        
        matches_json = json_rule[self._jsonstring]['matches']
        actions_json = json_rule[self._jsonstring]['actions']

        for match_entry in json_rule[self._jsonstring]['matches']:
            m = match_entry.keys()[0]
            v = match_entry[m]

            # This is described in check_syntax()
            match = SDXMatch.lookup_match_type(m)(v)
            self.matches.append(match)

        for action_entry in actions_json:
            a = action_entry.keys()[0]
            v = action_entry[a]

            # Same magic as above
            action = SDXAction.lookup_action_type(a)(v)
            self.actions.append(action)

    def breakdown_rule(self, tm, ai):
        self.breakdown = []
        topology = tm.get_topology()
        authorization_func = ai.is_authorized

        # Get switch/LC info
        shortname = topology.node[self.switch]['locationshortname']
        switch_id = topology.node[self.switch]['dpid']
        
        # Collect matches
        matches = []
        for match in self.matches:
            matches.append(match.get_match()) # Oh god, this hurts...
    
        # Collect actions
        actions = []
        drop = False
        cont = False
        for action in self.actions:
            a = action.get_match()
            if isinstance(a, Drop):
                drop = True
            elif isinstance(a, Continue):
                cont = True
            actions.append(a)
        # Since this is an SDX rule, there's an implied Continue as part of
        # the actions. Append this (if there isn't a drop).
        if !drop and !cont:
            actions.append(Continue())

        # Make breakdown
        bd = UserPolicyBreakdown(shortname, [])
        marule = MatchActionLCRule(switch_id, matches, actions, False)
        bd.add_to_list_of_rules(rule)
        self.breakdown.append(bd)
        
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


    def switch_change_callback(self, tm, ai, data):
        ''' This is called when a switch change message is called back. 
            May not need to be implemented. '''
        pass



class SDXEgressPolicy(SDXPolicy):
    ''' This policy inherits from SDXPolicy which has virtually all 
        functionality built in. '''    
    def __init__(self, username, json_rule):
        jsonstring = "sdxegress"
        VALID_SDX_EGRESS_MATCHES = ['src_mac', 'src_ip', 'tcp_src', 'udp_src',
                                    'dst_mac', 'dst_ip', 'tcp_dst', 'udp_dst',
                                    'ip_proto', 'eth_type', 'vlan']
        VALID_SDX_EGRESS_ACTIONS = ['ModifySRCMAC', 'ModifySRCIP',
                                    'ModifyTCPSRC', 'ModifyUDPSRC',
                                    'ModifyVLAN', 'Drop', 'Continue']

        super(SDXEgressPolicy, self).__init__(username, "SDXEgress",
                                              json_rule, jsonstring,
                                              VALID_SDX_EGRESS_MATCHES,
                                              VALID_SDX_EGRESS_ACTIONS)

        # Anything specific here?
        pass

class SDXIngressPolicy(SDXPolicy):
    ''' This policy inherits from SDXPolicy which has virtually all 
        functionality built in. '''    
    def __init__(self, username, json_rule):
        jsonstring = "sdxingress"
        VALID_SDX_INGRESS_MATCHES = ['src_mac', 'src_ip', 'tcp_src', 'udp_src',
                                     'dst_mac', 'dst_ip', 'tcp_dst', 'udp_dst',
                                     'ip_proto', 'eth_type', 'vlan']
        VALID_SDX_INGRESS_ACTIONS = ['ModifySRCMAC', 'ModifySRCIP',
                                     'ModifyTCPSRC', 'ModifyUDPSRC',
                                     'ModifyVLAN', 'Drop', 'Continue']

        super(SDXIngressPolicy, self).__init__(username, "SDXIngress",
                                               json_rule, jsonstring,
                                              VALID_SDX_INGRESS_MATCHES,
                                              VALID_SDX_INGRESS_ACTIONS)

        # Anything specific here?
        pass
