from __future__ import print_function
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.util import custom
from mininet.node import RemoteController, Host
from mininet.cli import CLI

# This runs one switch, each with three hosts at easy to read formats.
# Each switch has its own separate controller.

# To run (in 3 separate terminals) the topology and two controllers.
#   cd ~/atlanticwave-proto/demo
#   sudo python demo-one-site.py
#
#   cd ~/atlanticwave-proto/sdxctlr
#   python SDXController.py
#
#   cd ~/atlanticwave-proto/
#   python LocalController.py
#

# From: https://github.com/mininet/mininet/blob/master/examples/vlanhost.py

class VLANHost( Host ):
    "Host connected to VLAN interface"

    def config( self, vlan=100, **params ):
        """Configure VLANHost according to (optional) parameters:
           vlan: VLAN ID for default interface"""

        r = super( VLANHost, self ).config( **params )

        intf = self.defaultIntf()
        # remove IP from default, "physical" interface
        self.cmd( 'ifconfig %s inet 0' % intf )
        # create VLAN interface
        self.cmd( 'vconfig add %s %d' % ( intf, vlan ) )
        # assign the host's IP to the VLAN interface
        self.cmd( 'ifconfig %s.%d inet %s' % ( intf, vlan, params['ip'] ) )
        # update the intf name and host's intf map
        newName = '%s.%d' % ( intf, vlan )
        # update the (Mininet) interface to refer to VLAN interface name
        intf.name = newName
        # add VLAN interface to host's name to intf map
        self.nameToIntf[ newName ] = intf

        return r

hosts = { 'vlan': VLANHost }

def TwoSite():
    ''' This is the topology that we will be building here.

VLAN  +-------+1    1                          1    1+-------+ VLAN
1234  | atlh1 +----+            3  3            +----+ miah1 | 1876
      +-------+    +-----------+    +-----------+    +-------+
                   | atlswitch +----+ miaswitch |
VLAN  +-------+    +-----------+    +-----------+    +-------+ VLAN
2345  | atlh2 +----+                            +----+ miah2 | 2987
      +-------+1    2                          2    1+-------+
'''


    # Hosts and switches
    net = Mininet(topo=None, build=False)
    atlswitch = net.addSwitch('s1', listenPort=6633, mac='00:00:00:00:00:01')
    miaswitch = net.addSwitch('s2', listenPort=6653, mac='00:00:00:00:00:02')

    atlh1 = net.addHost('atlh1', mac='00:00:00:00:01:00',
                        cls=VLANHost, vlan=1234)
    atlh2 = net.addHost('atlh2', mac='00:00:00:00:02:00',
                        cls=VLANHost, vlan=2345)                         

    miah1 = net.addHost('miah1', mac='00:00:00:00:03:00',
                        cls=VLANHost, vlan=1876)
    miah2 = net.addHost('miah2', mac='00:00:00:00:04:00',
                        cls=VLANHost, vlan=2987)

    # Wiring
    net.addLink(atlswitch, atlh1, port1=1, port2=1)
    net.addLink(atlswitch, atlh2, port1=2, port2=1)
    net.addLink(miaswitch, miah1, port1=1, port2=1)
    net.addLink(miaswitch, miah2, port1=2, port2=1)
    net.addLink(atlswitch, miaswitch, port1=3, port2=3)

    # Add controllers
    # https://stackoverflow.com/questions/23677291/how-to-connect-different-switches-to-different-remote-controllers-in-mininet

    atlctlr = net.addController('c0', controller=RemoteController, 
                                ip='127.0.0.1', port=6633)
    miactlr = net.addController('c0', controller=RemoteController, 
                                ip='127.0.0.1', port=6653)
    
    net.build()
    print("net.build")
    
    atlswitch.start([atlctlr])
    miaswitch.start([miactlr])
    net.start()
    print("net.start")
    CLI(net)
    print("CLI(net)")
    net.stop()
    print("net.stop")


if __name__ == '__main__':
    TwoSite()
