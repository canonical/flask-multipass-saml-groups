#!/usr/bin/env bash
#  Copyright 2023 Canonical Ltd.
#  See LICENSE file for licensing details.

# Script that installs the required native libraries for installing the plugin's dependencies
# on Ubuntu 22.04.

sudo apt update
sudo apt install -y pkg-config libxml2-dev libxmlsec1-dev libxmlsec1-openssl libpython3-dev gcc libpq-dev
