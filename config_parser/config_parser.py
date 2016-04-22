# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


import json
from shared.offield import *
from shared.match import *
from shared.action import *
from shared.instruction import *
from shared.OpenFlowRule import * 

class ConfigurationParserTypeError(TypeError):
    pass

class ConfigurationParserValueError(ValueError):
    pass

class ConfigurationParser(object):
    ''' This parses configuration files.
    '''

    def __init__(self):
        pass

    def __repr__(self):
        pass

    def __str__(self):
        pass

    def parse_configuration_file(self, filename):
        with open(filename) as data_file:    
            data = json.load(data_file)
        return self.parse_configuration(data)

    def parse_configuration(self, data):
        rules = []
        for entry in data['rules']:
            switch_id = self._parse_switch(entry)
            priority = self._parse_priority(entry)
            cookie = self._parse_cookie(entry)
            table = self._parse_table(entry)
            instruction_type = self._parse_instruction_type(entry)

            # MATCH_NAME_TO_INSTRUCTION is used to figure out what we need to do
            # for each entry
            instruction_params = self.get_instruction_params(instruction_type)
            
            # Required fields first
            match = None
            param_values = {}
            if 'match' in instruction_params['required_fields']:
                match = self._parse_match(entry)
            if 'actions' in instruction_params['required_fields']:
                param_values['actions'] = self._parse_actions(entry)
                
            # Parameters
            for p in instruction_params['required_parameters']:
                param_values[p] = entry[p]
            for p in instruction_params['optional_parameters']:
                param_values[p] = entry[p]
            
            instruction = self._build_instruction(instruction_type,
                                                  param_values)

            # Have all pieces now, build the OpenFlowRule
            rule = OpenFlowRule(match, instruction, table, priority, cookie, switch_id)
            rules.append(rule)

        # Return rules, because that's what the configuration is.
        return rules

    def __parse_type(self, entry, name, typeof):
        if name not in entry.keys():
            raise ConfigurationParserValueError("%s value not in entry:\n    %s" % (name, entry))
        val = entry[name]
        if type(val) is not typeof:
            raise ConfigurationParserTypeError("%s is not of type %s of type %s:\n    %s" % (name, typeof, type(val), entry))
        return val
            
    def _parse_switch(self, entry):
        return self.__parse_type(entry, 'switch', int)

    def _parse_priority(self, entry):
        return self.__parse_type(entry, 'priority', int)

    def _parse_cookie(self, entry):
        return self.__parse_type(entry, 'cookie', int)

    def _parse_table(self, entry):
        return self.__parse_type(entry, 'table', int)

   


    def __parse_fields(self, fields):
        valid_matches = MATCH_NAME_TO_CLASS.keys()
        match_fields = []
        for ent in fields.keys():
            if ent not in valid_matches:
                raise ConfigurationParserValueError("%s is not a valid_match" % (ent))
            if MATCH_NAME_TO_CLASS[ent]['required'] == None:
                value = fields[ent]
                fieldtype = MATCH_NAME_TO_CLASS[ent]['type']
                match_fields.append(fieldtype(value))
            else:
                fieldvals = fields[ent]
                fieldtype = MATCH_NAME_TO_CLASS[ent]['type']
                for entry in MATCH_NAME_TO_CLASS[ent]['required']:
                    print "fieldvals: " + str(fieldvals)
                    if entry not in fieldvals.keys():
                        raise ConfigurationParserValueError("%s is missing field %s" % (fields, entry))
                match_fields.append(fieldtype(**fieldvals))
        return match_fields
    
    def _parse_match(self, entry):
        if 'match' not in entry.keys():
            raise ConfigurationParserValueError("match value not in entry:\n    %s" % (entry))
        matchval = entry['match']

        match_fields = self.__parse_fields(matchval)
                
        # if it's not valid, it'll blow up.
        match = OpenFlowMatch(match_fields)
        match.check_validity()
        return match

    def _parse_actions(self, entry):
        if 'actions' not in entry.keys():
            raise ConfigurationParserValueError("actions value not in entry:\n    %s" % (entry))
        actionval = entry['actions']

        # actionval is expected to be a list for processing. Convert singletons.
        if type(actionval) == dict:
            actionval = [actionval]

        valid_actions = ACTION_NAME_TO_CLASS.keys()
        actions = []
        for ent in actionval:
            action_type = ent.keys()[0]
            if action_type not in valid_actions:
                raise "%s is not in valid_actions:\n    %s" % (ent, entry)
            if ACTION_NAME_TO_CLASS[action_type]['fields'] == False:
                value = ent[action_type]
                actions.append(ACTION_NAME_TO_CLASS[action_type]['type'](value))
            else:      # Has a bunch of fields
                valid_matchs = MATCH_NAME_TO_CLASS.keys()
                fields = self.__parse_fields(ent[action_type])
                for field in fields:
                    actions.append(ACTION_NAME_TO_CLASS[action_type]['type'](field))

        return actions

    def _parse_instruction_type(self, entry):
        return self.__parse_type(entry, 'instruction', unicode)

    def get_instruction_params(self, instruction_type):
        if instruction_type not in MATCH_NAME_TO_INSTRUCTION.keys():
            raise ConfigurationParserValueError("%s is not a valid instruction type:\n    %s" % (instruction_type, entry))
        return MATCH_NAME_TO_INSTRUCTION[instruction_type]

    def _build_instruction(self, instruction_type, param_values):
        inst_type = MATCH_NAME_TO_INSTRUCTION[instruction_type]['type']
        return inst_type(**param_values)
    
