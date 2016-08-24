# AtlanticWave/SDX Controller Prototype

## Introduction

This repository contains all the code for the prototype AtlanticWave/SDX controller. It will likely transition to being the basis for a production controller in the future, however a different controller platform may be more appropriate.

The initial deployment for the AtlanticWave/SDX will be Atlanta, Miami, and Sao Paulo. The controller is broken into multiple parts (described in more detail below) running at these different locations.

It is written in Python, using the [Ryu](https://osrg.github.io/ryu/) SDN Framework as an OpenFlow speaker, and has a REST API and web application for management. It is being designed to allow for new types of rules to be added, as well as communicating using other SDN protocols ([P4](http://p4.org/), for instance).



## Controller Breakdown

The controller will be split into three main parts:
 *  Participant Interface(s)

The participant interfaces are where the participants (network operators typically, scientists moving data in this case) install rules that dictate how flows behave. There will be multiple, and of multiple different kinds. For the initial prototype, there will be a web app that allows users to create and install rules.

The SDX controller (below) will have a REST API, so other participant interfaces could be created. For example, a participant could create a meta-controller that uses the REST API to control their own flows.

 *  SDX Controller

The SDX controller is responsible for a number of things, including authentication and authorization of participants and local controllers, taking rules from the participant interfaces and breaking them down into per-location rules for the local controllers, handling federation challenges from many participants installing rules on a shared network, and providing an interface for the participants.

The SDX controller will provide a REST API that allows participants' rules to be installed. The participants will likely _not_ use it directly, but rather than provides participant interfaces (described above). This will provide options for installing many different types of rules, at different levels of abstraction (non-abstract near-OpenFlow to the very abstract creating a 40Gbps connection between Chicago and Chile). 

 * Local Controllers

Each location in the AtlanticWave/SDX will have a local controller that controlls the local switch. The local controller has one main job: take the somewhat abstract rules form the SDX controller, and translate them to a switch friendly protocol, OpenFlow right now. The local controller also bootstraps the configuration of the switch to establish connectivity between the local controller and the SDX controller.


## Shared Code

There is significant shared code of two different types: interface objects and library functions. Both types of shared code can be found in the `shared` folder.

The interface objects are used to pass data between different modules, typically different parts of the controller.

The libraries as of this writing include a communication library that abstracts away how to encode, send, and receive objects that are being sent between different parts of the controller. Abstracting the communication interface allows us to add more features, without altering other code. For instance, the initial implementation is very simple, sending data on an unencrypted TCP connection. Future versions will use bidirectionally authenticated TLS, while retaining the same `send` and `receive` functionality.



## Other code

The `testing` and `topo` folders are both for testing. `testing` contains test cases, typically at unit-test level, but some system tests as well. `topo` provides topologies for testing and demos.


## VM Requirements

** FIXME: This needs to be updated **

### Virtual Environment

Use virtualenv to easily set up the controller

creat a virtual environment.
do not do this inside of the directory if you are a contributor

    virtualenv venv
    source venv/bin/activate

now go into the atlanticwave directory and download the requirements

    cd atlanticwave-proto/
    pip install -r requirements.txt

Also be sure to set your python path

    export PYTHONPATH=/Users/johnskan/atlanticwave-proto
