# SDX Controller

## Introduction

The SDX controller is the main part of the controller architecture. It serves as as both the interface for participant policies and to push rules to the local controllers to implement participants' requests. There are two main pieces of the SDX controller: the user APIs, and the policy engine. The user APIs are the interface for the participants to instantiate policies. There are currently three different APIs: a REST API for programmatically controlling the SDX controller, a web (HTML) version of the REST interface, and a SENSE API for allowing the SENSE project's orchestrator to issue policies to the SDX controller using the SENSE interface. The policy engine takes policies from the participants, validates them, and breaks them down into rules that an individual local controller can implement.


## REST API

** FIXME: Details **


## Rule engine

** FIXME: Details **

 * Validation for correctness, authorization.
 * Breaking down rules to send them to local controllers



## Other Responsibilities

The SDX controller has other responsibilites, beyond is main rule-pushing role, described below.

### Authentication and Authorization

Before either accessing the API or breaking down rules, there are other things that must be checked by the SDX controller including authentication and authorization. 

 * Authentication of participants

The SDX controller will maintain a list of users that are able to use the SDX controller, though the REST API. We must verify that they are who they say they are. Initially, this will likely be something simple, like basic password protection, then changing into a certificate-driven system.

 * Authorization of participants for particular rules

Once authenticated, the SDX controller will verify that the participant is able to perform the action that they are requesting to do. This would be the first step in the verification step that the rule engine performs, as checking for syntactical validity isn't useful if the user cannot perform the action in the first place. 

 * Authentication of local controllers

Authenticating the local controllers is also necessary such that rules are not being dropped or are being modififed. If we know that the local controler is who they say that they are, we can trust that they are, in fact, the correct controller.


### Federation

We would like to allow _other_ systems to be able to push rules to the AtlanticWave/SDX, as well as being able to push rules to their systems as well. For example, we would like to be able to extend a VLAN all the way from Chile, through Sao Paulo, to Atlanta, then to Chicago, crossing over at least three administrative domains (RedCLARA, AtlanticWave/SDX, and Internet2). Being able to issue a command to any of these, and have it propogate through the other two would be ideal.
