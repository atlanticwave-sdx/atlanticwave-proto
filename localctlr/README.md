# Local Controller

## Introduction

The local controllers are responsible for translating the rules sent by the SDX controller and pushing them to the switch that they directly control. They also need to establish connectivity with the SDX controller, which involves bootstrapping the switches at startup to establish connectivity.

The local controller is an odd duck: it is mostly a pass through at this point, but will become much more complex in the fiture. Right now, the interface with the SDX controller is *very* nearly OpenFlow, as such, there is very little translation. Further, establishing connectivity with the SDX controller isn't yet an issue, as it is done in an out-of-band (OOB) manner thus far.


## Bootstrapping

In the future, the local controller will be connnected to the SDX controller over the very same network connection they are managing. As such, the local controller will need to bootstrap the switch with rules that set up the network to allow the connection to even start.

This likely will be done with a configuration file that has the rules necessary to set up the configuration correctly. 


## Translation

This is the main job of the local controllers. They will be translating rules that the SDX controller sends into switch protocol-specific rules. For now, we are focusing on OpenFlow, and using Ryu as the OpenFlow speaker.


## Pushing Rules with Ryu

Getting rules form the local controller to Ryu to pass them to the switch is far more complex than it should be. It does not appear to be possible to incorporate Ryu into an outside application, rather Ryu expect to be the main application. As such, I've connected the plumbing in such a way that there is a small shim program that Ryu runs that pulls rules off of a queue (filled by the main local controller) and issues them to the switch. It's ugly and kludgy, but works just fine.

Thus far, extracting information from the switches has _not_ been done, but a similar mechanism in the opposite directly will likely be used.