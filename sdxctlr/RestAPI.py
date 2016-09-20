# Copyright 2016 - Sean Donovan
# Edited by John Skandalakis
# AtlanticWave/SDX Project
# Login based on example code from https://github.com/maxcountryman/flask-login

from shared.Singleton import Singleton
from shared.L2TunnelPolicy import L2TunnelPolicy
from AuthenticationInspector import AuthenticationInspector
from AuthorizationInspector import AuthorizationInspector
from RuleManager import RuleManager
from TopologyManager import TopologyManager
#from RuleRegistry import RuleRegistry

#API Stuff
import flask
from flask import Flask, request, url_for, send_from_directory, render_template

import flask_login
from flask_login import LoginManager

#Topology json stuff
from networkx.readwrite import json_graph
import json

#multiprocess stuff
from multiprocessing import Process

#stuff to serve sdxctlr/static content - I will change this in an update but for now this is viable.
import SimpleHTTPServer
import SocketServer

#System stuff
import sys, os, traceback

#datetime
from datetime import datetime

class RestAPI(object):
    ''' The REST API will be the main interface for participants to use to push 
        rules (eventually) down to switches. It will gather authentication 
        information from the participant and check with the 
        AuthenticationInspector if the participant is authentic. It will check 
        with the AuthorizationInspector if a particular action is available to a 
        given participant. Once authorized, rules will be pushed to the 
        RuleManager. It will draw some of its API from the RuleRegistry, 
        specifically for the libraries that register with the RuleRegistry. 
        Singleton. '''
    __metaclass__ = Singleton


    global User, app, login_manager

    app = Flask(__name__, static_url_path='', static_folder='')
    #FIXME: This should be more secure.
    app.secret_key = 'ChkaChka.....Boo, Ohhh Yeahh!'


    login_manager = LoginManager()

    def api_process(self):
        login_manager.init_app(app)
        app.run()

    def __init__(self):
        #FIXME: Creating user only for testing purposes
        AuthenticationInspector().add_user('sdonovan','1234')
        p = Process(target=self.api_process)
        p.start()
        pass

    def _setup_logger(self):
        ''' Internal fucntion for setting up the logger formats. '''
        # reused from https://github.com/sdonovan1985/netassay-ryu/blob/master/base/mcm.py
        formatter = logging.Formatter('%(asctime)s %(name)-12s: %(levelname)-8s %(message)s')
        console = logging.StreamHandler()
        console.setLevel(logging.WARNING)
        console.setFormatter(formatter)
        logfile = logging.FileHandler('sdxcontroller.log')
        logfile.setLevel(logging.DEBUG)
        logfile.setFormatter(formatter)
        self.logger = logging.getLogger('sdxcontroller.rest')
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(console)
        self.logger.addHandler(logfile) 

    class User(flask_login.UserMixin):
        pass
    
    # This maintains the state of a logged in user.
    @staticmethod
    @login_manager.user_loader
    def user_loader(email):
        user = User()
        user.id = email
        return user

    # Preset the login form to the user and request to log user in
    @staticmethod
    @app.route('/', methods=['GET'])
    def home():
        #return app.send_static_file('static/index.html')
        try: 
            print flask_login.current_user.id
            return flask.render_template('index.html')
        except:
            print "test"
            return app.send_static_file('static/index.html')

    
    # Preset the login form to the user and request to log user in
    @staticmethod
    @app.route('/login', methods=['POST','GET'])
    def login(): 
        email = flask.request.form['email']
        #if flask.request.form['pw'] == users[email]['pw']:
        if AuthenticationInspector().is_authenticated(email,flask.request.form['pw']):
            user = User()
            user.id = email
            flask_login.login_user(user)
            return flask.redirect(flask.url_for('home'))

        return 'Bad login'

    # This is a worthless function. The redirect will eventually take you somewhere else.
    @staticmethod
    @app.route('/protected')
    @flask_login.login_required
    def protected():
        if AuthorizationInspector().is_authorized(flask_login.current_user.id,'login'):
            return 'Logged in as: ' + flask_login.current_user.id
        return unauthorized_handler()

    # Log out of the system
    @staticmethod
    @app.route('/logout')
    def logout():
        flask_login.logout_user()
        return flask.redirect(flask.url_for('home'))

    # Present the page which tells a user they are unauthorized
    @staticmethod
    @login_manager.unauthorized_handler
    def unauthorized_handler():
        return 'Unauthorized'

    # Access information about a user
    @staticmethod
    @app.route('/user/<username>')
    def show_user_information(username):
        if AuthorizationInspector().is_authorized(flask_login.current_user.id,'get_user_info'):
            return "Test: %s"%username
        return unauthorized_handler()

    # Return the network topology in json format
    @staticmethod
    @app.route('/topology.json')
    def show_network_topology_json():
        if AuthorizationInspector().is_authorized(flask_login.current_user.id,'show_topology'):
            G = TopologyManager().get_topology()
            data = json_graph.node_link_data(G)
            return json.dumps(data)
        return unauthorized_handler()

    # Return the network topology in json format
    @staticmethod
    @app.route('/topology')
    def show_network_topology():
        if AuthorizationInspector().is_authorized(flask_login.current_user.id,'show_topology'):
            html = open('static/topology.html').read()
            return html
            G = TopologyManager().get_topology()
            data = json_graph.adjacency_data(G)
            return str(data)
        return unauthorized_handler()

    @staticmethod
    @app.route('/pipe',methods=['POST'])
    def make_new_pipe():
        rfc3339format = "%Y-%m-%dT%H:%M:%S%z"
        if AuthorizationInspector().is_authorized(flask_login.current_user.id,'show_topology'):

            # Just making sure the datetimes are okay
            starttime = datetime.strptime(request.form['startdate'] + ' ' + request.form['starttime'], '%Y-%m-%d %H:%M')
            endtime = datetime.strptime(request.form['enddate'] + ' ' + request.form['endtime'], '%Y-%m-%d %H:%M')

            try:
                arb = request.form['sv']
            except:
                return "Scientists Portal has not yet been implemented!"
    
            # The Object to pass into L2TunnelPolicy
            data = {"l2tunnel":{"starttime":str(starttime.strftime(rfc3339format)),
                                            "endtime":str(endtime.strftime(rfc3339format)),
                                            "srcswitch":request.form['source'],
                                            "dstswitch":request.form['dest'],
                                            "srcport":request.form['sp'],
                                            "dstport":request.form['dp'],
                                            "srcvlan":request.form['sv'],
                                            "dstvlan":request.form['dv'],
                                            "bandwidth":request.form['bw']}}
            
            policy = L2TunnelPolicy(flask_login.current_user.id, data)

            # I am really not sure what to pass through RuleManager as args
            rule_hash = RuleManager().add_rule(policy)

            return '<pre>%s</pre>'%json.dumps(data, indent=2)

            # I plan on making this redirect to a page for the rulehash, but currently this is not ready
            return rule_hash

    # Get information about a specific rule IDed by hash.
    @staticmethod
    @app.route('/rule/<rule_hash>')
    def get_rule_details_by_hash(rule_hash):
        if AuthorizationInspector().is_authorized(flask_login.current_user.id,'access_rule_by_hash'):
            try:
                return RuleManager().get_rule_details(rule_hash)
            except:
                return "Invalid rule hash"
        return unauthorized_handler()

    # Get a list of rules that match certain filters or a query.
    @staticmethod
    @app.route('/rule/search/<query>')
    def get_rule_search_by_query(query):
        if AuthorizationInspector().is_authorized(flask_login.current_user.id,'search_rules'):
            return RuleManager().get_rules(query)
        return unauthorized_handler()


if __name__ == "__main__":
    def blah(param):
        pass

    RuleManager(blah,blah)    

    RestAPI()
