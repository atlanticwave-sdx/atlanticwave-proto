# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project

class UserPolicyError(Exception):
    pass

class UserPolicyTypeError(TypeError):
    pass

class UserPolicyValueError(ValueError):
    pass

class UserPolicy(object):
    ''' This is the interface between the SDX controller and the user-level 
        application. This will likely be heavily modified over the course of 
        development, more so than most other interfaces. '''


    def __init__(self, username, json_policy):
        ''' Parses the json_policy passed in to populate the UserPolicy. '''
        self.username = username
        self.policytype = self.get_policy_name()
        self.json_policy = json_policy

        # The breakdown list should be a list of UserPolicyBreakdown objects.
        self.breakdown = None
        self.policy_hash = None

        # The resource list should be a list of PathResource children.
        self.resources = []

        # All policies should have start and stop times. They may be
        # rediculously far in the past and/or the future, but the should have
        # them. They should be strings in rfc3339format (see shared.constants).
        self.start_time = None
        self.stop_time = None

        # Now that all the fields are set up, parse the json.
        self._parse_json(self.json_policy)


    @classmethod
    def check_syntax(cls, json_policy):
        ''' Used to validate syntax of json user policies before they are 
            parsed.
            Must be implemented by child classes. '''
        raise NotImplementedError("Subclasses must implement this.")

    @classmethod
    def get_html_help(cls):
        ''' Used to get HTML help. Should be filled in per-policy. By default,
            a "Not User Accessible" message will be returned. User accessible 
            UserPolicys should implement this. '''
        # Find out if there's an <classname>.html file in the doc/ directory
        name = cls.__name__
        if name.startswith("shared."):
            name = name[len("shared."):]
        #FIXME: Magic .. there... The only places that this would be called from
        # are subdirectories, so should be safe to do. Ugly, but should be fine.
        filename = "../doc/" + name + ".html"

        # If so, read and return the string
        try:
            with open(filename) as f:
                data = f.readlines()
                return "".join(data)
        except IOError as e:
            print "Example HTML file %s does not exist." % filename
                    
        # If not:
        return "<html><h1>Not User Accessible</h1></html>"

    @classmethod
    def get_policy_name(cls):
        ''' Returns the Policy's name. '''
        n = cls.__name__

        if n.startswith("shared."):
            n = cls.__name__[len("shared."):]
        if n.endswith("Policy"):
            n = n[:0-len("Policy")]
        return n

    def breakdown_policy(self, tm, ai):
        ''' Called by the BreakdownEngine to break a user policy apart. Should
            only be called by the BreakdownEngine, which passes the topology
            and authorization_func to it.
            This recieves TopologyManager and AuthorizationEngine references
            to perform topology manipulations and verify authorization for
            specific actions.
            Returns a list of UserPolicyBreakdown objects.
            Must be implemented by child classes. '''
        raise NotImplementedError("Subclasses must implement this.")

    def check_validity(self, tm, ai):
        ''' Called by the ValidityInspector to check if the particular object is
            valid. Should only be called by the ValidityInspector, which passes
            the topology and authorization_func to it. ''' 
        raise NotImplementedError("Subclasses must implement this.")

    def pre_add_callback(self, tm, ai):
        ''' This is called before a policy is added to the database. For instance,
            if certain resources need to be locked down or policies authorized,
            this can do it. May not need to be implemented. '''
        pass

    def pre_remove_callback(self, tm, ai):
        ''' This is called before a policy is removed from the database. For 
            instance, if certain resources need to be released, this can do it.
            May not need to be implemented. '''
        pass

    def switch_change_callback(self, tm, ai, data):
        ''' This is called if there is a change triggered by a switch. For 
            instance, a switch learns of a new endpoint, this will be called.
            data is an opaque data type that is specific to the particular
            policy type.
            May not need to be implemented. '''
        pass

    def get_endpoints(self):
        ''' This is not a mandatory function: it should be implemented by 
            UserPolicy children that have external facing endpoints that can use
            resources (bandwidth and VLANs, in particular). Returns a list of 
            tuples:
              (endpointshortname, endpointedge, vlan)
            The endpointshortname and endpointedge is the name of the node being
            connected (if it's an edge node and not a switch) or the name of the
            switch (for instance, br2). Order doesn't matter, we only care about
            the nodes involved. The vlan is the VLAN ID being used to connect 
            the two nodes.
        '''
        return []

    def get_bandwidth(self):
        ''' Another non-mandatory function: it should be implemented by 
            UserPolicy children that have external facing endpoints that can use
            resources (bandwidth and VLANs, in particular). Returns the 
            bandwidth reserved for this service in bps.
        '''
        return None

    def set_breakdown(self, breakdown):
        self.breakdown = breakdown

    def get_breakdown(self):
        return self.breakdown

    def get_start_time(self):
        return self.start_time

    def get_stop_time(self):
        return self.stop_time

    def get_json_policy(self):
        return self.json_policy

    def get_policytype(self):
        return self.policytype

    def get_user(self):
        return self.username

    def set_policy_hash(self, hash):
        self.policy_hash = hash

    def get_policy_hash(self):
        return self.policy_hash

    def get_resources(self):
        return self.resources


    def _parse_json(self, json_policy):
        ''' Actually does parsing. 
            Must be implemented by child classes. '''
        raise NotImplementedError("Subclasses must implement this.")

            


        
class UserPolicyBreakdown(object):
    ''' This provides a standard way of holding broken down policies. Captures 
        the local controller and the rules passed to them. '''

    def __init__(self, lc, list_of_rules):
        ''' The lc is the shortname of the local controller. The list_of_rules 
            is a list of LC rules that are being sent to the Local Controllers. 
        '''
        self.lc = lc
        self.rules = list_of_rules

    def get_lc(self):
        return self.lc

    def get_list_of_rules(self):
        return self.rules

    def add_to_list_of_rules(self, rule):
        self.rules.append(rule)

    def set_cookie(self, cookie):
        for rule in self.rules:
            rule.set_cookie(cookie)
