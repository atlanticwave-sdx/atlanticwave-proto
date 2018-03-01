# Copyright 2017 - Sean Donovan, John Skandalakis
# AtlanticWave/SDX Project

import os

import dataset
import cPickle as pickle
import logging
import json

from lib.Singleton import SingletonMixin
from AuthorizationInspector import AuthorizationInspector
from AuthenticationInspector import AuthenticationInspector


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

        # Check to see if there's anything in the DB, if so, we're done.
        if self._parse_db() != None:
            return
        # If DB is empty, parse manifest file that's passed in
        else:
            self._parse_manifest(manifest)

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


    def _send_to_AA(self, user):
        print "Sending %s:%s to AuthenticationInspector" % (user['username'],
                                                            user['credentials'])
        AuthenticationInspector.instance().add_user(user['username'],
                                                    user['credentials'])
        AuthorizationInspector.instance().set_user_authorization(
                                                    user['username'],
                                                    user['permitted_actions'])

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
