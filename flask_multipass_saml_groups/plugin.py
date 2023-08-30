#  Copyright 2023 Canonical Ltd.
#  See LICENSE file for licensing details.
"""Marks the package in order to be used by the Indico plugin system."""

from indico.core.plugins import IndicoPlugin


class SAMLGroupsPlugin(IndicoPlugin):
    """SAML Groups Plugin.

    The plugin provides an identity provider for SAML which supports groups.
    """
