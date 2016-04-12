# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


import json
from shared.offield import *
from shared.match import *
from shared.action import *
from shared.instruction import *

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
        self.parse_configuration(data)

    def parse_configuration(self, data)
        for entry in data['rules']:
            switch = self._parse_switch(entry)
            priority = self._parse_priority(entry)
            cookie = self._parse_cookie(entry)
            match = self._parse_match(entry)
            action = self._parse_action(entry)
            instruction = self._parse_instruction(entry,
                                                  match,
                                                  action)

    def __parse_type(self, entry, name, typeof):
        if name not in entry.keys():
            raise ConfigurationParserValueError("%s value not in entry:\n    %s" % name, entry)
        val = entry[name]
        if type(val) is not typeof:
            raise ConfigurationParserTypeError("%s is not of type %s:\n    %s" % name, typeof, entry)
        return val
            
    def _parse_switch(self, entry):
        return self.__parse_type(entry, 'switch', int)

    def _parse_priority(self, entry):
        return self.__parse_type(entry, 'priority', int)

    def _parse_cookie(self, entry):
        return self.__parse_type(entry, 'cookie', int)


    def __parse_fields(self, fields):
        valid_matches = MATCH_NAME_TO_CLASS.keys()
        match_fields = []
        for ent in fields.keys():
            if ent not in valid_matches:
                raise "%s is not a valid_match:\n    %s" % ent, entry
            if MATCH_NAME_TO_CLASS[ent]['required'] == None:
                value = fields[ent]
                match_fields.append(MATCH_NAME_TO_CLASS[ent](value))
            else:
                vals = fields[ent]
                match_fields.append(MATCH_NAME_TO_CLASS[ent](**value))
        return match_fields
    
    def _parse_match(self, entry):
        if 'match' not in entry.keys():
            raise ConfigurationParserValueError("match value not in entry:\n    %s" % entry)
        matchval = entry['match']

        match_fields = self.__parse_fields(matchval)
                
        # if it's not valid, it'll blow up.
        match = OpenFlowMatch(match_fields)
        match.check_validity()
        return match

    def _parse_actions(self, entry):
        if 'actions' not in entry.keys():
            raise ConfigurationParserValueError("actions value not in entry:\n    %s" % entry)
        actionval = entry['actions']

        valid_actions = ACTION_NAME_TO_CLASS.keys()
        actions = []
        for ent in actionval:
            action_type = ent.keys()[0]
            if action_type not in valid_actions:
                raise "%s is not in valid_actions:\n    %s" % ent, entry
            if ACTION_NAME_TO_CLASS[action_type][fields] == False:
                value = ent[action_type]
                actions.append(ACTION_NAME_TO_CLASS[action_type]['type'](value))
            else:      # Has a bunch of fields
                valid_matchs = MATCH_NAME_TO_CLASS.keys()
                fields = self.__parse_fields(ent[action_type])
                for field in fields:
                    actions.append(ACTION_NAME_TO_CLASS[action_type]['type'](**field))

        return actions

    def _parse_instruction(self, entry, match, action):
        pass


    
    
