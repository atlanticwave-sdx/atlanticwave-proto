# `remotectlr`

This directory contains the "remote controller". It is used for testing of the local controller, and acts as if it is the SDX controller. It uses the `config_parser` library to push rules from a configuration file to a local controller, which then pushes rules to a switch.

It can be used as an example interface to base the SDX controller off of.