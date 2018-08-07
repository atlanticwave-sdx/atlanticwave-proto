# In-Band Management Examples

This Vagrant image is for testing out In-Band Management (IBM). There are three topologies that we offer for simulating IBM:

 - `singlenode-mn-topo.py` - this has one single switch, a few hosts, and containers for the LC and SDX controller.
 - `twonode-mn-topo.py` - this has two switches, a few hosts per switch two LCs (one per switch), and an SDX controller.
 - `containernet-mn-topo.py` - This has four switches, a few hosts per switch, three LCs (one handling two switches), and an SDX controller.

It is based on [Containernet](https://github.com/containernet/containernet), which is a modification of Mininet that, in addition to simple hosts that Mininet provides, can use Docker containers as hosts. We use this capability to run the LCs and SDXes in their own containers and connect them to switch data ports.

## Setup

## SETUP

In order to use the IBM example, users must first install both VirtualBox and Vagrant:

 - [VirtualBox Install](https://www.virtualbox.org/wiki/Downloads)
 - [Vagrant Install](https://www.vagrantup.com/docs/installation/)

Once installed, you must clone the atlanticwave-proto repository, then create the VM using Vagrant

``` bash
git clone https://github.com/atlanticwave-sdx/atlanticwave-proto.git
cd atlanticwave-proto/configuration/containernet-vagrant
vagrant up
```

Get comfortable, as the VM takes a few minutes to complete building. Once the VM is created, you will likely want two terminals: one to run the topology, and one to verify rules are being installed. You can get away with only having a single terminal running the topology, however.

To connect to the VM, issue the `vagrant ssh` command from the `containernet-vagrant` directory.

To run a topology, issue `sudo python <topology>`, where `<topology>` is one of the topologies described above. After a few seconds, connections betwen the LCs and the SDX controller will be established, and basic rules will be installed.

At the `containernet>`prompt issue `net` to show the switch names (usually s1, s2, etc.). The rules installed can be seen in a separate terminal. At the second terminal that has issued `vagrant ssh`, you can issue the command `sudo ovs-ofctl -O OpenFlow13 dump-flows <switch name>` to see installed rules.

