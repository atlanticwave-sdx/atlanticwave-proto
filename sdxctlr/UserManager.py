from __future__ import print_function
from __future__ import absolute_import
# Copyright 2017 - Sean Donovan, John Skandalakis
# AtlanticWave/SDX Project

import os

import cPickle as pickle
import json

from lib.AtlanticWaveManager import AtlanticWaveManager
from .AuthorizationInspector import AuthorizationInspector
from .AuthenticationInspector import AuthenticationInspector


class UserManager(AtlanticWaveManager):
    
    def __init__(self, db_filename, manifest, loggeridprefix='sdxcontroller'):
        loggerid = loggeridprefix + '.usermanager'
        super(UserManager, self).__init__(loggerid)

        # Start database
        db_tuples = [('user_table', 'users')]
        self._initialize_db(db_filename, db_tuples)

        # Used for filtering.
        self._valid_table_columns = ['username', 'credentials',
                                     'organization', 'contact',
                                     'permitted_actions', 'restrictions']

        # Check to see if there's anything in the DB, if so, we're done.
        if self._parse_db() != None:
            return
        # If DB is empty, parse manifest file that's passed in
        else:
            self.logger.info("Loading users from the Manifest")
            self._parse_manifest(manifest)

        self.logger.warning("%s initialized: %s" % (self.__class__.__name__,
                                                    hex(id(self))))

    def _parse_db(self):
        # This needs to check to see if the list of users is empty.
        count = 0
        for user in self.user_table.find():
            self._send_to_AA(user)
            count += 1

        self.logger.info("There are %d users in the user table" % count)

        if count == 0:
            return None
        return count                         

    def _parse_manifest(self, manifest_filename):
        with open(manifest_filename) as data_file:
            data = json.load(data_file)

        for unikey in data['participants'].keys():
            key = str(unikey)
            user = data['participants'][key]
            user['username'] = key
            self.add_user(user)

    def add_user(self, user):
        # Add to DB
        self.user_table.insert(self._format_db_entry(user))

        # Push to A&A Inspectors
        self._send_to_AA(user)
    
    def get_user(self, user):
        self.logger.info("getting user: {}".format(user))
        user = self.user_table.find_one(username=user)
        if None != user:
            return self._convert_db_user(user)
        return None

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


    def _send_to_AA(self, user):
        print("Sending %s:%s to AuthenticationInspector" % (user['username'],
                                                            user['credentials']))
        AuthenticationInspector().add_user(user['username'],
                                           user['credentials'])
        AuthorizationInspector().set_user_authorization(
            user['username'], user['permitted_actions'])
