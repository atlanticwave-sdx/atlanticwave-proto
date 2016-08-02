# config_parser


The configuration parser has been used for testing, but allows for a configuration file to be used to pre-populate rules for a particular participant.

I (Sean) anticipate that this may get used as a way to upload a configuration file for a static configuration from a web interface (say, a long running experiment transfers data at a known data rate every night from 3-6 AM, a static configuration file to reserve some bandwidth would be reasonable.

Additionally, a variant of the parser could be used at each site to bootstrap the local controller to set up connections with the SDX controller.