# Copyright 2016 - Sean Donovan
# Edited by John Skandalakis
# AtlanticWave/SDX Project
# Login based on example code from https://github.com/maxcountryman/flask-login

from shared.Singleton import Singleton
from AuthenticationInspector import AuthenticationInspector
from AuthorizationInspector import AuthorizationInspector
from RuleManager import RuleManager
from TopologyManager import TopologyManager
#from RuleRegistry import RuleRegistry

#API Stuff
import flask
from flask import Flask
from flask import request

from flask_login import LoginManager
import flask_login

#Topology json stuff
from networkx.readwrite import json_graph

#multiprocess stuff
from multiprocessing import Process

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


    global User, users, app, login_manager, authenticator, authorizor, topo, rule_manager

    #FIXME: Our mock database should be deleter.
    users = {'foo@bar.tld': {'pw': 'secret'}}

    app = Flask(__name__)
    app.secret_key = 'ChkaChka.....Boo, Ohhh Yeahh!'

    login_manager = LoginManager()

    authenticator = AuthenticationInspector()
    authorizor = AuthorizationInspector()

    topo = TopologyManager()

    #rule_manager = RuleManager()


    def api_process(self):
        login_manager.init_app(app)
        app.run()

    def __init__(self):
        #FIXME: Creating user only for testing purposes
        authenticator.add_user('sdonovan','1234')
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

    @staticmethod
    @login_manager.user_loader
    def user_loader(email):
        #TODO: Fix this
        #if email not in users:
        #    return

        user = User()
        user.id = email
        return user

    @staticmethod
    @login_manager.request_loader
    def request_loader(request):
        email = request.form.get('email')

        #TODO: Fix this
        #if email not in users:
        #    return

        user = User()
        user.id = email

        # DO NOT ever store passwords in plaintext and always compare password
        # hashes using constant-time comparison!
        user.is_authenticated = request.form['pw'] == users[email]['pw']

        return user

    @staticmethod
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if flask.request.method == 'GET':
            return '''
                   <form action='login' method='POST'>
                    <input type='text' name='email' id='email' placeholder='email'></input><br>
                    <input type='password' name='pw' id='pw' placeholder='password'></input><br>
                    <input type='submit' name='submit'></input>
                   </form>
                   '''

        email = flask.request.form['email']
        #if flask.request.form['pw'] == users[email]['pw']:
        if authenticator.is_authenticated(email,flask.request.form['pw']):
            user = User()
            user.id = email
            flask_login.login_user(user)
            return flask.redirect(flask.url_for('protected'))

        return 'Bad login'


    @staticmethod
    @app.route('/protected')
    @flask_login.login_required
    def protected():
        if authorizor.is_authorized(flask_login.current_user.id,'login'):
            return 'Logged in as: ' + flask_login.current_user.id
        return unauthorized_handler()

    @staticmethod
    @app.route('/logout')
    def logout():
        flask_login.logout_user()
        return 'Logged out'

    @staticmethod
    @login_manager.unauthorized_handler
    def unauthorized_handler():
        return 'Unauthorized'

    @staticmethod
    @app.route('/user/<username>')
    def show_user_information(username):
        if authorizor.is_authorized(flask_login.current_user.id,'get_user_info'):
            return "Test: %s"%username
        return unauthorized_handler()

    @staticmethod
    @app.route('/topology')
    def show_network_topology():
        if authorizor.is_authorized(flask_login.current_user.id,'show_topology'):
            G = topo.get_topology()
            data = json_graph.adjacency_data(G)
            return str(data)
        return unauthorized_handler()

    @staticmethod
    @app.route('/rule/<rule_hash>')
    def get_rule_details_by_hash(rule_hash):
        if authorizor.is_authorized(flask_login.current_user.id,'access_rule'):
            #TODO: Write rule functionality.
            try:
                #return rule_manager.get_rule_details(rule_hash)
                return "tmp"
            except:
                return "Invalid rule hash"
        return unauthorized_handler()

    @staticmethod
    @app.route('/rule/search/<query>')
    def get_rule_search_by_query(query):
        if authorizor.is_authorized(flask_login.current_user.id,'access_rule'):
            #TODO: Write rule functionality.
            return "test"
        return unauthorized_handler()

    @staticmethod
    @app.route('/rule/', methods=['GET', 'POST'])
    def rule():
        if authorizor.is_authorized(flask_login.current_user.id,'rule_form'):
            if flask.request.method == 'GET':
                return open('html/rule_form.html','r').read()
            
            rule = flask.request.form['rule']

            try:
                #rule_manager.add_rule(rule)
                #TODO: REDIRECT FOR RULE HASH
                return "rule added"
            except Exception as e:
                #FIXME: currently this just appends the exception to the beginning of the form It is ugly.
                return str(e) + '<br>' + open('html/rule_form.html','r').read()

            
        return unauthorized_handler()

        

if __name__ == "__main__":
    RestAPI()
