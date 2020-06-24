from __future__ import absolute_import
# Copyright 2017 - Sean Donovan
# AtlanticWave/SDX Project


from .LCFields import *
from .LCAction import *

class SDXActionTypeError(TypeError):
    pass

class SDXActionValueError(ValueError):
    pass

class SDXAction(object):
    ''' This is used to encapsulate actions for SDX Ingress and Egress policies.
        It uses LCFields to handle sanity checking of values.
    '''

    def __init__(self, name, value, action):
        ''' - name is the name of the field
            - value is the value that this particular field is initialized with
              and can be changed by setting the value.
            - action is an LCAction.

            The field is created by the child of the SDXAction. name and value 
            are likely duplicate, but here for ease-of-use.
        '''
        self._name = name
        self.value = value
        if not isinstance(action, LCAction):
            raise SDXActionTypeError("field is not LCAction: %s" % type(action))
        self.action = action

    def __repr__(self):
        return "%s : %s:%s : %s" % (self.__class__.__name__,
                                    self._name,
                                    self.value,
                                    repr(self.action))

    def __str__(self):
        return str(self.field)

    def __eq__(self, other):
        if type(other) != type(self):
            return False
        return (self._name == other._name and
                self.value == other.value and
                str(self.action) == str(other.action)) #FIXME: This is dirty, as
                                                       #LCAction doesn't have a
                                                       #__eq__() function.

    def get_action(self):
        return self.action

    @staticmethod
    def lookup_action_type(name):
        if name not in SDXACTION_TO_CLASS.keys():
            raise SDXActionValueError("%s not in SDXACTION_TO_CLASS: %s" %
                                     (name, SDXACTION_TO_CLASS.keys()))
        return SDXACTION_TO_CLASS[name]


class SDXActionModifySRCMAC(SDXAction):
    def __init__(self, value):
        action = SetField(ETH_SRC(value))
        super(SDXActionModifySRCMAC, self).__init__('ModifySRCMAC',
                                                    value, action)
        
class SDXActionModifyDSTMAC(SDXAction):
    def __init__(self, value):
        action = SetField(ETH_DST(value))
        super(SDXActionModifyDSTMAC, self).__init__('ModifyDSTMAC',
                                                    value, action)
        
class SDXActionModifySRCIP(SDXAction):
    def __init__(self, value):
        action = SetField(IPV4_SRC(value))
        super(SDXActionModifySRCIP, self).__init__('ModifySRCIP',
                                                    value, action)
        
class SDXActionModifyDSTIP(SDXAction):
    def __init__(self, value):
        action = SetField(IPV4_DST(value))
        super(SDXActionModifyDSTIP, self).__init__('ModifyDSTIP',
                                                    value, action)
        
class SDXActionModifyTCPSRC(SDXAction):
    def __init__(self, value):
        action = SetField(TCP_SRC(value))
        super(SDXActionModifyTCPSRC, self).__init__('ModifyTCPSRC',
                                                    value, action)
        
class SDXActionModifyTCPDST(SDXAction):
    def __init__(self, value):
        action = SetField(TCP_DST(value))
        super(SDXActionModifyTCPDST, self).__init__('ModifyTCPDST',
                                                    value, action)
        
class SDXActionModifyUDPSRC(SDXAction):
    def __init__(self, value):
        action = SetField(UDP_SRC(value))
        super(SDXActionModifyUDPSRC, self).__init__('ModifyUDPSRC',
                                                    value, action)
        
class SDXActionModifyUDPDST(SDXAction):
    def __init__(self, value):
        action = SetField(UDP_DST(value))
        super(SDXActionModifyUDPDST, self).__init__('ModifyUDPDST',
                                                    value, action)

class SDXActionModifyVLAN(SDXAction):
    def __init__(self, value):
        action = SetField(VLAN_VID(value))
        super(SDXActionModifyVLAN, self).__init__('ModifyVLAN',
                                                  value, action)
        
class SDXActionForward(SDXAction):
    def __init__(self, value):
        action = Forward(value)
        super(SDXActionForward, self).__init__('Forward',
                                               value, action)

class SDXActionDrop(SDXAction):
    def __init__(self, value):
        action = Drop(value)
        super(SDXActionDrop, self).__init__('Drop',
                                            value, action)

#FIXME: Does this need to exist?
class SDXActionContinue(SDXAction):
    def __init__(self, value):
        action = Continue(value)
        super(SDXActionContinue, self).__init__('Continue',
                                                value, action)

SDXACTION_TO_CLASS = {
    'ModifySRCMAC':SDXActionModifySRCMAC,
    'ModifyDSTMAC':SDXActionModifyDSTMAC,
    'ModifySRCIP':SDXActionModifySRCIP,
    'ModifyDSTIP':SDXActionModifyDSTIP,
    'ModifyTCPSRC':SDXActionModifyTCPSRC,
    'ModifyTCPDST':SDXActionModifyTCPDST,
    'ModifyUDPSRC':SDXActionModifyUDPSRC,
    'ModifyUDPDST':SDXActionModifyUDPDST,
    'ModifyVLAN':SDXActionModifyVLAN,
    'Forward':SDXActionForward,
    'Drop':SDXActionDrop,
    'Continue':SDXActionContinue
}


