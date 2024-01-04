#  Copyright 2024 Canonical Ltd.
#  See LICENSE file for licensing details.

"""Common fixtures for integration tests."""
from secrets import token_hex
from unittest.mock import Mock

import onelogin
import pytest
from flask import Flask
from flask_multipass import Multipass

from flask_multipass_saml_groups.provider import SAMLGroupsIdentityProvider
from tests.common import setup_sqlite
from tests.integration.common import SP_ENTITY_ID, User


@pytest.fixture(name="config")
def config_fixture():
    """Return a config dict for the flask multipass plugin."""
    saml_config = {
        "sp": {
            "entityId": SP_ENTITY_ID,
            "x509cert": "",
            "privateKey": "",
        },
        "idp": {
            "entityId": "https://login.saml.com",
            "x509cert": "dGVzdAo=",
            "singleSignOnService": {
                "url": "https://login.saml.com/saml/",
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
            },
            "singleLogoutService": {
                "url": "https://login.saml.com/+logout",
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
            },
        },
        "security": {
            "nameIdEncrypted": False,
            "authnRequestsSigned": False,
            "logoutRequestSigned": False,
            "logoutResponseSigned": False,
            "signMetadata": False,
            "wantMessagesSigned": False,
            "wantAssertionsSigned": False,
            "wantNameId": False,
            "wantNameIdEncrypted": False,
            "wantAssertionsEncrypted": False,
            "allowSingleLabelDomains": False,
            "signatureAlgorithm": "http://www.w3.org/2001/04/xmldsig-more#rsa-sha256",
            "digestAlgorithm": "http://www.w3.org/2001/04/xmlenc#sha256",
        },
    }
    multipass_auth_providers = {
        "ubuntu": {
            "type": "saml",
            "title": "SAML SSO",
            "saml_config": saml_config,
        },
    }
    multipass_identity_providers = {
        "ubuntu": {
            "type": "saml_groups",
            "title": "SAML",
            "mapping": {
                "name": "DisplayName",
                "email": "EmailAddress",
                "affiliation": "HomeInstitute",
            },
        }
    }
    multipass_provider_map = {
        "ubuntu": "ubuntu",
    }
    return {
        "MULTIPASS_AUTH_PROVIDERS": multipass_auth_providers,
        "MULTIPASS_IDENTITY_PROVIDERS": multipass_identity_providers,
        "MULTIPASS_PROVIDER_MAP": multipass_provider_map,
        "MULTIPASS_REQUIRE_IDENTITY": True,
    }


@pytest.fixture(name="app")
def app_fixture(config):
    """Return a properly setup flask app."""
    app = Flask("test")
    setup_sqlite(app)
    app.config.update(config)
    app.debug = True
    app.secret_key = "fma-example"  # nosec
    app.add_url_rule("/", "index", lambda: "")
    return app


@pytest.fixture(name="multipass")
def multipass_fixture(app, monkeypatch):
    """Return a properly set up flask multipass instance."""
    multipass = Multipass()
    multipass.register_provider(SAMLGroupsIdentityProvider, "saml_groups")
    multipass.init_app(app)
    multipass.identity_handler(Mock(return_value=None))
    monkeypatch.setattr(
        onelogin.saml2.response.OneLogin_Saml2_Response, "is_valid", lambda *args, **kwargs: True
    )  # disable signature validation of SAML response

    return multipass


@pytest.fixture(name="user")
def user_fixture():
    """Return a user email and identifier."""
    user_email = token_hex(16)
    user_identifier = f"{user_email}@{SP_ENTITY_ID}"
    return User(email=user_email, identifier=user_identifier)
