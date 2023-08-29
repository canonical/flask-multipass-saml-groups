#  Copyright 2023 Canonical Ltd.
#  See LICENSE file for licensing details.

"""Unit tests for the plugin module."""

import sys
from datetime import datetime, timedelta, timezone
from secrets import token_hex
from unittest.mock import MagicMock, Mock

import pytest
from flask import Flask, session

from flask_multipass_saml_groups.provider import EXPIRY_SESSION_KEY


@pytest.fixture(name="app")
def app_fixture():
    """Create a flask app with a proper setup."""
    app = Flask("test")
    app.secret_key = token_hex(16)

    app.route("/dummy", endpoint="dummy")(lambda: "dummy")
    app.route("/auth/login", endpoint="auth.login")(lambda: "login")
    return app


@pytest.fixture(name="client")
def client_fixture(app):
    """Create the flask test client."""
    return app.test_client()


@pytest.fixture(name="plugin", autouse=True)
def plugin_fixture(app, monkeypatch):
    """Initialize the plugin."""

    class FakeIndicoPlugin:  # pylint: disable=too-few-public-methods
        """Fake IndicoPlugin class which does not a lot to avoid side-effects."""

        def __init__(self, app, plugin_engine):  # pylint: disable=unused-argument
            """Initialize the plugin by calling init.

            Args:
                app: The flask app.
                plugin_engine: The plugin engine.
            """
            self.init()

        def init(self):
            """Initialize the plugin.

            Does nothing. It is intended to be overridden.
            """

    # We patch 'indico.core.plugins' as the real import has a lot of side-effects for the other
    # tests. It seems that all database models from Indico are registered as soon as the module is
    # imported.
    module_mock = MagicMock()
    module_mock.IndicoPlugin = FakeIndicoPlugin
    monkeypatch.setitem(sys.modules, "indico.core.plugins", module_mock)
    # pylint: disable=import-outside-toplevel
    from flask_multipass_saml_groups.plugin import SAMLGroupsPlugin

    with app.app_context():
        SAMLGroupsPlugin(app=app, plugin_engine=Mock())


@pytest.fixture(name="dt_mock")
def dt_mock_fixture(monkeypatch):
    """Mock datetime."""
    dt_mock = Mock(spec_set=datetime)
    monkeypatch.setattr("flask_multipass_saml_groups.plugin.datetime", dt_mock)
    return dt_mock


def test_before_request_clears_session_if_expires(app, dt_mock):
    """
    arrange: a session with an expiry date in the past
    act: the before_request signal is triggered
    assert: the session is cleared
    """
    dt_now = dt_mock.now.return_value = datetime.now(timezone.utc)

    with app.test_request_context("/dummy", method="GET"):
        session[EXPIRY_SESSION_KEY] = dt_now - timedelta(seconds=1)

        app.preprocess_request()

        assert session == {}


def test_before_request_redirects_to_login_if_expires(client, dt_mock):
    """
    arrange: a session with an expiry date in the past
    act: a request is made, triggering the before_request signal
    assert: the response is a redirect to the login page
    """
    dt_now = dt_mock.now.return_value = datetime.now(timezone.utc)

    with client.session_transaction() as sess:
        sess[EXPIRY_SESSION_KEY] = dt_now - timedelta(seconds=1)

    resp = client.get("/dummy")
    assert resp.status_code == 302
    assert resp.location == "/auth/login"


def test_before_request_ignores_session_if_not_expired(app, dt_mock):
    """
    arrange: a session with an expiry date in the future
    act: the before_request signal is triggered
    assert: the session is not cleared
    """
    dt_now = dt_mock.now.return_value = datetime.now(timezone.utc)

    with app.test_request_context("/dummy", method="GET"):
        session[EXPIRY_SESSION_KEY] = dt_now + timedelta(seconds=1)

        app.preprocess_request()

        assert session == {EXPIRY_SESSION_KEY: dt_now + timedelta(seconds=1)}


def test_before_request_does_not_redirect_to_login_if_expires(client, dt_mock):
    """
    arrange: a session with an expiry date in the future
    act: a request is made, triggering the before_request signal
    assert: the response is not a redirect to the login page
    """
    dt_now = dt_mock.now.return_value = datetime.now(timezone.utc)

    with client.session_transaction() as sess:
        sess[EXPIRY_SESSION_KEY] = dt_now + timedelta(seconds=1)

    resp = client.get("/dummy")
    assert resp.status_code == 200
    assert not resp.location
