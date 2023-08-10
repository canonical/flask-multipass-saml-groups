#  Copyright 2023 Canonical Ltd.
#  See LICENSE file for licensing details.

"""Integration tests which check if the groups are properly handled when a user logins."""
from secrets import token_hex
from typing import List

from flask import Flask
from flask_multipass import Multipass

from tests.integration.common import login


def test_login_extracts_groups_from_saml_attributes(app, multipass, user):
    """
    arrange: given an app
    act: call login with a user that has groups in the SAML attributes
    assert: the user is logged in and the groups are assigned to the user
    """
    client = app.test_client()

    grp_names = [token_hex(16), token_hex(6)]
    login(client, groups=grp_names, user_email=user.email)

    _assert_user_is_logged_in_with_groups(grp_names, app, multipass, user.identifier)


def test_relogin_removes_previous_groups(app, multipass, user):
    """
    arrange: given an app and a user with groups
    act: call login with a user and recall login with the same user but differing groups
    assert: the user is logged in and the invalid group memberships from first login are removed
    """
    client = app.test_client()

    grp_names = [token_hex(16), token_hex(6)]
    other_grp_names = [token_hex(16), token_hex(6)]

    login(client, groups=grp_names, user_email=user.email)
    login(client, groups=other_grp_names, user_email=user.email)

    _assert_user_is_logged_in_with_groups(other_grp_names, app, multipass, user.identifier)


def test_login_with_no_groups(app, multipass, user):
    """
    arrange: given an app
    act: call login with a user that has no groups in the SAML attributes
    assert: the user is logged in and no groups are assigned to the user
    """
    client = app.test_client()

    login(client, groups=[], user_email=user.email)

    _assert_user_is_logged_in_with_groups([], app, multipass, user.identifier)


def test_login_with_multiple_identical_groups(app, multipass, user):
    """
    arrange: given an app
    act: call login with a user that has duplicate group names in the SAML attributes
    assert: the user is logged in and the duplicate group names are not counted
    """
    client = app.test_client()

    grp_name = token_hex(16)

    login(client, groups=[grp_name, grp_name], user_email=user.email)

    _assert_user_is_logged_in(app, multipass)

    with app.app_context():
        idp = multipass.identity_providers["ubuntu"]

        grps = list(idp.get_identity_groups(user.identifier))
        assert len(grps) == 1


def _assert_user_is_logged_in_with_groups(
    groups: List[str], app: Flask, multipass: Multipass, user_identifier: str
):
    """Assert that the user is logged in with the given groups.

    Args:
        groups: The groups the user should be in
        app: The app
        multipass: The multipass instance
        user_identifier: The identifier of the user which is expected to belong to the groups.
    """
    _assert_user_is_logged_in(app, multipass)
    _assert_user_only_in_groups(groups, app, multipass, user_identifier)


def _assert_user_is_logged_in(app: Flask, multipass: Multipass):
    """Assert that the user is logged in.

    Args:
        app: The app
        multipass: The multipass instance

    """
    with app.app_context():
        # The identity callback is only called when `get_identity_from_auth` returns
        # an identity_info object.
        multipass.identity_callback.assert_called()


def _assert_user_only_in_groups(
    groups: List[str], app: Flask, multipass: Multipass, user_identifier: str
):
    """Assert that the user is only in the given groups.

    Args:
        groups: The groups the user should be in
        app: The app
        multipass: The multipass instance
        user_identifier: The identifier of the user which is expected to belong to the groups.

    """
    with app.app_context():
        idp = multipass.identity_providers["ubuntu"]

        grps = list(idp.get_identity_groups(user_identifier))
        assert len(grps) == len(groups)

        for grp in grps:
            assert grp.name in groups
            assert isinstance(grp, idp.group_class)
            assert grp.has_member(user_identifier)
