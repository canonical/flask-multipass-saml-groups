#  Copyright 2023 Canonical Ltd.
#  See LICENSE file for licensing details.

"""Integration tests which check if the session is properly invalidated after a given time."""
from datetime import datetime, timedelta, timezone
from secrets import token_hex

import pytest
from flask import current_app, session, url_for
from freezegun import freeze_time
from werkzeug import Response

from flask_multipass_saml_groups.provider import DEFAULT_SESSION_EXPIRY
from tests.integration.common import login


@pytest.mark.usefixtures("multipass")
def test_redirect_after_invalid_session(app, user):
    """
    arrange: given an app and a user that has groups in the SAML attributes
    act: call login and all a URL after the session expiry
    assert: the session is invalidated and the user is redirected to the login page
    """
    client = app.test_client()

    grp_names = [token_hex(16), token_hex(6)]
    dt_now = datetime.now(timezone.utc)
    with freeze_time(dt_now) as frozen_datetime:
        login(client, groups=grp_names, user_email=user.email)

        frozen_datetime.tick(delta=timedelta(seconds=DEFAULT_SESSION_EXPIRY + 1))
        with client:
            resp = client.get("/dummy")

            _assert_session_invalidation(resp)


@pytest.mark.usefixtures("multipass")
def test_no_redirect_before_session_expiry(app, user):
    """
    arrange: given an app and a user that has groups in the SAML attributes
    act: call login and call a URL before the session expires
    assert: the session is not invalidated and the user is not redirected to the login page
    """
    client = app.test_client()

    grp_names = [token_hex(16), token_hex(6)]
    dt_now = datetime.now(timezone.utc)
    with freeze_time(dt_now) as frozen_datetime:
        login(client, groups=grp_names, user_email=user.email)

        frozen_datetime.tick(delta=timedelta(seconds=DEFAULT_SESSION_EXPIRY - 1))
        with client:
            resp = client.get("/dummy")

            _assert_no_session_invalidation(resp)


@pytest.mark.usefixtures("multipass")
def test_no_session_invalidation_for_users_without_groups(app, user):
    """
    arrange: given an app and a user that has no groups in the SAML attributes
    act: call login and all a URL after the default session expiry
    assert: the session is not invalidated and the user is not redirected to the login page
    """
    client = app.test_client()

    dt_now = datetime.now(timezone.utc)
    with freeze_time(dt_now) as frozen_datetime:
        login(client, groups=[], user_email=user.email)

        frozen_datetime.tick(delta=timedelta(seconds=DEFAULT_SESSION_EXPIRY + 1))
        with client:
            resp = client.get("/dummy")

            _assert_no_session_invalidation(resp)


def _assert_session_invalidation(response: Response):
    """Assert that the session is invalidated and the user is redirected to the login page.

    Args:
        response: The response to check.
    """
    assert response.status_code == 302
    assert response.location == url_for(current_app.config["MULTIPASS_LOGIN_ENDPOINT"])
    assert not session


def _assert_no_session_invalidation(response: Response):
    """Assert that the session is not invalidated and the user is not redirected to the login page.

    Args:
        response: The response to check.
    """
    assert response.status_code == 200
    assert not response.location
    assert session
