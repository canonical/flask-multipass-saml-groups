#!/usr/bin/env bash
#  Copyright 2023 Canonical Ltd.
#  See LICENSE file for licensing details.

# Call script with sudo to install the required native libraries for installing the plugin's dependencies
sudo bash -xe "$(dirname "$0")"/../install-libs.sh