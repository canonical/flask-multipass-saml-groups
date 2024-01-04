#  Copyright 2024 Canonical Ltd.
#  See LICENSE file for licensing details.

"""Integration tests which check if the provider works as expected."""
from secrets import token_hex
from typing import List

from flask_multipass import Group, IdentityInfo

from tests.integration.common import login


def test_get_group(app, multipass, user):
    """
    arrange: given a logged-in user which is a member of a group
    act: call get_group on identity provider
    assert: the group is returned and group methods work as expected
    """
    client = app.test_client()

    grp_name = token_hex(16)
    login(client, groups=[grp_name], user_email=user.email)

    with app.app_context():
        idp = multipass.identity_providers["ubuntu"]
        _assert_group_methods_work([idp.get_group(grp_name)], user.identifier)


def test_get_identity_groups(app, multipass, user):
    """
    arrange: given a logged-in user which is a member of multiple group
    act: call get_identity_groups on identity provider
    assert: the groups of the user are returned and group methods work as expected
    """
    client = app.test_client()

    grp_names = [token_hex(16), token_hex(6)]
    login(client, groups=grp_names, user_email=user.email)

    with app.app_context():
        idp = multipass.identity_providers["ubuntu"]
        groups = list(idp.get_identity_groups(user.identifier))

        _assert_group_methods_work(groups, user.identifier)
        _assert_group_names(groups, grp_names)


def test_search_groups(app, multipass, user):
    """
    arrange: given a logged-in user which is a member of a group
    act: call search_groups on identity provider
    assert: only the matched groups of the user are returned and group methods work as expected
    """
    client = app.test_client()
    login(client, groups=["x", "xy", "z"], user_email=user.email)

    with app.app_context():
        idp = multipass.identity_providers["ubuntu"]
        groups = list(idp.search_groups("x"))

        _assert_group_methods_work(groups, user.identifier)
        _assert_group_names(groups, ["x", "xy"])


def _assert_group_methods_work(groups: List[Group], user_identifier: str):
    """Assert that all the group methods work as expected.

    Args:
        groups: The groups to check.
        user_identifier: The identifier of the user which is expected to belong to the groups.
    """
    for grp in groups:
        members = list(grp.get_members())
        assert len(members) == 1
        member = members[0]
        assert isinstance(member, IdentityInfo)
        assert member.identifier == user_identifier

        assert grp.has_member(user_identifier)


def _assert_group_names(groups: List[Group], expected_names: List[str]):
    """Assert that the group names are as expected.

    Args:
        groups: The groups to check.
        expected_names: The expected group names.
    """
    assert len(groups) == len(expected_names)
    for grp in groups:
        assert grp.name in expected_names
