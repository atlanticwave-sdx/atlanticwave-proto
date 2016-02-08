# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


import sys

class FieldTypeError(TypeError):
    pass

class FieldValueError(ValueError):
    pass

class FieldPrereqError(ValueError):
    pass

class Field(object):
    ''' This is the parent class for different kinds of fields that are used in
        OpenFlowActions (defined below). It provides common structure and defines
        descriptors for each child class. '''
    
    def __init__(self, name, value=None, prereq=None, optional_without=None, mask=False):
        ''' - name is the name of the field, and is used for prerequisite
              checking.
            - value is the value that this particular field is initialized with
              and can be changed by setting the value.
            - prereq is a list of prerequisite conditions. If at least one of 
              them is satisfied, then prerequisites are met. 
            - optional_without is a condition that, if satisfied, this Field is
              not optional. If it is None, then it is also not optional. '''
        
        
        self._name = name
        self.value = value
        self.optional_wo = optional_without
        self.prereq = prereq

    #TODO - Can these be represented as a property/discriptor? I don't think so.
    def get(self):
        return self.value

    def set(self, value):
        self.value = value

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        if ((self._name == other._name) and
            (self.value == other.value)):
            return True
        return False

    def check_validity(self):
        raise NotImplementedError("Subclasses must implement this.")

    def is_optional(self, allfields):
        ''' This checks the other fields in this particular action to see if 
            this is an optional field. If it is optional, returns True, if it is
            required, return False. '''
            
        if self.optional_wo == None:
            return False
        # Loop through all the fields
        for field in allfields:
            # If the field matches the prerequisites, then this is not an
            # optional field, return False.
            if self.optional_wo == field:
                return False
        # Seems it is optional.
        return True

    def check_prerequisites(self, allfields):
        ''' This checks to see if any of the prereqs exist in allfields that
            is passed in. If at least one of the prereqs are satisfied, the
            check passes. Otherwise, raises an error. '''
        if self.prereq == None:
            return
        for field in allfields:
            if field in self.prereq:
                return
        raise FieldPrereqError("Prerequisites are not met")
        
        

class number_field(Field):
    ''' Used for fields that need to be numbers. Has additional required init
        fields:
            minval - Minimum value that is allowed.
            maxval - Maximum value that is allowed.
            others - Optional field that is a list of other values that are
                     valid.
    '''
    def __init__(self, name, minval, maxval, value=None, prereq=None,
                 optional_without=None, others=[]):
        if value is not None:
            if type(value) is not int:
                raise FieldTypeError("value is not a number")
        
        super(number_field, self).__init__(name, value, prereq, optional_without)

        self.minval = minval
        self.maxval = maxval
        self.others = others

    def check_validity(self):
        # Check if self.value is a number
        if not isinstance(self.value, int):
            raise FieldTypeError("self.value of " + self._name + " is not of type int: " + str(type(self.value)))

        # Check if self.value is between self.minval and self.maxval
        if (self.value < self.minval) or (self.value > self.maxval):
             if len(self.others) == 0 :
                 raise FieldValueError(
                     "self.value (" + str(self.value) + ") is not between " + str(self.minval) +
                     " and " + str(self.maxval))
             elif self.value not in self.others:
                 raise FieldValueError(
                     "self.value is not between " + str(self.minval) +
                     " and " + str(self.maxval) + " and not in (" +
                     str(self.others) + ")")        


class bitmask_field(number_field):
    ''' Used for fields that need bitmasks. Same as a number_field right 
        now, but could change in the future. '''
    pass

class ipv4_field(Field):
    ''' Used for IPv4 addresses. '''
    
    def check_validity(self):
        # TODO: This needs to be written.
        pass

class ipv6_field(Field):
    ''' Used for IPv6 addresses. '''
    
    def check_validity(self):
        # TODO: This needs to be written.
        pass



