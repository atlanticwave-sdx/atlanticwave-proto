# Containernet Vagrant Image

This Vagrant image uses [Containernet](https://containernet.github.io/) in place of Mininet to gain the ability to use arbitrary Docker containers as hosts in a simulated topology. Mininet hosts are still available, and, in the example provided, both are used.

## SETUP

First, we must set up the Containernet Vagrant image. Users must first install VirtualBox and Vagrant:

 - [VirtualBox Install](https://www.virtualbox.org/wiki/Downloads)
 - [Vagrant Install](https://www.vagrantup.com/docs/installation/)

Once installed, you must clone the atlanticwave-proto repository, then create the VM using Vagrant

``` bash
git clone https://github.com/atlanticwave-sdx/atlanticwave-proto.git
cd atlanticwave-proto/configuration/containernet-vagrant
vagrant up
```

This takes *many* minutes for the VM to be created. Go and have lunch, seriously.

Once created, I recommend starting up at least two  terminals in the containernet-vagrant directory. One will be to run the topology and start up all the containers. The second will be for attaching (if desired - not strictly needed) to the controller containers using `docker attach`.

In the first terminal, run the following commands:

``` bash
cd atlanticwave-proto/configuration/containernet-vagrant/
sudo python containernet-mn-topo.py
```

A `containernet` prompt will come up: this is equivalent to the Mininet prompt.

In the second terminal, issue `sudo docker ps` to see running docker containers. To attach to a particular container, issue the `sudo docker attach <containername>` command. To detach, **DO NOT** hit `<CTRL-C>` as one may be tempted to do: this will end the controller, which is messy to restart (restarting the topology is easier). Hit `<CTRL-P> <CTRL-Q>` instead.

The manifest file that is being used in the example uses in-band management, by default. This can be seen in `~/atlanticwave-proto/configuration/containernet-vagrant/containernet.manifest` by looking for all entries that contain `managementvlan` - *managementvlan*, *managementvlanports*, and *untaggedmanagementvlanports*.