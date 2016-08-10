# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


from shared.Singleton import Singleton

class LocalControllerManager(object):
    ''' The LocalControllerManager is responsible for keeping track of local 
        controller information, in particular authorization information for 
        different local controllers. In the future, this may also include 
        information as to capabilities present at different local controllers 
        (i.e., different switch capabilities).
        Singleton. '''

    __metaclass__ = Singleton
    
    def __init__(self):
        ''' The bulk of work is handled at initialization and pushing user 
            information to both the AuthenticationInspector and 
            AuthorizationInspector. '''
        pass

    def add_controller(self, controller, credentials):
        ''' This adds users to the LocalControllerManager’s database, which will 
            push information to the AuthenticationInspector and the 
            SDXControllerConnectionManager. '''
        pass

    def new_controller_connection(self, controller):
        ''' When a new local controller connects, this is called, which informs 
            the TopologyManager of the change. ''' 
        #FIXME: what to do? Does this trigger recalculations?
        pass

    def remove_controller_connection(self, controller):
        ''' When a local controller has disconnected, this is called. '''
        #FIXME: what to do? Does this trigger recalculations?
        pass
    
