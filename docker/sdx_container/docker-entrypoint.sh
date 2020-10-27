#!/usr/bin/env bash

_generate_dot_env() {
  cat > atlanticwave-proto/sdxctlr/.env <<EOF
# SDX Controller

# Specifies the database
export DATABASE=${DATABASE}
# Specifies the manifest
export MANIFEST=${MANIFEST}
# Run with Shibboleth for authentication
export SHIBBOLETH=${SHIBBOLETH}
# Run with CILogon for authentication
export CILOGON=${CILOGON}
# Run without the topology
export NOTOPO=${NOTOPO}
# Choose a host address
export HOST=${HOST}
# Port number of web interface
export PORT=${PORT}
# Port number of SENSE interface
export SPORT=${SPORT}
# Port number for LCs to connect to
export LCPORT=${LCPORT}
EOF
}

### main ###

_generate_dot_env
cd atlanticwave-proto
python sdxctlr/SDXController.py
