# Hello World - Multiple Locations Example

This is a testbed for trying out the AtlanticWave/SDX controller with multiple locations and multiple Local Controllers. It uses a combination of [Vagrant](https://www.vagrantup.com), [VirtualBox](https://www.virtualbox.org/), [Mininet](http://mininet.org/), and [Docker](https://www.docker.com/) to provide an easy-to-use environment.

## SETUP

In order to use the Hello World example, users must first install both VirtualBox and Vagrant:

 - [VirtualBox Install](https://www.virtualbox.org/wiki/Downloads)
 - [Vagrant Install](https://www.vagrantup.com/docs/installation/)

Once installed, you must clone the atlanticwave-proto repository, then create the VM using Vagrant

``` bash
git clone https://github.com/atlanticwave-sdx/atlanticwave-proto.git
cd atlanticwave-proto/configuration/helloworld-multi-vagrant
vagrant up
```

Get comfortable, as the VM takes a few minutes to complete building. Once the VM is created, you need to create two terminals. Create each terminal from the `atlanticwave-proto/configuration/helloworld-multi-vagrant` directory. In each terminal issue the `vagrant ssh` command to connect to the newly created VM. Each terminal serves a different function:

1. Controller startup
2. Topology startup

So, in the first terminal, issue the following command `./1-start-controller.sh`.  
In the second terminal, issue `./2-start-topology.sh`.

Once Mininet comes up, it will connect to the Local Controller, which  will connect to the SDX Controller. At this point, you can connect to the SDX Controller's web interface using a browser in your host system.

On the first terminal, the script will return an IP address. Assume it returns 192.168.47.10. Copy that IP to a brower window, and tack on the port 5000. So, for our case, you would navigate to `http://192.168.47.10:5000` and see the GUI.

From here, you'll need to log in. Click the log in button on the top bar, and use the very secure credentials `sdonovan`/`1234` to log in.


## Topology

The topology is a complicated enough to make for interesting tests. The LAX switch is controlled by one local controller, the ORD and ATL switches are controlled by a second, and the NYC switch is controlled by a third.

``` markdown
                           21         22         23
                        +-------+  +-------+  +-------+
                        | ORDH1 |  | ORDH2 |  | ORDH3 |
                        +---+---+  +---+---+  +---+---+
                          1 |        2 |        3 |
                            |   1      | 2        | 3
                            +------+---+---+------+
                                   | ORDS1 |
                          +--------+---+---+-----+
VLAN          PORT        |       4    |     6   |
    +-------+ 1           |            | 5       |          1 +-------+
11  | LAXH1 +-----+       |            |         |       +----+ NYCH1 | 31
    +-------+   1 |       |            |         |       | 1  +-------+
                  |       |4           |       4 |       |
    +-------+ 2   +-------+            |         +-------+  2 +-------+
12  | LAXH2 +-----+ LAXS1 |            |         | NYCS1 +----+ NYCH2 | 32
    +-------+   2 +-------+            |         +-------+ 2  +-------+
                  |       |5           |                 |
    +-------+ 3   |       |            |                 |  3 +-------+
13  | LAXH3 +-----+       |            |                 +----+ NYCH3 | 33
    +-------+   3         |            |                   3  +-------+
                          |            |
                          |            | 5
                          |      4     |
                          +--------+---+---+
                                   | ATLS1 |
                            +------+-------+------+
                            |  1       |2         | 3
                           1|         2|         3|
                        +-------+  +-------+  +-------+
                        | ATLH1 |  | ATLH2 |  | ATLH3 |
                        +-------+  +-------+  +-------+
                           41          42        43
```

## User Interfaces

There are three UIs that a user can use: one REST and two web-based GUIs.

The REST API is a bit complicated, but is described [here](https://docs.google.com/document/d/1yCbCZYFwVfDbKzIxoKz9zuhJitZVomA2aWUtsgsP7rw/edit?usp=sharing).

These same endpoints (generally) can be seen using a web browser.

The original web-based GUI is available as well, but is depricated.