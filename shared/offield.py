# Copyright 2016 - Sean Donovan
# AtlanticWave/SDX Project


class FieldTypeError(TypeError):
    pass

class FieldValueError(ValueError):
    pass

class Field(object):
    ''' This is the parent class for different kinds of fields that are used in
        OpenFlowActions (defined below). It provides common structure and defines
        descriptors for each child class. '''
    
    def __init__(self, name, value=None, prereq=None):
        ''' name is the name of the field, and is used for prerequisite
            checking.
            value is the value that this particular field is initialized with
            and can be changed by setting the value.
            prereq is an optional prerequisite. If the prereq condition is 
            satisfied, than this is a non-optional field. If None, this is a
            non-optional field. '''
        
        self._name = name
        self.value = value
        self.prereq = prereq

    def __get__(self, obj, objtype):
        return self.value

    def __set__(self, obj, value):
        self.value = value

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        if ((self._name == other._name) &&
            (self.value == other.value)):
            return True
        return False

    def check_validity(self):
        raise NotImplementedError("Subclasses must implement this.")

    def is_optional(self, allfields):
        ''' This checks the other fields in this particular action to see if 
            this is an optional field. If it is optional, returns True, if it is
            required, return False. '''
            
        if self.prereqs == None:
            return False
        # Loop through all the fields
        for field in allfields:
            # If the field matches the prerequisites, then this is not an
            # optional field, return False.
            if self.prereq == field:
                return False
        # Seems it is optional.
        return True
        

class number_field(field):
    ''' Used for fields that need to be numbers. Has additional required init
        fields:
            min    - Minimum value that is allowed.
            max    - Maximum value that is allowed.
            others - Optional field that is a list of other values that are
                     valid.
    '''
     def __init__(self, name, value=None, prereq=None, min, max, others=None):
         super(number_field, self).__init__(name, value, prereq)

         self.min = min
         self.max = max
         self.others = others

    def check_validity(self):
        # Check if self.value is a number
        if not isinstance(self.value, int):
            raise FieldTypeError("self.value is not of type int")

        # Check if self.value is between self.min and self.max a
         if self.value < min or self.value > max:
             if self.other is not None:
                 raise FieldValueError(
                     "self.value is not between " + str(self.min) +
                     " and " + str(self.max))
             elif self.value not in self.other:
                 raise FieldValueError(
                     "self.value is not between " + str(self.min) +
                     " and " + str(self.max) + " and not in (" +
                     str(self.others) + ")")        


class tlv_field(field):
    ''' Used for the TLV field required by action_SET_FIELD. '''
    
# More Field types will need to be written.
