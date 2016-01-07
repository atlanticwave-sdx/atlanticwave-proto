from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.util import custom
from mininet.node import RemoteController
from mininet.cli import CLI

# This runs two switches, each with three hosts at easy to read formats.
# Each switch has its own separate controller.

# To run (in 3 separate terminals) the topology and two controllers.
#   cd ~/atlanticwave-proto/topo
#   sudo python twosite.py
#
#   cd ~/ryu
#   ./bin/ryu-manager --verbose ryu/app/simple_switch.py --ofp-tcp-listen-port 6653
#
#   cd ~/ryu
#   ./bin/ryu-manager --verbose ryu/app/simple_switch.py --ofp-tcp-listen-port 6654



def TwoSite():

    # Hosts and switches
    net = Mininet(topo=None, build=False)
    atlswitch = net.addSwitch('s1', listenPort=6633, mac='00:00:00:00:00:01')
    miaswitch = net.addSwitch('s2', listenPort=6634, mac='00:00:00:00:00:02')

    atlh1 = net.addHost('atlh1', mac='00:00:00:00:01:00')
    atlh2 = net.addHost('atlh2', mac='00:00:00:00:02:00')
    atlh3 = net.addHost('atlh3', mac='00:00:00:00:03:00')

    miah1 = net.addHost('miah1', mac='00:00:00:00:04:00')
    miah2 = net.addHost('miah2', mac='00:00:00:00:05:00')
    miah3 = net.addHost('miah3', mac='00:00:00:00:06:00')

    # Wiring
    net.addLink(atlswitch, miaswitch)
    net.addLink(atlh1, atlswitch)
    net.addLink(atlh2, atlswitch)
    net.addLink(atlh3, atlswitch)
    net.addLink(miah1, miaswitch)
    net.addLink(miah2, miaswitch)
    net.addLink(miah3, miaswitch)

    # Add controllers
    # https://stackoverflow.com/questions/23677291/how-to-connect-different-switches-to-different-remote-controllers-in-mininet

    atlctlr = net.addController('c0', controller=RemoteController, 
                                ip='127.0.0.1', port=6653)
    miactlr = net.addController('c0', controller=RemoteController, 
                                ip='127.0.0.1', port=6654)
    
    net.build()
    atlswitch.start([atlctlr])
    miaswitch.start([miactlr])

    CLI(net)
    net.stop

if __name__ == '__main__':
    TwoSite()
