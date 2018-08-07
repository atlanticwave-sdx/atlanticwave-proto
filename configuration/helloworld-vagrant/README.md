# Hello World Example

This is a testbed for trying out the AtlanticWave/SDX controller. It uses a combination of [Vagrant](https://www.vagrantup.com), [VirtualBox](https://www.virtualbox.org/), [Mininet](http://mininet.org/), and [Docker](https://www.docker.com/) to provide an easy-to-use environment.

## SETUP

In order to use the Hello World example, users must first install both VirtualBox and Vagrant:

 - [VirtualBox Install](https://www.virtualbox.org/wiki/Downloads)
 - [Vagrant Install](https://www.vagrantup.com/docs/installation/)

Once installed, you must clone the atlanticwave-proto repository, then create the VM using Vagrant

``` bash
git clone https://github.com/atlanticwave-sdx/atlanticwave-proto.git
cd atlanticwave-proto/configuration/helloworld-vagrant
vagrant up
```

Get comfortable, as the VM takes a few minutes to complete building. Once the VM is created, you need to create four different terminals. Create each terminal from the `atlanticwave-proto/configuration/helloworld-vagrant` directory. In each terminal issue the `vagrant ssh` command to connect to the newly created VM. Each terminal serves a different function:

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


## TESTS

Below is the topology:

``` markdown
VLAN+------+1      1         3       1+------+
1234|  ATL +-------+         +--------+ MIA  |1234
    +------+       +---------+        +------+
                   | Switch  |
    +------+       +---------+        +------+
2345|ATLDTN+-------+         +--------+MIADTN|2345
    +------+1      2         4       1+------+
```

This topology is fairly simple, but we can use it to demonstrate both types of rules that the currenat AtlanticWave/SDX Controller supports.

NOTE:
See the [Issues](https://github.com/atlanticwave-sdx/atlanticwave-proto/issues/) page for potential issues. There are none known as of 11 October 2017.

Let's start by checking connectivity. Run the `pingall` command in the mininet window (window 3). None of the nodes will be able to communicate.

So, our first configuration setp, we will create a DTN rule that connects the DTNs at the bottom of the topology.

On the GUI, click "Requests" from the top bar, then "Scientists" to pull up the creation interface. Select `atldtn` as the Source and `miadtn` as Destination. Set the deadline for sometime in the future, perhaps a week away. Be sure to fill in the time in addition to the date. Set a data size of somethign large, such as 50 GB.

Click Submit, and you'll see a successful creation of a DTN Rule. In the mininet window, run `pingall` again, and you'll see that `atldtn` and `miadtn` will be able to communicate.

Back at the GUI, you can delete the rule (NOTE: [Issue 39](https://github.com/atlanticwave-sdx/atlanticwave-proto/issues/39)). If there are any issues, return to the original URL (e.g., `http://192.168.47.10:5000`).

You can create any tunnel using the Network Engineers portal. For instance, try connecting ATL to MIADTN and try running the pingall command to confirm functionality.
