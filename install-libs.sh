#!/usr/bin/env bash
#  Copyright 2024 Canonical Ltd.
#  See LICENSE file for licensing details.

# Script that installs the required native libraries for installing the plugin's dependencies
# on Ubuntu 22.04.

if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

apt-get update
apt-get install -y pkg-config libxml2-dev libxmlsec1-dev libxmlsec1-openssl libpython3-dev gcc libpq-dev \
  libxslt1-dev libffi-dev libpcre3-dev libyaml-dev build-essential libbz2-dev libreadline-dev libsqlite3-dev \
  libjpeg-turbo8-dev zlib1g-dev liblzma-dev