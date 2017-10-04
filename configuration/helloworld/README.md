# Hello World Example

This is a testbed for trying out the AtlanticWave/SDX controller. It uses a combination of [Vagrant](https://www.vagrantup.com), [VirtualBox](https://www.virtualbox.org/), [Mininet](http://mininet.org/), and [Docker](https://www.docker.com/) to provide an easy-to-use environment.

In order to use the Hello World example, users must first install both VirtualBox and Vagrant:

 - [VirtualBox Install](https://www.virtualbox.org/wiki/Downloads)
 - [Vagrant Install](https://www.vagrantup.com/docs/installation/)

Once installed, you must clone the atlanticwave-proto repository, then create the VM using Vagrant

'''bash
git clone https://github.com/atlanticwave-sdx/atlanticwave-proto.git
cd atlanticwave-proto/configuration/helloworld
vagrant up
'''

Get comfortable, as the VM takes a few minutes to complete building. Once the VM is created, you need to create four different terminals. Create each terminal from the `atlanticwave-proto/configuration/helloworld` directory. In each terminal issue the `vagrant ssh` command to connect to the newly created VM. Each terminal serves a different function:

1. SDX Controller
2. Local Controller
3. Mininet
4. Displays IP address of the VM so that you can create rules

So, in the first terminal, issue the following command `./1-start-sdxctlr.sh`.  
In the second terminal, issue `./2-start-lcctlr.sh`.  
In the third terminal, issue `./3-start-mininet.sh`.  
In the forth terminal, issue `./4-get-ip.sh`

The order in which these commands are issued matters, thus the numbering.

Once Mininet comes up, it will connect to the Local Controller, which  will connect to the SDX Controller. At this point, you can connect to the SDX Controller's web interface using a browser in your host system.

On the forth terminal, `./4-get-ip.sh` will return an IP address. Assume it returns 192.168.47.10. Copy that IP to a brower window, and tack on the port 5000. So, for our case, you would navigate to `http://192.168.47.10:5000` and see the GUI.

From here, you'll need to log in. Click the log in button on the top bar, and use the very secure credentials `sdonovan`/`1234` to log in.
