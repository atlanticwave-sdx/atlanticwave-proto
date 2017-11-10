# Copyright 2017 - Sean Donovan, John Skandalakis
# AtlanticWave/SDX Project

import os

import dataset
import cPickle as pickle
import logging
import json

from lib.Singleton import SingletonMixin
from AuthorizationInspector import AuthorizationInspector


class UserManager(SingletonMixin):
    
    def __init__(self, database, manifest):
        self._setup_logger()

        # Start database/dictionary
        self.db = database
        self.user_table = self.db['users']        # All the find live here.

        # Used for filtering.
        self._valid_table_columns = ['username', 'credentials',
                                     'organization', 'contact',
                                     'permitted_actions', 'restrictions']

        # Parse manifest file that's passed in
        self._parse_manifest(manifest)

    def _parse_manifest(self, manifest_filename):
        with open(manifest_filename) as data_file:
            data = json.load(data_file)

        for unikey in data['participants'].keys():
            key = str(unikey)
            user = data['participants'][key]
            user['username'] = key
            self.add_user(user)

    def add_user(self, user):
        self.user_table.insert(self._format_db_entry(user))
    
    def get_user(self, user):
        self.logger.info("getting user: {}".format(user))
        user = self.user_table.find_one(username=user)
        return self._convert_db_user(user)

    def get_users(self):
        self.logger.info("getting all users") 

        users = []
        for user in self.user_table.all():
            users.append(self._convert_db_user(user))
        return users

    def _convert_db_user(self, user):
        temp_user = {}
        temp_user['username'] = user['username']
        temp_user['credentials'] = user['credentials']
        temp_user['organization'] = user['organization']
        temp_user['contact'] = user['contact']
        temp_user['type'] = user['type']
        temp_user['permitted_actions'] = pickle.loads(
            str(user['permitted_actions']))
        temp_user['restrictions'] = pickle.loads(
            str(user['restrictions']))
        return temp_user

    
    def _format_db_entry(self, user):
        temp_user = {}
        temp_user['username'] = user['username']
        temp_user['credentials'] = user['credentials']
        temp_user['organization'] = user['organization']
        temp_user['contact'] = user['contact']
        temp_user['type'] = user['type']
        temp_user['permitted_actions'] = pickle.dumps(user['permitted_actions'])
        temp_user['restrictions'] = pickle.dumps(user['restrictions'])
        return temp_user

    def _setup_logger(self):
        ''' Internal function for setting up the logger formats. '''
        # reused from https://github.com/sdonovan1985/netassay-ryu/blob/master/base/mcm.py
        formatter = logging.Formatter('%(asctime)s %(name)-12s: %(levelname)-8s %(message)s')
        console = logging.StreamHandler()
        console.setLevel(logging.WARNING)
        console.setFormatter(formatter)
        logfile = logging.FileHandler('sdxcontroller.log')
        logfile.setLevel(logging.DEBUG)
        logfile.setFormatter(formatter)
        self.logger = logging.getLogger('sdxcontroller.localctlrmgr')
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(console)
        self.logger.addHandler(logfile)
