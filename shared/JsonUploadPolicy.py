# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project

from UserPolicy import *
from config_parser.config_parser import *


class JsonUploadPolicy(UserPolicy):
    ''' This is a demo for testing the RuleManager. '''

    def __init__(self, username, json_rule):
        self.rules = None
        super(JsonUploadPolicy, self).__init__(username, json_rule)

        # JsonUploadPolicy specific init stuff below.

    @staticmethod
    def check_syntax(json_rule):
        # The config_parser may be useful here.
        try:
            parse_configuration(json_rule)
        except (ConfigurationParserTypeError,
                ConfigurationParserValueError) as e:
            raise e
        return True
    
    def breakdown_rule(self, topology, authorization_func):
        # self.rules is a tuple of (location, rule).
        # First, gather up all the rules belonging to a switch.
        self.breakdown = []
        rules_per_location = {}
        for (location, rule) in self.rules:
            if location not in rules_per_location.keys():
                rules_per_location[location] = []
            rules_per_location[location].append(rule)


        #Second, put those rules into a UserPolicyBreakdown.
        all_locations = topology.nodes()
        for location in rules_per_location.keys():
            # get LC
            if location not in all_locations:
                raise ValueError("There is no switch named %s in the topology (%s)" %
                                 (location, all_locations))
                                 
            local_ctlr = topology.node[location]['lcip']
            bd = UserPolicyBreakdown(local_ctlr)
            for rule in rules_per_location[location]:
                bd.add_to_list_of_rules(rule)

            self.breakdown.append(bd)
        return self.breakdown

    def check_validity(self, topology, authorization_func):
        return self.check_syntax(self.json_rule)

    def _parse_json(self, json_rule):
        self.rules =  parse_configuration(json_rule)
