#  Copyright 2023 Canonical Ltd.
#  See LICENSE file for licensing details.

"""Unit tests for the identity provider."""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from random import randint
from secrets import token_hex
from unittest.mock import Mock

import pytest
from flask import Flask, session
from flask_multipass import AuthInfo, IdentityRetrievalFailed, Multipass
from werkzeug.datastructures import MultiDict

from flask_multipass_saml_groups.provider import (
    DEFAULT_IDENTIFIER_FIELD,
    DEFAULT_SESSION_EXPIRY,
    EXPIRY_SESSION_KEY,
    SAML_GRP_ATTR_NAME,
    SAMLGroupsIdentityProvider,
)
from tests.common import setup_sqlite

USER_EMAIL = "user@example.com"
OTHER_USER_EMAIL = "other@example.com"


@pytest.fixture(name="group_names")
def group_names_fixture():
    """A list of group names."""
    return [token_hex(16), token_hex(16)]


@pytest.fixture(name="saml_attrs")
def saml_attrs_fixture(group_names):
    """SAML attributes for a user.

    The user belongs to all groups.
    """
    return {
        "_saml_nameid": USER_EMAIL,
        DEFAULT_IDENTIFIER_FIELD: f"{USER_EMAIL}@https://site",
        "email": USER_EMAIL,
        "fullname": "Foo bar",
        "openid": "https://openid",
        "userid": USER_EMAIL,
        "username": "user",
        SAML_GRP_ATTR_NAME: group_names,
    }


@pytest.fixture(name="saml_attrs_other_user")
def saml_attrs_other_user_fixture(group_names):
    """SAML attributes for another user.

    This user belongs only to the second group.
    """
    return {
        "_saml_nameid": OTHER_USER_EMAIL,
        DEFAULT_IDENTIFIER_FIELD: f"{OTHER_USER_EMAIL}@https://site",
        "email": OTHER_USER_EMAIL,
        "fullname": "Foo bar",
        "openid": "https://openid",
        "userid": OTHER_USER_EMAIL,
        "username": "other",
        SAML_GRP_ATTR_NAME: group_names[1],  # single elements are expected as str
    }


@pytest.fixture(name="auth_info")
def auth_info_fixture(saml_attrs):
    """The AuthInfo object for a user."""
    return AuthInfo(provider=Mock(), **saml_attrs)


@pytest.fixture(name="auth_info_other_user")
def auth_info_other_user_fixture(saml_attrs_other_user):
    """The AuthInfo object for another user."""
    return AuthInfo(provider=Mock(), **saml_attrs_other_user)


@pytest.fixture(name="app")
def app_fixture():
    """Create a flask app with a properly setup sqlite db."""
    app = Flask("test")
    app.secret_key = token_hex(16)
    setup_sqlite(app)

    app.add_url_rule("/dummy", "dummy", lambda: "dummy")
    app.add_url_rule("/auth/login", "auth.login", lambda: "login")

    return app


@pytest.fixture(name="client")
def client_fixture(app):
    """Create the flask test client."""
    return app.test_client()


@pytest.fixture(name="provider")
def provider_fixture(app):
    """Setup a SAMLGroupsIdentityProvider."""
    multipass = Multipass(app)

    # We need a request context in order to access the session
    with app.test_request_context("/dummy", method="GET"):
        yield SAMLGroupsIdentityProvider(multipass=multipass, name="saml_groups", settings={})


@pytest.fixture(name="provider_custom_field")
def provider_custom_field_fixture(app):
    """Setup a SAMLGroupsIdentityProvider with a custom identifier_field."""
    multipass = Multipass(app)

    # We need a request context in order to access the session
    with app.test_request_context("/dummy", method="GET"):
        yield SAMLGroupsIdentityProvider(
            multipass=multipass,
            name="saml_groups",
            settings={"identifier_field": "fullname"},
        )


@pytest.fixture(name="session_expiry")
def session_expiry_fixture():
    """Create a random session expiry time."""
    return randint(0, 365 * 24 * 60 * 60)  # nosec B311 secret is not used for security


@pytest.fixture(name="provider_session_expiry")
def provider_session_expiry_fixture(app, session_expiry):
    """Setup a SAMLGroupsIdentityProvider with a specific session_expiry setting."""
    multipass = Multipass(app)

    # We need a request context in order to access the session
    with app.test_request_context("/dummy", method="GET"):
        yield SAMLGroupsIdentityProvider(
            multipass=multipass,
            name="saml_groups",
            settings={"session_expiry": session_expiry},
        )


@pytest.fixture(name="dt_mock")
def dt_mock_fixture(monkeypatch):
    """Mock datetime."""
    dt_mock = Mock(spec_set=datetime)
    monkeypatch.setattr("flask_multipass_saml_groups.provider.datetime", dt_mock)
    return dt_mock


def test_init_provider_with_wrong_session_expiry_settings_raises_value_error(app):
    """
    arrange: given a dict with wrong session_expiry setting
    act: call SAMLGroupsIdentityProvider with the settings
    assert: a ValueError is raised
    """
    multipass = Multipass(app)
    wrong_settings = ["not a number", -1]

    with app.app_context():
        for wrong_setting in wrong_settings:
            with pytest.raises(ValueError):
                SAMLGroupsIdentityProvider(
                    multipass=multipass,
                    name="saml_groups",
                    settings={"session_expiry": wrong_setting},
                )


def test_get_identity_from_auth_returns_identity_info(provider, auth_info, saml_attrs):
    """
    arrange: given AuthInfo by AuthProvider
    act: call get_identity_from_auth from identity provider
    assert: the returned IdentityInfo object contains the expected data from AuthInfo
    """
    identity_info = provider.get_identity_from_auth(auth_info)

    assert identity_info is not None
    assert identity_info.provider == provider
    assert identity_info.identifier == auth_info.data[DEFAULT_IDENTIFIER_FIELD]
    assert identity_info.data == MultiDict(saml_attrs)


def test_get_identity_from_auth_returns_identity_info_for_user_without_groups(
    provider, auth_info, saml_attrs
):
    """
    arrange: given AuthInfo by AuthProvider for user without groups
    act: call get_identity_from_auth from identity provider
    assert: the returned IdentityInfo object contains the expected data from AuthInfo
    """
    auth_info.data.pop(SAML_GRP_ATTR_NAME)

    identity_info = provider.get_identity_from_auth(auth_info)

    assert identity_info is not None
    assert identity_info.provider == provider
    assert identity_info.identifier == auth_info.data[DEFAULT_IDENTIFIER_FIELD]
    assert identity_info.data == MultiDict(
        {k: v for k, v in saml_attrs.items() if k != SAML_GRP_ATTR_NAME}
    )


def test_get_identity_from_auth_returns_identity_from_custom_field(
    auth_info, provider_custom_field
):
    """
    arrange: given AuthInfo and provider using custom identifier_field
    act: call get_identity_from_auth from SAMLGroupsIdentityProvider
    assert: the returned IdentityInfo object uses the custom field as identifier
    """
    identity_info = provider_custom_field.get_identity_from_auth(auth_info)

    assert identity_info is not None
    assert identity_info.identifier == auth_info.data["fullname"]


def test_get_identity_from_auth_returns_identity_from_list(auth_info, provider_custom_field):
    """
    arrange: given AuthInfo using a one element list for identifier_field
    act: call get_identity_from_auth from SAMLGroupsIdentityProvider
    assert: the returned IdentityInfo object uses value from the list as identifier
    """
    fullname = token_hex(10)
    auth_info.data["fullname"] = [fullname]

    identity_info = provider_custom_field.get_identity_from_auth(auth_info)

    assert identity_info is not None
    assert identity_info.identifier == fullname


def test_get_identity_from_auth_raises_exc_for_multi_val_identifier(
    auth_info, provider_custom_field
):
    """
    arrange: given AuthInfo using identifier_field with multiple values
    act: call get_identity_from_auth from SAMLGroupsIdentityProvider
    assert: an exception is raised
    """
    fullnames = [token_hex(10), token_hex(15)]

    auth_info.data["fullname"] = fullnames

    with pytest.raises(IdentityRetrievalFailed):
        provider_custom_field.get_identity_from_auth(auth_info)


def test_get_identity_from_auth_raises_exc_for_no_identifier(auth_info, provider):
    """
    arrange: given AuthInfo which does not provide value for identifier field
    act: call get_identity_from_auth from SAMLGroupsIdentityProvider
    assert: an exception is raised
    """
    del auth_info.data[DEFAULT_IDENTIFIER_FIELD]

    with pytest.raises(IdentityRetrievalFailed):
        provider.get_identity_from_auth(auth_info)


def test_get_identity_from_auth_adds_user_to_group(auth_info, provider, group_names):
    """
    arrange: given AuthInfo by AuthProvider
    act: call get_identity_from_auth from SAMLGroupsIdentityProvider
    assert: the user is added to the groups
    """
    provider.get_identity_from_auth(auth_info)

    for grp_name in group_names:
        group = provider.get_group(grp_name)
        members = list(group.get_members())
        assert members
        assert members[0].identifier == auth_info.data[DEFAULT_IDENTIFIER_FIELD]


def test_get_identity_from_auth_adds_user_to_existing_group(
    auth_info, auth_info_other_user, provider, group_names
):
    """
    arrange: given AuthInfo of two users by AuthProvider
    act: call get_identity_from_auth twice and second time with another user
    assert: the user is added to the existing group
    """
    provider.get_identity_from_auth(auth_info)
    provider.get_identity_from_auth(auth_info_other_user)

    group = provider.get_group(group_names[0])
    members = list(group.get_members())
    assert members
    assert members[0].identifier == auth_info.data[DEFAULT_IDENTIFIER_FIELD]

    group = provider.get_group(group_names[1])
    members = list(group.get_members())
    assert len(members) == 2
    expected_identifiers = {
        auth_info.data[DEFAULT_IDENTIFIER_FIELD],
        auth_info_other_user.data[DEFAULT_IDENTIFIER_FIELD],
    }
    assert members[0].identifier in expected_identifiers
    assert members[1].identifier in expected_identifiers


def test_get_identity_from_auth_removes_user_from_group(auth_info, provider, group_names):
    """
    arrange: given AuthInfo by AuthProvider
    act: call get_identity_from_auth and afterwards again with a group removed
    assert: the user is removed from the group
    """
    provider.get_identity_from_auth(auth_info)

    group = provider.get_group(group_names[0])
    members = list(group.get_members())
    assert members
    assert members[0].identifier == auth_info.data[DEFAULT_IDENTIFIER_FIELD]

    auth_info_grp_removed = deepcopy(auth_info)
    auth_info_grp_removed.data[SAML_GRP_ATTR_NAME] = group_names[1]
    provider.get_identity_from_auth(auth_info_grp_removed)

    group = provider.get_group(group_names[0])
    members = list(group.get_members())
    assert not members

    group = provider.get_group(group_names[1])
    members = list(group.get_members())
    assert members
    assert members[0].identifier == auth_info.data[DEFAULT_IDENTIFIER_FIELD]


def test_get_identity_from_auth_removes_user_from_group_if_no_groups_are_passed(
    auth_info, provider, group_names
):
    """
    arrange: given AuthInfo by AuthProvider
    act: call get_identity_from_auth and afterwards again with no groups passed
    assert: the user is removed from all groups
    """
    provider.get_identity_from_auth(auth_info)

    for grp_name in group_names:
        group = provider.get_group(grp_name)
        members = list(group.get_members())
        assert members
        assert members[0].identifier == auth_info.data[DEFAULT_IDENTIFIER_FIELD]

    auth_info_grp_removed = deepcopy(auth_info)
    auth_info_grp_removed.data[SAML_GRP_ATTR_NAME] = []
    provider.get_identity_from_auth(auth_info_grp_removed)

    for grp_name in group_names:
        group = provider.get_group(grp_name)
        members = list(group.get_members())
        assert not members


def test_get_identity_from_auth_sets_default_session_expiry(provider, auth_info, monkeypatch):
    """
    arrange: given AuthInfo with User with groups
    act: call get_identity_from_auth from SAMLGroupsIdentityProvider
    assert: the session expiry is set to the current time plus the default session_expiry seconds
    """
    dt_mock = Mock(spec_set=datetime)
    dt_now = dt_mock.now.return_value = datetime.now(timezone.utc)
    monkeypatch.setattr("flask_multipass_saml_groups.provider.datetime", dt_mock)

    provider.get_identity_from_auth(auth_info)

    assert session.get(EXPIRY_SESSION_KEY) == dt_now + timedelta(seconds=DEFAULT_SESSION_EXPIRY)


def test_get_identity_from_auth_sets_session_expiry(
    provider_session_expiry, session_expiry, auth_info, monkeypatch
):
    """
    arrange: given AuthInfo with User with groups and a provider with explicit session_expiry set
    act: call get_identity_from_auth from SAMLGroupsIdentityProvider
    assert: the session expiry is set to the current time plus the session_expiry seconds
    """
    dt_mock = Mock(spec_set=datetime)
    dt_now = dt_mock.now.return_value = datetime.now(timezone.utc)
    monkeypatch.setattr("flask_multipass_saml_groups.provider.datetime", dt_mock)

    provider_session_expiry.get_identity_from_auth(auth_info)

    assert session.get(EXPIRY_SESSION_KEY) == dt_now + timedelta(seconds=session_expiry)


def test_get_identity_from_auth_sets_no_session_expiry_for_users_without_groups(
    provider_session_expiry, auth_info
):
    """
    arrange: given AuthInfo with User without groups and provider with session_expiry set
    act: call get_identity_from_auth from SAMLGroupsIdentityProvider
    assert: the session expiry is not set
    """
    auth_info.data[SAML_GRP_ATTR_NAME] = []

    provider_session_expiry.get_identity_from_auth(auth_info)

    assert not session.get(EXPIRY_SESSION_KEY)


def test_get_group_returns_specific_group(auth_info, provider, group_names):
    """
    arrange: given AuthInfo by AuthProvider
    act: call get_identity_from_auth and afterwards get_group with a specific group name
    assert: the returned group name is the one requested
    """
    provider.get_identity_from_auth(auth_info)
    group = provider.get_group(group_names[0])

    assert group.name == group_names[0]


def test_get_group_returns_none_if_no_auth_handled(provider, group_names):
    """
    arrange: given only an SAMLGroupsIdentityProvider whose methods have never been called
    act: call get_group from SAMLGroupsIdentityProvider with a specific group name
    assert: the result is None
    """
    group = provider.get_group(group_names[0])

    assert group is None


def test_get_identity_groups(auth_info, provider, group_names):
    """
    arrange: given AuthInfo by AuthProvider
    act: call get_identity_from_auth and afterwards get_identity_groups
    assert: the returned groups of the user are the ones expected
    """
    provider.get_identity_from_auth(auth_info)
    groups = list(provider.get_identity_groups(auth_info.data[DEFAULT_IDENTIFIER_FIELD]))

    assert len(groups) == 2
    assert set(g.name for g in groups) == set(group_names)


def test_search_groups_returns_all_matched_groups(auth_info, provider, group_names):
    """
    arrange: given AuthInfo by AuthProvider
    act: call get_identity_from_auth and afterwards search_groups
    assert: the returned list of groups contains all the groups the user belongs to
    """
    provider.get_identity_from_auth(auth_info)
    groups = list(provider.search_groups(group_names[0], exact=True))

    assert len(groups) == 1
    assert groups[0].name == group_names[0]


def test_search_groups_non_exact_returns_all_matched_groups(auth_info, provider, group_names):
    """
    arrange: given AuthInfo by AuthProvider
    act: call get_identity_from_auth and afterwards search_groups using exact=False
    assert: the returned list of groups contains all the groups the user belongs to
    """
    provider.get_identity_from_auth(auth_info)
    groups = list(provider.search_groups(group_names[0][:-1], exact=False))

    assert len(groups) == 1
    assert groups[0].name == group_names[0]


@pytest.mark.usefixtures("provider")
def test_session_is_cleared_if_expired(app, dt_mock):
    """
    arrange: a session with an expiry date in the past
    act: the flask before_request signal is triggered
    assert: the session is cleared
    """
    dt_now = dt_mock.now.return_value = datetime.now(timezone.utc)

    with app.test_request_context("/dummy", method="GET"):
        session[EXPIRY_SESSION_KEY] = dt_now - timedelta(seconds=1)

        app.preprocess_request()

        assert session == {}


@pytest.mark.usefixtures("provider")
def test_redirect_to_login_if_session_expired(client, dt_mock):
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


@pytest.mark.usefixtures("provider")
def test_ignore_session_if_not_expired(app, dt_mock):
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


@pytest.mark.usefixtures("provider")
def test_no_redirect_to_login_if_session_not_expired(client, dt_mock):
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
