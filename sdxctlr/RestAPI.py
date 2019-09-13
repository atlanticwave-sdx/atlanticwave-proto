
# Edited by John Skandalakis
# AtlanticWave/SDX Project
# Login based on example code from https://github.com/maxcountryman/flask-login

from lib.AtlanticWaveModule import AtlanticWaveModule

from shared.SDXPolicy import SDXIngressPolicy, SDXEgressPolicy
from shared.L2MultipointPolicy import L2MultipointPolicy
from shared.L2TunnelPolicy import L2TunnelPolicy
from shared.EndpointConnectionPolicy import EndpointConnectionPolicy
from shared.SDXControllerConnectionManager import *

from AuthenticationInspector import AuthenticationInspector
from AuthorizationInspector import AuthorizationInspector
from PolicyManager import PolicyManager
from TopologyManager import TopologyManager
from UserManager import UserManager
from PolicyRegistry import PolicyRegistry, PolicyRegistryTypeError

#API Stuff
import flask
from flask import Flask, session, redirect, request, url_for, send_from_directory, render_template, Markup, make_response, jsonify

import flask_login
from flask_login import LoginManager, login_required

import jinja2

#from flask_sso import *

#Topology json stuff
import networkx as nx

from networkx.readwrite import json_graph
import json

#multiprocess stuff - This must be a thread, as Process is problematic with 
#syncing is necessary. With multiprocessing.Process, objects are not synched
#after the Process is started. 
from threading import Thread

#stuff to serve sdxctlr/static content - I will change this in an update but for
#now this is viable.
import SimpleHTTPServer
import SocketServer

#System stuff
import sys, os, traceback

#datetime
from datetime import datetime
from dateutil.parser import parse as pd

#Constants
from shared.constants import *

# ENDPOINTS
# - localcontrollers
EP_LOCALCONTROLLER = "/api/v1/localcontrollers"
EP_LOCALCONTROLLERLC = "/api/v1/localcontrollers/<lcname>"
EP_LOCALCONTROLLERLCINT = "/api/v1/localcontrollers/<lcname>/internalconfig"
EP_LOCALCONTROLLERLCSW = "/api/v1/localcontrollers/<lcname>/switches"
EP_LOCALCONTROLLERLCSWSPEC = "/api/v1/localcontrollers/<lcname>/switches/<switchname>"
EP_LOCALCONTROLLERLCSWSPECPORT = "/api/v1/localcontrollers/<lcname>/switches/<switchname>/ports"
EP_LOCALCONTROLLERLCSWSPECPORTSPEC = "/api/v1/localcontrollers/<lcname>/switches/<switchname>/ports/<portnumber>"
# - users
EP_USERS = "/api/v1/users"
EP_USERSSPEC = "/api/v1/users/<username>"
EP_USERSSPECPOLICIES = "/api/v1/users/<username>/policies"
EP_USERSSPECPERMISSIONS = "/api/v1/users/<username>/permissions"
# - policies
EP_POLICIES = "/api/v1/policies"
EP_POLICIESSPEC = "/api/v1/policies/number/<policynumber>"
EP_POLICIESTYPE = "/api/v1/policies/type"
EP_POLICIESTYPESPEC = "/api/v1/policies/type/<policytype>"
EP_POLICIESTYPESPECEXAMPLE = "/api/v1/policies/type/<policytype>/example.html"
# - Login
EP_LOGIN = "/api/v1/login"
EP_LOGOUT = "/api/v1/logout"


# From     http://flask.pocoo.org/snippets/45/
def request_wants_json(r):
    best = r.accept_mimetypes.best_match(['application/json',
                                          'text/html'])
    return (best == 'application/json' and
            r.accept_mimetypes[best] >
            r.accept_mimetypes['text/html'])



class RestAPI(AtlanticWaveModule):
    ''' The REST API will be the main interface for participants to use to push 
        policies (eventually) down to switches. It will gather authentication 
        information from the participant and check with the 
        AuthenticationInspector if the participant is authentic. It will check 
        with the AuthorizationInspector if a particular action is available to a
        given participant. Once authorized, policies will be pushed to the 
        PolicyManager. It will draw some of its API from the PolicyRegistry, 
        specifically for the libraries that register with the PolicyRegistry. 
        Singleton. '''

    global User, app, login_manager, shibboleth

    app = Flask(__name__, static_url_path='', static_folder='')
    my_loader = jinja2.ChoiceLoader([
        app.jinja_loader,
        jinja2.FileSystemLoader(['overhaul-templates', 
                                 'templates']),
    ])
    app.jinja_loader = my_loader
    #sso = SSO(app=app)

    #FIXME: This should be more secure.
    app.secret_key = 'ChkaChka.....Boo, Ohhh Yeahh!'

    #: Default attribute map
    '''
    SSO_ATTRIBUTE_MAP = {
        'ADFS_AUTHLEVEL': (False, 'authlevel'),
        'ADFS_GROUP': (True, 'group'),
        'ADFS_LOGIN': (True, 'nickname'),
        'ADFS_ROLE': (False, 'role'),
        'ADFS_EMAIL': (True, 'email'),
        'ADFS_IDENTITYCLASS': (False, 'external'),
        'HTTP_SHIB_AUTHENTICATION_METHOD': (False, 'authmethod'),
    }

    app.config['SSO_ATTRIBUTE_MAP'] = SSO_ATTRIBUTE_MAP
    '''
    login_manager = LoginManager()

    def api_process(self):
        login_manager.init_app(app)
        app.run(host=self.host, port=self.port)

    def __init__(self, loggeridprefix='sdxcontroller',
                 host='0.0.0.0', port=5000, shib=False):
        loggerid = loggeridprefix + ".rest"
        super(RestAPI, self).__init__(loggerid)
        
        global shibboleth
        shibboleth = shib

        self.host=host
        self.port=port

        self.logger.critical("Opening socket %s:%s" % (self.host, self.port))

        
        p = Thread(target=self.api_process)
        p.daemon = True
        p.start()
        #app.config['SSO_LOGIN_URL'] = 'http://aw.cloud.rnoc.gatech.edu/secure/login2.cgi'
        self.logger.warning("%s initialized: %s" % (self.__class__.__name__,
                                                    hex(id(self))))


    class User(flask_login.UserMixin):
        def __init__(self, id):
            self.id = id


    '''
    GET /api/v1/localcontrollers/
      List all configured Local Controllers.
    Query Parameters
      details (bool) - Default: false. Return all the details of the local 
        controllers. By default, returns a link to the local controller's 
        detailed information.
    Status Codes
      200 OK - no error
    Example Request
      GET /api/v1/localcontrollers
    Example Response
      HTTP/1.1 200 OK
      Content-Type: application/json
      {
        "href": "http://awavesdx/api/v1/localcontrollers/",
        "links": {
          "NAME": {
            "href": "http://awavesdx/api/v1/localcontrollers/NAME"
          }
        }
      }
    '''
    
    @staticmethod
    @login_required
    @app.route(EP_LOCALCONTROLLER, methods=['GET'])
    def v1localcontrollers():
        base_url = request.base_url
        retdict = {'links':{},'href':base_url}
        
        # Get topology
        topo = TopologyManager().get_topology()            
        for node_id in topo.nodes():
            node = topo.node[node_id]
            if node['type'] == 'localcontroller':
                # Add each LC to the dictionary
                lcdict = {'href':base_url + "/" + node_id}
                
                ##### QUERY details #####
                if (flask_login.current_user.is_authenticated and
                    (request.args.get('details') == 'true' or
                     request.args.get('details') == 'True')):
                    lcdict['lcip'] = node['ip']
                    lcdict['internalconfig'] = {'href': base_url + "/" +
                                                node_id + "/internalconfig"}
                    lcdict['operator'] = {'organization': node['org'],
                                        'administrator': node['administrator'],
                                        'contact' : node['contact']}
                    # Add links to each switch
                    lcdict['switches'] = {'href': base_url + "/" +
                                          node_id + "/switches"}
                    for switch in node['switches']:
                        lcdict['switches'][switch] = {'href': base_url +
                                                      "/" + node_id +
                                                      "/switches/" + switch}
                retdict['links'][node_id] = lcdict

        # If they requested a JSON, send back the raw JSON
        if request_wants_json(request):
            return json.dumps(retdict)
        # HTML output
        return flask.render_template('localcontrollers.html', lcdict=retdict)


    '''
    GET /api/v1/localcontrollers/<lcname>
      List details of local controller named lcname.
    Query Parameters
      details (bool) - Default: false. Return all the details of the local 
        controller's switches. By default, returns a link to the local 
        controller's switches' detailed information. 
    Status Codes
      200 OK - no error
      404 Not Found - If local controller lcname doesn't exist.
    Example Request
      GET /api/v1/localcontrollers/ATL
    Example Response
      HTTP/1.1 200 OK
      Content-Type: application/json
      {
        "ATL": {
          "href": "http://awavesdx/api/v1/localcontrollers/ATL",
          "lcip": "10.2.3.4",
          "internalconfig": {
            "href": "http://awavesdx/api/v1/localcontrollers/ATL/internalconfig"},
          "switches": {
            "href": "http://awavesdx/api/v1/localcontrollers/ATL/switches",
            "links": {
              "atlsw1": {
                "href": "http://awavesdx/api/v1/localcontrollers/ATL/switches/atlsw1"},
              "atlsw2": {
                "href": "http://awavesdx/api/v1/localcontrollers/ATL/switches/atlsw2"}}}
          "operator": {
            "organization": "Georgia Tech/RNOC",
            "administrator": "Sean Donovan",
            "contact": "sdonovan@gatech.edu"}
        }
      }
    '''
    @staticmethod
    @app.route(EP_LOCALCONTROLLERLC, methods=['GET'])
    def v1localcontrollersspecific(lcname):
        retdict =  {}
        # Get topology
        topo = TopologyManager().get_topology()            
        for node_id in topo.nodes():
            node = topo.node[node_id]
            if (node_id == lcname and
                node['type'] == 'localcontroller'):
                # Add that LC to the dictionary
                base_url = request.base_url
                retdict[node_id] = {'href':base_url}
                retdict[node_id]['lcip'] = node['ip']
                retdict[node_id]['internalconfig'] = {'href':
                                            base_url + "/internalconfig"}
                retdict[node_id]['operator'] = {'organization': node['org'],
                                       'administrator': node['administrator'],
                                       'contact' : node['contact']}
                # Add links to each switch
                retdict[node_id]['switches'] = {'href':
                                            base_url + "/switches"}
                for switch in node['switches']:
                    swdict = {'href': base_url + "/switches/" + switch}
                    ##### QUERY details = True #####
                    if (request.args.get('details') == 'true' or
                        request.args.get('details') == 'True'):
                        swnode = topo.node[switch]
                        swdict['friendlyname'] = swnode['friendlyname']
                        swdict['ip'] = swnode['ip']
                        swdict['dpid'] = swnode['dpid']
                        swdict['brand'] = swnode['brand']
                        swdict['model'] = swnode['model']

                        swdict['ports'] = {'href':base_url + "/switches/" +
                                           switch + "/ports"}
                        for neighbor in topo.neighbors(switch):
                            portnum = topo.edge[switch][neighbor][switch]
                            pns = "port"+str(portnum)
                            portinfo = topo.edge[switch][neighbor]
                            swdict['ports'][pns] = {'href':
                                        base_url + "/switches/" + switch +
                                        "/ports/" + str(portnum),
                                        'portnumber':portnum}
                    
                    retdict[node_id]['switches'][switch] = swdict
                                                                        
                                                

        # If they requested a JSON, send back the raw JSON
        if request_wants_json(request):
            return json.dumps(retdict)
        # HTML output
        return flask.render_template('localcontrollersspecific.html',
                                     lcdict=retdict)




    '''
    GET /api/v1/localcontrollers/<lcname>/internalconfig
      Details of a local controller's internal configuration.
    Query Parameters
      N/A
    Status Codes
      200 OK - no error
      403 Forbidden - if a non-local administrator or non-global administrator 
        attempts to view the internal configuration information, this is 
        returned.
    Example Request
      GET /api/v1/localcontrollers/ATL/internalconfig
    Example Response
      HTTP/1.1 200 OK
      Content-Type: application/json
      {
        "ATL": {
          "href": "http://awavesdx/api/v1/localcontrollers/ATL/internalconfig",
          "internalconfig": {
            "ryucxninternalport": 55780,
            "openflowport": 6680
          }
        }
      }
    '''
    @staticmethod
    @login_required
    @app.route(EP_LOCALCONTROLLERLCINT, methods=['GET'])
    def v1localcontrollersspecificinternalconfig(lcname):
        if not flask_login.current_user.is_authenticated:
            print "Not Authenticated!"
            return make_response(jsonify({'error': 'User Not Authenticated'}),
                                 403)            

        retdict = {}
        # Get the topology first
        topo = TopologyManager().get_topology()            
        for node_id in topo.nodes():
            node = topo.node[node_id]
            if (node_id == lcname and
                node['type'] == 'localcontroller'):
                # For the particular LC, get the internal configuration
                base_url = request.base_url
                retdict[node_id] = {'href':base_url}
                retdict[node_id]['internalconfig'] = node['internalconfig']

        # If they requested a JSON, send back the raw JSON
        if request_wants_json(request):
            return json.dumps(retdict)
        # HTML output
        return flask.render_template(
            'localcontrollersspecificinternalconfig.html',
             config=retdict)



    '''
    GET /api/v1/localcontrollers/<lcname>/switches
      List of switches associated with lcname.
    Query Parameters
      details (bool) - Default: false. Return all the details of the local 
        controller's switches. By default, returns a link to the local 
        controller's switches' detailed information. 
    Status Codes
      200 OK - no error
      403 Forbidden - if a non-local administrator or non-global administrator 
        attempts to view the internal configuration information, this is 
        returned.
    Example Request
      GET /api/v1/localcontrollers/ATL/switches
    Example Response
      HTTP/1.1 200 OK
      Content-Type: application/json
      {
        "href": "http://awavesdx/api/v1/localcontrollers/ATL/switches/",
        "links": {
          "atlsw1": {
            "href": "http://awavesdx/api/v1/localcontrollers/ATL/switches/atlsw1"},
          "atlsw2": {
            "href": "http://awavesdx/api/v1/localcontrollers/ATL/switches/atlsw2"}
        }
      }
    ''' 
    @staticmethod
    @login_required
    @app.route(EP_LOCALCONTROLLERLCSW, methods=['GET'])
    def v1localcontrollersspecificswitches(lcname):
        if not flask_login.current_user.is_authenticated:
            print "Not Authenticated!"
            return make_response(jsonify({'error': 'User Not Authenticated'}),
                                 403)            
                    
        retdict = {}
        # Get the topology first
        topo = TopologyManager().get_topology()            
        for node_id in topo.nodes():
            node = topo.node[node_id]
            if (node_id == lcname and
                node['type'] == 'localcontroller'):
                # For the particular LC, get the internal configuration
                base_url = request.base_url
                retdict[node_id] = {'href':base_url}
                # Add links to each switch:
                retdict[node_id]['links'] = {}
                for switch in node['switches']:
                    swdict = {'href': base_url + "/" + switch}
                    ##### Query details = True #####
                    if (request.args.get('details') == 'true' or
                        request.args.get('details') == 'True'):
                        swnode = topo.node[switch]
                        swdict['friendlyname'] = swnode['friendlyname']
                        swdict['ip'] = swnode['ip']
                        swdict['dpid'] = swnode['dpid']
                        swdict['brand'] = swnode['brand']
                        swdict['model'] = swnode['model']

                        swdict['ports'] = {'href':base_url +
                                           switch + "/ports"}
                        for neighbor in topo.neighbors(switch):
                            portnum = topo.edge[switch][neighbor][switch]
                            pns = "port"+str(portnum)
                            portinfo = topo.edge[switch][neighbor]
                            swdict['ports'][pns] = {'href':
                                        base_url + switch +
                                        "/ports/" + str(portnum),
                                        'portnumber':portnum}
                    
                    retdict[node_id]['links'][switch] = swdict

        # If they requested a JSON, send back the raw JSON
        if request_wants_json(request):
            return json.dumps(retdict)
        # HTML output
        return flask.render_template('localcontrollersspecificswitches.html',
                                     lcdict=retdict)


    '''
    GET /api/v1/localcontrollers/<lcname>/switches/<switchname>
      Returns details on switch switchname that belongs to local controller 
      lcname.
    Query Parameters
      details (bool) - Default: false. Return all the details of the switch's 
      ports. By default, returns a link to the switch's ports' detailed 
      information. 
    Status Codes
      200 OK - no error
      403 Forbidden - if a non-local administrator or non-global administrator 
        attempts to view the internal configuration information, this is 
        returned.
    Example Request
      GET /api/v1/localcontrollers/ATL/switches/atlsw1
    Example Response
      HTTP/1.1 200 OK
      Content-Type: application/json
      {
        "atlsw1": {
          "href": "http://awavesdx/api/v1/localcontrollers/ATL/switches/atlsw1"}
          "friendlyname":"Atlanta Switch 1",
          "ip": "10.2.3.20",
          "dpid": "1",
          "brand": "Corsa",
          "model": "DP2200 Software version 3.0.2",
          "ports": {
            "href":  "http://awavesdx/api/v1/localcontrollers/ATL/switches/atlsw1/ports"},
            "port1": {
              "portnumber": 1,
              "href": "http://awavesdx/api/v1/localcontrollers/ATL/switches/atlsw1/ports/1"},
            "port2": {
              "portnumber": 2,
              "href": "http://awavesdx/api/v1/localcontrollers/ATL/switches/atlsw1/ports/2"},
            "port3": {
              "portnumber": 3,
              "href": "http://awavesdx/api/v1/localcontrollers/ATL/switches/atlsw1/ports/3"},
            "port4": {
              "portnumber": 4,
              "href": "http://awavesdx/api/v1/localcontrollers/ATL/switches/atlsw1/ports/4"}
          }
        }
      }
    '''
    @staticmethod
    @login_required
    @app.route(EP_LOCALCONTROLLERLCSWSPEC, methods=['GET'])
    def v1localcontrollersspecificswitchesspecific(lcname, switchname):
        if not flask_login.current_user.is_authenticated:
            print "Not Authenticated!"
            return make_response(jsonify({'error': 'User Not Authenticated'}),
                                 403)            
                            
        retdict = {}
        # Get the topology first
        topo = TopologyManager().get_topology()            
        for node_id in topo.nodes():
            node = topo.node[node_id]
            if (node_id == switchname and
                node['type'] == 'switch' and
                node['lcname'] == lcname):

                # Found the correct node, 
                base_url = request.base_url
                retdict[node_id] = {'href':base_url}
                retdict[node_id]['friendlyname'] = node['friendlyname']
                retdict[node_id]['ip'] = node['ip']
                retdict[node_id]['dpid'] = node['dpid']
                retdict[node_id]['brand'] = node['brand']
                retdict[node_id]['model'] = node['model']

                # Per-port information
                portsdict = {'href':base_url + "/ports"}
                for neighbor in topo.neighbors(node_id):
                    # Need to extract the port info out of this
                    portnum = topo.edge[node_id][neighbor][node_id]
                    pns = "port"+str(portnum) # port number string
                    portinfo = topo.edge[node_id][neighbor]
                    ##### QUERY details = True #####
                    if (request.args.get('details') == 'true' or
                        request.args.get('details') == 'True'):
                        portsdict[pns] = {'href':
                                          base_url + "/ports/" + str(portnum),
                                          'portnumber': portnum,
                                          'speed': portinfo['weight'],
                                          'destination': neighbor,
                                          'vlansinuse':
                                          portinfo['vlans_in_use'],
                                          'bwinuse': portinfo['bw_in_use']}
                    ##### QUERY details = False/None #####
                    else:
                        portsdict[pns] = {'href':
                                          base_url + "/ports/" + str(portnum),
                                          'portnumber':portnum}

                retdict[node_id]['ports'] = portsdict
                
        # If they requested a JSON, send back the raw JSON
        if request_wants_json(request):
            return json.dumps(retdict)
        # HTML output
        return flask.render_template(
            'localcontrollersspecificswitchesspecific.html',
                                     lcdict=retdict)

    '''
    GET /api/v1/localcontrollers/<lcname>/switches/<switchname>/ports
      List of ports associated with switchname.
    Query Parameters
      details (bool) - Default: false. Return all the details of the switch's 
      ports. By default, returns a link to the local switch's ports' detailed 
      information. 
    Status Codes
      200 OK - no error
      403 Forbidden - if a non-local administrator or non-global administrator 
        attempts to view the internal configuration information, this is 
        returned.
    Example Request
      GET /api/v1/localcontrollers/ATL/switches/atlsw1/ports
    Example Response
      HTTP/1.1 200 OK
      Content-Type: application/json
      {
        "href": "http://awavesdx/api/v1/localcontrollers/ATL/switches/atlsw1/ports"}
        "links": {
          "port1": {
            "portnumber": 1,
            "href": "http://awavesdx/api/v1/localcontrollers/ATL/switches/atlsw1/ports/1"},
          "port2": {
            "portnumber": 2,
            "href": "http://awavesdx/api/v1/localcontrollers/ATL/switches/atlsw1/ports/2"},
          "port3": {
            "portnumber": 3,
            "href": "http://awavesdx/api/v1/localcontrollers/ATL/switches/atlsw1/ports/3"},
          "port4": {
            "portnumber": 4,
            "href": "http://awavesdx/api/v1/localcontrollers/ATL/switches/atlsw1/ports/4"}
      }
    '''
    @staticmethod
    @login_required
    @app.route(EP_LOCALCONTROLLERLCSWSPECPORT, methods=['GET'])
    def v1localcontrollersspecificswitchesspecificports(lcname, switchname):
        if not flask_login.current_user.is_authenticated:
            print "Not Authenticated!"
            return make_response(jsonify({'error': 'User Not Authenticated'}),
                                 403)            
                    
        retdict = {}
        # Get the topology first
        topo = TopologyManager().get_topology()            
        for node_id in topo.nodes():
            node = topo.node[node_id]
            if (node_id == switchname and
                node['type'] == 'switch' and
                node['lcname'] == lcname):

                # Found the correct node, 
                base_url = request.base_url
                retdict['href'] = base_url
                
                # Per-port information
                portsdict = {}
                for neighbor in topo.neighbors(node_id):
                    # Need to extract the port info out of this
                    portnum = topo.edge[node_id][neighbor][node_id]
                    pns = "port"+str(portnum) # port number string
                    portinfo = topo.edge[node_id][neighbor]
                    ##### QUERY details = True #####
                    if (request.args.get('details') == 'true' or
                        request.args.get('details') == 'True'):
                        portsdict[pns] = {'href':
                                          base_url + "/" + str(portnum),
                                          'portnumber': portnum,
                                          'speed': portinfo['weight'],
                                          'destination': neighbor,
                                          'vlansinuse':
                                          portinfo['vlans_in_use'],
                                          'bwinuse': portinfo['bw_in_use']}
                    ##### QUERY details = False/None #####
                    else:
                        portsdict[pns] = {'href':
                                          base_url + "/" + str(portnum),
                                          'portnumber':portnum}
                retdict['links'] = portsdict

        # If they requested a JSON, send back the raw JSON
        if request_wants_json(request):
            return json.dumps(retdict)
        # HTML output
        return flask.render_template(
            'localcontrollersspecificswitchspecificports.html',
            lcdict=retdict)

    '''
    GET /api/v1/localcontrollers/<lcname>/switches/<switchname>/ports/<portnumber>
      Details of port portnumber belonging to switchname. speed is in bits per 
      second
    Query Parameters
      N/A
    Status Codes
      200 OK - no error
      403 Forbidden - if a non-local administrator or non-global administrator 
        attempts to view the internal configuration information, this is 
        returned.
    Example Request
      GET /api/v1/localcontrollers/ATL/switches/atlsw1/ports/1
    Example Response
      HTTP/1.1 200 OK
      Content-Type: application/json
      {
        "port1": {
          "href": "http://awavesdx/api/v1/localcontrollers/ATL/switches/atlsw1/ports/1",
          "portnumber": 1,
          "speed": 800000000,
          "destination": "atldtn"
        }
      }
    '''
    @staticmethod
    @app.route(EP_LOCALCONTROLLERLCSWSPECPORTSPEC,
               methods=['GET'])
    def v1localcontrollersspecificswitchesspecificportsspecific(lcname,
                                                                switchname,
                                                                portnumber):
        if not flask_login.current_user.is_authenticated:
            print "Not Authenticated!"
            return make_response(jsonify({'error': 'User Not Authenticated'}),
                                 403)            
                    
        retdict = {}
        # Get the topology first
        topo = TopologyManager().get_topology()            
        for node_id in topo.nodes():
            node = topo.node[node_id]
            if (node_id == switchname and
                node['type'] == 'switch' and
                node['lcname'] == lcname):

                # Found the correct node, 
                base_url = request.base_url

                # Find the correct port next
                for neighbor in topo.neighbors(node_id):
                    # Need to extract the port info out of this
                    portnum = topo.edge[node_id][neighbor][node_id]
                    if portnum != int(portnumber): continue

                    pns = "port"+str(portnum) # port number string
                    portinfo = topo.edge[node_id][neighbor]
                    retdict[pns] = {'href': base_url,
                                    'portnumber': portnum,
                                    'speed': portinfo['weight'],
                                    'destination': neighbor,
                                    'vlansinuse': portinfo['vlans_in_use'],
                                    'bwinuse': portinfo['bw_in_use']}

        # If they requested a JSON, send back the raw JSON
        if request_wants_json(request):
            return json.dumps(retdict)
        # HTML output
        return flask.render_template(
            'localcontrollersspecificswitchesspecificportsspecific.html',
            lcdict=retdict)

    '''
    GET /api/v1/users/
      List all users. Administrators are able to view all users, while regular 
      users are only able to see themselves. 
    Query Parameters
      details (bool) - Default: false. Return all the details of the users. May
        produce very large results.
    Status Codes
      200 OK - no error
       403 Forbidden - if a non-local administrator or non-global administrator 
        attempts to view the internal configuration information, this is 
        returned.
    Example Request
      GET /api/v1/users
    Example Response
      HTTP/1.1 200 OK
      Content-Type: application/json
      {
        "href": "http://awavesdx/api/v1/users
        "links": {
          "sdonovan": {	
            "href": "http://awavesdx/api/v1/users/sdonovan",
            "type":"administrator",
            "organization":"sox",
            "policies": 
              {"href":"http://awavesdx/api/v1/users/sdonovan/policies"},
            "permissions": 
              {"href":"http://awavesdx/api/v1/users/sdonovan/permissions"}},
          "jchung": {
            "href": "http://awavesdx/api/v1/users/jchung",
            "type":"user",
            "organization":"georgiatech",
            "policies": 
              {"href":"http://awavesdx/api/v1/users/jchung/policies"},
            "permissions": 
              {"href":"http://awavesdx/api/v1/users/jchung/permissions"}}
        }
      }
    '''
    @staticmethod
    @login_required
    @app.route(EP_USERS, methods=['GET'])
    def v1users():
        if not flask_login.current_user.is_authenticated:
            print "Not Authenticated!"
            return make_response(jsonify({'error': 'User Not Authenticated'}),
                                 403)            
           
        base_url = request.base_url
        retdict = {'href':base_url, 'links':{}}
        # Get all the users
        users = UserManager.get_users()
        for user in users:
            un = user['username']
            retdict['links'][un] = {'href': base_url + "/" + un,
                                    'type': user['type'],
                                    'organization': user['organization']}
            perms = {'href':base_url + "/" + un + "/permissions"}
            policies = {'href':base_url + "/" + un + "/policies"}

            ##### QUERY details #####
            if (request.args.get('details') == 'true' or
                request.args.get('details') == 'True'):
                # Permissions - FIXME
                user['permitted_actions']
                # Policies
                policies = PolicyManager().get_policies({'user':un})
                policy_url = request.url_root[:-1] + EP_POLICIES + "/number/"

                for policy in policies:
                    (policy_hash, jsonpolicy, policytype,
                     username, state) = policy
                    policies['policy'+str(policy_hash)] = {'href':
                                    policy_url + str(policy_hash),
                                    'policynumber':policy_hash,
                                    'user':un,
                                    'type':policytype}
                    
            # Add permissions and policies to the user 
            retdict['links'][un]['permissions'] = perms
            retdict['links'][un]['policies'] = policies
        # If they requested a JSON, send back the raw JSON
        if request_wants_json(request):
            return json.dumps(retdict)
        # HTML output
        return flask.render_template('users.html', userdict=retdict)


    '''
    GET /api/v1/users/<username>
      Show an individual user. Administrators are able to view all users, while
      regular users are only able to see themselves. 
    Query Parameters
      details (bool) - Default: false. Return all the details of the users.
    Status Codes
      200 OK - no error
      403 Forbidden - if a non-local administrator or non-global administrator 
        attempts to view the internal configuration information, this is 
        returned.
    Example Request
      GET /api/v1/users/sdonovan
    Example Response
      HTTP/1.1 200 OK
      Content-Type: application/json
      {
        "href": "http://awavesdx/api/v1/users/sdonovan",
        "sdonovan": {	
          "href": "http://awavesdx/api/v1/users/sdonovan",
          "type":"administrator",
          "organization":"sox",
          "policies": 
              {"href":"http://awavesdx/api/v1/users/sdonovan/policies"},
          "permissions": 
              {"href":"http://awavesdx/api/v1/users/sdonovan/permissions"}
        }
      }
    '''
    @staticmethod
    @login_required
    @app.route(EP_USERSSPEC, methods=['GET'])
    def v1usersspec(username):
        if not flask_login.current_user.is_authenticated:
            print "Not Authenticated!"
            return make_response(jsonify({'error': 'User Not Authenticated'}),
                                 403)            

        retdict = {}
        base_url = request.base_url
        retdict = {'href':base_url}
        # Get specific user
        user = UserManager().get_user(username)
        retdict[username] = {'href': base_url,
                             'type': user['type'],
                             'organization': user['organization']}
        perms = {'href':base_url + "/permissions"}
        policies = {'href':base_url + "/policies"}

        ##### QUERY details #####
        if (request.args.get('details') == 'true' or
            request.args.get('details') == 'True'):
            # Permissions - FIXME
            user['permitted_actions']
            # Policies
            policies = PolicyManager().get_policies({'user':username})
            policy_url = request.url_root[:-1] + EP_POLICIES + "/number/"

            for policy in policies:
                (policy_hash, jsonpolicy, policytype, un, state) = policy
                policies['policy'+str(policy_hash)] = {'href':
                                    policy_url + str(policy_hash),
                                    'policynumber':policy_hash,
                                    'user':username,
                                    'type':policytype}
                    
        # Add permissions and policies to the user 
        retdict[username]['permissions'] = perms
        retdict[username]['policies'] = policies
            
        # If they requested a JSON, send back the raw JSON
        if request_wants_json(request):
            return json.dumps(retdict)
        # HTML output
        return flask.render_template('usersspec.html', userdict=retdict)
    

    '''
    GET /api/v1/users/<username>/permissions
      Retrieves permissions about a single user, username.
    Query Parameters
      N/A
    Status Codes
      200 OK - no error
      403 Forbidden - This is for when a regular user attempts to view 
        another user's permissions that they are not authorized to view.
      404 Not Found - This is for when a user attempts to find a user  that does
        not exist

    Example Request
      GET /api/v1/users/sdonovan/permissions
    Example Response
      HTTP/1.1 200 OK
      Content-Type: application/json
      {
        "sdonovan": {	
          "href":"http://awavesdx/api/v1/users/sdonovan/permissions",
          FIXME
      }
    '''
    @staticmethod
    @login_required
    @app.route(EP_USERSSPECPERMISSIONS, methods=['GET'])
    def v1usersspecperms(username):
        if not flask_login.current_user.is_authenticated:
            print "Not Authenticated!"
            return make_response(jsonify({'error': 'User Not Authenticated'}),
                                 403)
        
        retdict = {}
        base_url = request.base_url
        retdict = {}
        # Get specific user
        user = UserManager().get_user(username)
        retdict[username] = {'href': base_url}

        #FIXME - Once this is squared away, this needs to be written.
        retdict[username]['permissions'] = user['permitted_actions']
        
        # If they requested a JSON, send back the raw JSON
        if request_wants_json(request):
            return json.dumps(retdict)
        # HTML output
        return flask.render_template('usersspecperms.html', userdict=retdict)

    '''
    GET /api/v1/users/<username>/policies
      Retrieves policies created/owned by a single user, username.
    Query Parameters
      type (string) - Filter based on a policy type. See the endpoint 
        /api/v1/policies/type/ for a list of policies. 
    Status Codes
      200 OK - no error
      403 Forbidden - This is for when a regular user attempts to view 
        another user's permissions that they are not authorized to view.
      404 Not Found - This is for when a user attempts to find a policy that 
        does not exist

    Example Request
      GET /api/v1/users/sdonovan/policies
    Example Response
      HTTP/1.1 200 OK
      Content-Type: application/json
      {
        "sdonovan": {
          "href":"http://awavesdx/api/v1/users/sdonovan/policies",
          "policies": {
            "policy2": {	
              "href": "http://awavesdx/api/v1/policy/number/2",
              "policynumber": 2,
              "user":"sdonovan",
              "type":"l2tunnel"},
            "policy3": {
              "href": "http://awavesdx/api/v1/policy/number/3",
              "policynumber": 3,
              "user":"sdonovan",
              "type":"l2multipoint"}
          }
        }
      }
    '''
    @staticmethod
    @login_required
    @app.route(EP_USERSSPECPOLICIES, methods=['GET'])
    def v1usersspecpolicies(username):
        if not flask_login.current_user.is_authenticated:
            print "Not Authenticated!"
            return make_response(jsonify({'error': 'User Not Authenticated'}),
                                 403)
        
        base_url = request.base_url
        retdict = {}
        # Get specific user
        user = UserManager().get_user(username)
        retdict[username] = {'href': base_url,
                             'policies':{}}

        # Get Policies
        query = {'user':username}
        ##### QEURY type #####
        if (request.args.get('type') != None):
            query['policytype'] = request.args.get('type')
        
        policies = PolicyManager().get_policies(query)
        policy_url = request.url_root[:-1] + EP_POLICIES + "/number/"

        for policy in policies:
            (policy_hash, jsonpolicy, policytype, user, state) = policy
            retdict[username]['policies']['policy'+str(policy_hash)] = {'href':
                                    policy_url + str(policy_hash),
                                    'policynumber':policy_hash,
                                    'user':username,
                                    'type':policytype}

        # If they requested a JSON, send back the raw JSON
        if request_wants_json(request):
            return json.dumps(retdict)
        # HTML output
        return flask.render_template('usersspecpolicies.html', userdict=retdict)


    '''
    GET /api/v1/policies/
      List all visible policies. Administrators are able to view all policies, 
      while regular users are only able to see their own policies. 
    Query Parameters
      details (bool) - Default: false. Return all the details of the policies. 
        May produce very large results.
      FIXME
    Status Codes
      200 OK - no error

    Example Request
      GET /api/v1/policies
    Example Response
      HTTP/1.1 200 OK
      Content-Type: application/json
      {
        "href": "http://awavesdx/api/v1/policies",
        "links": {
          "policy2": {	
            "href": "http://awavesdx/api/v1/policies/number/2",
            "policynumber": 2,
            "user":"sdonovan",
            "type":"l2tunnel"
          },
          "policy3": {
            "href": "http://awavesdx/api/v1/policies/number/3",
            "policynumber": 3,
            "user":"sdonovan",
            "type":"l2multipoint"
        }
      }
    '''
    @staticmethod
    @login_required
    @app.route(EP_POLICIES, methods=['GET'])
    def v1policies():
        if not flask_login.current_user.is_authenticated:
            print "Not Authenticated!"
            return make_response(jsonify({'error': 'User Not Authenticated'}),
                                 403)           
        base_url = request.base_url
        retdict = {'href': base_url, 'links':{}}

        # Get all the policies:
        policies = PolicyManager().get_policies()
        policy_url = base_url + "/number/"

        for policy in policies:
            (policy_hash, jsonpolicy, policytype, username, state) = policy
            policy = {'href':policy_url + str(policy_hash),
                      'policynumber':policy_hash,
                      'user':username,
                      'type':policytype}
            retdict['links']['policy'+str(policy_hash)] = policy
            
        # If they requested a JSON, send back the raw JSON
        if request_wants_json(request):
            return json.dumps(retdict)
        # HTML output
        return flask.render_template('policies.html',
                                     policydict=retdict)


    '''
    GET /api/v1/policies/number/<policynumber>
      Get details of a given policy specified by policynumber. Each policy type 
      will return different style of information, so we've sequestered the 
      details into a sub-piece
    Query Parameters
      N/A
    Status Codes
      200 OK - no error
      403 Forbidden - This is for when a regular user attempts to view 
        another user's policy that they are not authorized to view.
      404 Not Found - This is for when a user attempts to find a policy that 
        does not exist
      410 Gone - FIXME - should we use this?

    Example Request
      GET /api/v1/policies/number/5
    Example Response
      HTTP/1.1 200 OK
      Content-Type: application/json
      {
        "policy3": {
          "href": "http://awavesdx/api/v1/policies/number/3",
          "policynumber": 3,
          "user":"sdonovan",
          "type":"l2multipoint",
          "json":"{
            "l2multipoint":{
              "starttime":"1985-04-12T23:20:50",
              "endtime":"1985-04-12T23:20:50+0400",
              "endpoints": [ {"switch":"mia-switch", 
                              "port":5, 
                              "vlan":286},
                             {"switch":"atl-switch", 
                              "port":3, 
                              "vlan":1856},
                             {"switch":"gru-switch", 
                              "port":4, 
                              "vlan":3332} ],
                           "Bandwidth":1000}
          }
        }
      }
    '''
    @staticmethod
    @login_required
    @app.route(EP_POLICIESSPEC, methods=['GET'])
    def v1policiesspec(policynumber):
        if not flask_login.current_user.is_authenticated:
            print "Not Authenticated!"
            return make_response(jsonify({'error': 'User Not Authenticated'}),
                                 403)
        
        base_url = request.base_url
        retdict = {}

        # Get all the policies:
        policy = PolicyManager().get_policy_details(policynumber)
        if policy == None:
            #FIXME - proper response
            if request_wants_json(request):
                return make_response(jsonify({'error': 'Not found'}), 404)
            # HTML output
            return make_response(jsonify({'error': 'Not found'}), 404)

        (policy_hash, jsonpolicy, policytype, state, user, breakdowns) = policy
        policy = {'href':base_url,
                  'policynumber':policy_hash,
                  'user':user,
                  'type':policytype,
                  'json':jsonpolicy}
        retdict['policy'+str(policy_hash)] = policy
            
        # If they requested a JSON, send back the raw JSON
        if request_wants_json(request):
            return json.dumps(retdict)
        # HTML output
        return flask.render_template('policiesspec.html', policydict=retdict)
        # else: fancy HTML
        detail = PolicyManager().get_policy_details(policy_hash)
        return flask.render_template('details.html', detail = detail)
        
    '''
    DELETE /api/v1/policies/number/<policynumber>
      Deletes a given policy specified by policynumber. 
    Query Parameters
      N/A
    Status Codes
      204 No Content - no error
      403 Forbidden - This is for when a regular user attempts to view 
        another user's policy that they are not authorized to view.
      404 Not Found - This is for when a user attempts to find a policy that 
        does not exist
      410 Gone - FIXME - should we use this?

    Example Request
      DELETE /api/v1/policies/number/5
    Example Response
      HTTP/1.1 204 No Content
    '''
    @staticmethod
    @login_required
    @app.route(EP_POLICIESSPEC, methods=['DELETE'])
    def v1policiesspecDEL(policynumber):
        if not flask_login.current_user.is_authenticated:
            print "Not Authenticated!"
            return make_response(jsonify({'error': 'User Not Authenticated'}),
                                 403)
        
        policy = PolicyManager().get_policy_details(policynumber)
        if policy == None:
            #FIXME - proper response
            if request_wants_json(request):
                return make_response(jsonify({'error': 'Not found'}), 404)
            #FIXME:  NEED HTML response written
            return make_response(jsonify({'error': 'Not found'}), 404)        

        # Delete policy
        (policy_hash, jsonpolicy, policytype, state, user, breakdowns) = policy
        PolicyManager().remove_policy(policy_hash, user)

        #FIXME - proper response
        if request_wants_json(request):
            return make_response(jsonify({}), 204)
        #FIXME:  NEED HTML response written
        return make_response(jsonify({}), 204) 

    '''
    GET /api/v1/policies/type
      Get the list of different types of policies. This has two functions: easy
      to walk thorugh the different policy types, and easy way for a user to see
      if there are new functions and how to use them.
    Query Parameters
      N/A
    Status Codes
      200 OK - no error

    Example Request
      GET /api/v1/policies/type
    Example Response
      HTTP/1.1 200 OK
      Content-Type: application/json
      {
        "href": "http://awavesdx/api/v1/policies/type",
        "l2tunnel": {
          "type": "l2tunnel",
          "href": "http://awavesdx/api/v1/policies/type/l2tunnel",
          "example": 
            "http://awavesdx/api/v1/policies/type/l2tunnel/example.html"},
        "l2multipoint": {
          "type": "l2multipoint",
          "href": "http://awavesdx/api/v1/policies/type/l2multipoint",
          "example": 
            "http://awavesdx/api/v1/policies/type/l2multipoint/example.html"},
        "sdxingress": {
          "type": "sdxingress",
          "href": "http://awavesdx/api/v1/policies/type/sdxingress",
          "example": 
            "http://awavesdx/api/v1/policies/type/sdxingress/example.html"},
        "sdxegress": {
          "type": "sdxegress",
          "href": "http://awavesdx/api/v1/policies/type/sdxegress",
          "example": 
            "http://awavesdx/api/v1/policies/type/sdxegress/example.html"}
       }
    '''
    @staticmethod
    @app.route(EP_POLICIESTYPE, methods=['GET'])
    def v1policiestype():
        base_url = request.base_url
        retdict = {'href':base_url}
        policies = PolicyRegistry().get_list_of_policies()

        for policy in policies:
            p = {'type':policy,
                 'href':base_url + "/" + policy,
                 'example': base_url + "/" + policy + "/example.html"}
            retdict[policy] = p
            

        # If they requested a JSON, send back the raw JSON
        if request_wants_json(request):
            return json.dumps(retdict)
        # HTML output
        return flask.render_template('policiestype.html', policydict=retdict)


    '''
    GET /api/v1/policies/type/<policytype>
      Get the list of policies of type policytype that the user has access to. 
      This is a filtered version of the /api/v1/policies endpoint. 
    Query Parameters
      FIXME
    Status Codes
      403 Forbidden -  if a non-local administrator or non-global administrator 
        attempts to view the internal configuration information, this is 
        returned.
      200 OK - no error

    Example Request
      GET /api/v1/policies/type/l2tunnel
    Example Response
      HTTP/1.1 200 OK
      Content-Type: application/json
      {
        "href": "http://awavesdx/api/v1/policies/type/l2tunnel",
        "policy3": {
          "href": "http://awavesdx/api/v1/policies/number/3",
          "policynumber": 3,
          "user":"sdonovan",
          "type":"l2tunnel",
          "json":"{
            "l2tunnel":{
              "starttime":"1985-04-12T23:20:50",
              "endtime":"1985-04-12T23:20:50+0400",
              "srcswitch":"atl-switch",
              "dstswitch":"mia-switch",
              "srcport":5,
              "dstport":7,
              "srcvlan":1492,
              "dstvlan":1789,
              "bandwidth":1}
            }
          }
        }
    '''
    @staticmethod
    @login_required
    @app.route(EP_POLICIESTYPESPEC, methods=['GET'])
    def v1policiestypespec(policytype):
        if not flask_login.current_user.is_authenticated:
            print "Not Authenticated!"
            return make_response(jsonify({'error': 'User Not Authenticated'}),
                                 403)            

        base_url = request.base_url
        retdict = {'href': base_url}

        # Get all the policies:
        policies = PolicyManager().get_policies()
        policy_url = request.url_root[:-1] + EP_POLICIES + "/number/"

        for policy in policies:
            (policy_hash, jsonpolicy, policytype, username, state) = policy
            if policytype == policytype:
                policy = {'href':policy_url + str(policy_hash),
                          'policynumber':policy_hash,
                          'user':username,
                          'type':policytype}
                retdict['policy'+str(policy_hash)] = policy
            
        # If they requested a JSON, send back the raw JSON
        if request_wants_json(request):
            return json.dumps(retdict)
        # HTML output
        return flask.render_template('policiestypespec.html',
                                     policydict=retdict,
                                     policytype=policytype)
    '''
    GET /api/v1/policies/type/<policytype>/example.html
      This endpoint returns an HTML file describing an example for creating that
      policy type. This is meant to be human readable and is not directly part 
      of the REST API. This is meant for developers to manually request 
      particular policy type information, such that they can use the REST API 
      more effectively.
    '''
    @staticmethod
    @app.route(EP_POLICIESTYPESPECEXAMPLE, methods=['GET'])
    def v1policiestypeexample(policytype):
        pr = PolicyRegistry()
        try:
            html = pr.get_policy_class(policytype).get_html_help()
            return html
            
        except TypeError as e:
            #FIXME - proper response
            if request_wants_json(request):
                return make_response(jsonify({}), 404)
            #FIXME:  NEED HTML response written
            return make_response(jsonify({}), 404) 

        
    ##### SPECIFIC POLICY POSTS #####


    '''
    POST /api/v1/policies/type/<policytype>
      This endpoint is used for creating new policies of type <policytype>. See
      individual example.html file for how to create each of these.
    '''
    @staticmethod
    @login_required
    @app.route(EP_POLICIESTYPESPEC, methods=['POST'])
    def v1policiestypespecpost(policytype):
        RestAPI().logger.info("POST new policy type %s" % policytype)

        if not flask_login.current_user.is_authenticated:
            print "Not Authenticated!"
            return make_response(jsonify({'error': 'User Not Authenticated'}),
                                 403)
        '''
        Helper function that's used to preprocess incoming data from form
        '''        
        def _parse_post_data(data_json):
            print data_json
            if "L2Multipoint" in data_json.keys():
                # This parses out the individual "multipointelements" and
                # reinserts them into the data_json object
                count = int(data_json['L2Multipoint'].pop('count'))
                data_json['L2Multipoint']['endpoints']=[]
                for i in range(1,count+1):
                    element = data_json['L2Multipoint'].pop(
                        'multipointelement_'+str(i))
                    (node, portstr, vlanstr) = str(element).split(',')
                    data_json['L2Multipoint']['endpoints'].append(
                        {"switch":node,
                         "port":int(portstr),
                         "vlan":int(vlanstr)})
            elif ("SDXEgress" in data_json.keys() or
                  "SDXIngress" in data_json.keys()):
                if "SDXEgress" in data_json.keys():
                    pol = "SDXEgress"
                    # See SDXPolicy.py for source of this list
                    types = {'src_mac':str, 'src_ip':str,
                             'tcp_src':int, 'udp_src':int,
                             'dst_mac':str, 'dst_ip':str,
                             'tcp_dst':int, 'udp_dst':int,
                             'ip_proto':int, 'eth_type':int, 'vlan':int,
                             'ModifySRCMAC':str, 'ModifySRCIP':str,
                             'ModifyTCPSRC':int, 'ModifyUDPSRC':int,
                             'ModifyVLAN':int}

                else:
                    pol = "SDXIngress"
                    types = {'src_mac':str, 'src_ip':str,
                             'tcp_src':int, 'udp_src':int,
                             'dst_mac':str, 'dst_ip':str,
                             'tcp_dst':int, 'udp_dst':int,
                             'ip_proto':int, 'eth_type':int, 'vlan':int,
                             'ModifyDSTMAC':str, 'ModifyDSTIP':str,
                             'ModifyTCPDST':int, 'ModifyUDPDST':int,
                             'ModifyVLAN':int}
                    no_type = ['Drop', 'Continue']


                match_count = int(data_json[pol].pop('match_count'))
                action_count = int(data_json[pol].pop('action_count'))
                data_json[pol]['matches']=[]
                for i in range(1,match_count+1):
                    element = data_json[pol].pop('match_'+str(i))
                    (m,vstr) = str(element).split(',')
                    # Only somewhat dirty type conversion
                    v = types[m](vstr)
                    data_json[pol]['matches'].append({m:v})
                data_json[pol]['actions']=[]
                for i in range(1,action_count+1):
                    element = data_json[pol].pop('action_'+str(i))
                    if element in no_type:
                        data_json[pol]['actions'].append({element})
                    else:
                        (a,v) = str(element).split(',')
                        data_json[pol]['actions'].append({a:v})
                    
            return data_json


        base_url = request.url_root[:-1] + EP_POLICIES + "/number/"

        userid = flask_login.current_user.id
        RestAPI().logger.info("  - user %s" % userid)

        # Extract out data. Try JSON first.
        data = request.get_json()
        if data != None:
            RestAPI().logger.info("  - JSON data %s" % data)
        
        if data == None:
            # Not JSON, so from the HTML form:
            preprocessed_data = {policytype:(flask.request.form.to_dict())}
            data = _parse_post_data(preprocessed_data)
            RestAPI().logger.info("  - Form data %s" % data)
            
        retdict = {'policy':{'user':userid,
                             'type':policytype,
                             'json':data}}
                             
        # Get UserPolicy
        try:
            policyclass = PolicyRegistry().get_policy_class(policytype)
            RestAPI().dlogger.debug("POST %s: %s" % (policytype, policyclass))
            policyclass.check_syntax(data)
            RestAPI().dlogger.debug("  - check_syntax successful")
            policy = policyclass(userid, data)
            RestAPI().dlogger.debug("  - policy: %s" % policy)
            hashval = PolicyManager().add_policy(policy)
            RestAPI().dlogger.debug("  - hash: %s" % hashval)
            policy_url = base_url + str(hashval)
            retdict['policy']['href'] = policy_url
            #FIXME - proper response
            if request_wants_json(request):
                return make_response(jsonify(retdict), 201)

            # else: HTML
            return flask.redirect(policy_url, code=303)
        
        except PolicyRegistryTypeError:
            #FIXME - proper response
            if request_wants_json(request):
                return make_response(jsonify({}), 404)
            #FIXME:  NEED HTML response written
            return make_response(jsonify({}), 404)

        except Exception as e:
             #FIXME - proper response
            errorstr = str(e)
            RestAPI().dlogger.warning("Exception caught on %s" % policytype)
            RestAPI().exception_tb(e)

            print "\n\nerrorstr %s\ntojsonify %s" % (errorstr, {"Error":str(e)})
            if request_wants_json(request):
                RestAPI().logger.error("POST %s ERROR: %s" % (policyname, e,))
                return make_response(jsonify({"Error":str(e)}), 400)
            #FIXME:  NEED HTML response written
            RestAPI().logger.error("POST %s ERROR: %s" % (policyname, e,))
            return make_response(jsonify({"Error":str(e)}), 400)


    # Login endpoint
    @staticmethod
    @app.route(EP_LOGIN, methods=['GET'])
    def login_form():
        if flask_login.current_user.get_id() == None:
            return app.send_static_file('overhaul/login.html')
        else:
            print "%s already logged in" % flask_login.current_user.get_id() 
            return flask.redirect(EP_LOGOUT)
        
    @staticmethod
    @app.route(EP_LOGIN, methods=['POST'])
    def login():
        # Extract username and password
        if 'username' in flask.request.form.keys():
            username = flask.request.form['username']
            password = flask.request.form['password']
        else:
            data = request.get_json()
            username = data['username']
            password = data['password']
            
        # Check with AuthenticationInspector
        if AuthenticationInspector().is_authenticated(username,
                                                               password):
            # Log user in
            user = User(username)
            flask_login.login_user(user)
            return flask.redirect(EP_LOGOUT, code=303)

        return make_response(jsonify({'error': 'User Not Authenticated'}),
                             403)


    # Logout endpoint
    @staticmethod
    @app.route(EP_LOGOUT, methods=['GET'])
    def logout_form():
        if flask_login.current_user.get_id() == None:
            return flask.redirect(EP_LOGIN)
        else:
            print "%s viewing logout page" % flask_login.current_user.get_id()
            return flask.render_template('logout.html')
        
    @staticmethod
    @login_required
    @app.route(EP_LOGOUT, methods=['POST'])
    def logout():
        flask_login.logout_user()
        return flask.redirect(EP_LOGIN, code=303)

    
    # Unauthorized handler
    @staticmethod
    @login_manager.unauthorized_handler
    def unauthorized_handler():
        return 'Unauthorized'

    # User handler
    @staticmethod
    @login_manager.user_loader
    def user_loader(username):
        user = UserManager().get_user(username)
        if user == None:
            return None

        return User(username)
            

