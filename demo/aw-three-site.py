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

                               +-------+ VLAN
                               | miah1 | 1800
  VLAN                         +-------+                          VLAN
  1000                              |1                            1200
+-------+1    1                     |                     1    1+------+
| atlh1 +----+            3  3      |1     4  3            +----+ gru1 |
+-------+    +-----------+    +-----------+    +-----------+    +------+
             | atlswitch +----+ miaswitch +----+ gruswitch |
+-------+    +-----+-----+    +-----------+    +-----+-----+    +------+
| atlh2 +----+     | 4              |2             4 |     +----+ gru2 |
+-------+1    2    |                |                |    2    1+------+
  VLAN             |                |1               |            VLAN
  2000             | 1         +-------+ VLAN      1 |            2200
              +--------+       | miah2 | 2800    +--------+
              | atldtn |       +-------+         | grudtn |
              +--------+                         +--------+
'''


    # Hosts and switches
    net = Mininet(topo=None, build=False)
    atlswitch = net.addSwitch('sw1', listenPort=6633, mac='00:00:00:00:00:01')
    miaswitch = net.addSwitch('sw2', listenPort=6643, mac='00:00:00:00:00:02')
    gruswitch = net.addSwitch('sw3', listenPort=6653, mac='00:00:00:00:00:03')

    atlh1 = net.addHost('atlh1', mac='00:00:00:00:10:00',
                        cls=VLANHost, vlan=1000)
    atlh2 = net.addHost('atlh2', mac='00:00:00:00:11:00',
                        cls=VLANHost, vlan=2000)                         

    miah1 = net.addHost('miah1', mac='00:00:00:00:20:00',
                        cls=VLANHost, vlan=1800)
    miah2 = net.addHost('miah2', mac='00:00:00:00:21:00',
                        cls=VLANHost, vlan=2800)

    gruh1 = net.addHost('gruh1', mac='00:00:00:00:30:00',
                        cls=VLANHost, vlan=1200)
    gruh2 = net.addHost('gruh2', mac='00:00:00:00:31:00',
                        cls=VLANHost, vlan=2200)

    atldtn = net.addHost('atldtn', mac='00:00:00:10:00:00',
                        cls=VLANHost, vlan=100)
    miadtn = net.addHost('miadtn', mac='00:00:00:20:00:00',
                        cls=VLANHost, vlan=200)
    grudtn = net.addHost('grudtn', mac='00:00:00:20:00:00',
                        cls=VLANHost, vlan=300)

    # Wiring
    net.addLink(atlswitch, atlh1, port1=1, port2=1)
    net.addLink(atlswitch, atlh2, port1=2, port2=1)
    net.addLink(miaswitch, miah1, port1=1, port2=1)
    net.addLink(miaswitch, miah2, port1=2, port2=1)
    net.addLink(gruswitch, gruh1, port1=1, port2=1)
    net.addLink(gruswitch, gruh2, port1=2, port2=1)
    net.addLink(atlswitch, atldtn, port1=4, port2=1)
    net.addLink(miaswitch, miadtn, port1=5, port2=1)
    net.addLink(gruswitch, grudtn, port1=4, port2=1)

    net.addLink(atlswitch, miaswitch, port1=3, port2=3)
    net.addLink(miaswitch, gruswitch, port1=4, port2=3)

    # Add controllers
    # https://stackoverflow.com/questions/23677291/how-to-connect-different-switches-to-different-remote-controllers-in-mininet

    atlctlr = net.addController('catl', controller=RemoteController, 
                                ip='127.0.0.1', port=6633)
    miactlr = net.addController('cmia', controller=RemoteController, 
                                ip='127.0.0.1', port=6643)
    gructlr = net.addController('cgru', controller=RemoteController, 
                                ip='127.0.0.1', port=6653)
    
    net.build()
    print "net.build"
    
    atlswitch.start([atlctlr])
    miaswitch.start([miactlr])
    gruswitch.start([gructlr])
    net.start()
    print "net.start"
    CLI(net)
    print "CLI(net)"
    net.stop()
    print "net.stop"


if __name__ == '__main__':
    TwoSite()
