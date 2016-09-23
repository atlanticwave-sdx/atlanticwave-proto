from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.util import custom
from mininet.node import RemoteController
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

def OneSite():
    ''' This is the topology that we will be building here.
    +------+1      1         3       1+------+
    |  ATL +-------+         +--------+ MIA  |
    +------+       +---------+        +------+
                   | Switch  |
    +------+       +---------+        +------+
    |ATLDTN+-------+         +--------+MIADTN|
    +------+1      2         4       1+------+

''' 


    # Hosts and switches
    net = Mininet(topo=None, build=False)
    atlswitch = net.addSwitch('s1', listenPort=6633, mac='00:00:00:00:00:01')

    atl    = net.addHost('atl', mac='00:00:00:00:01:00')
    atldtn = net.addHost('atldtn', mac='00:00:00:00:02:00')

    mia    = net.addHost('miah1', mac='00:00:00:00:03:00')
    miadtn = net.addHost('miah2', mac='00:00:00:00:04:00')

    # Wiring
    net.addLink(atlswitch, atl, port1=1)
    net.addLink(atlswitch, atldtn, port1=2)
    net.addLink(atlswitch, mia, port1=3)
    net.addLink(atlswitch, miadtn, port1=4)

    # Add controllers
    # https://stackoverflow.com/questions/23677291/how-to-connect-different-switches-to-different-remote-controllers-in-mininet

    atlctlr = net.addController('c0', controller=RemoteController, 
                                ip='127.0.0.1', port=6633)
    
    net.build()
    print "net.build"
    
    net.start()
    print "net.start"
    CLI(net)
    print "CLI(net)"
    net.stop()
    print "net.stop"


if __name__ == '__main__':
    OneSite()
