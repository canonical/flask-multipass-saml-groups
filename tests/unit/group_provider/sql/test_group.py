#  Copyright 2023 Canonical Ltd.
#  See LICENSE file for licensing details.

"""Unit tests for the sql group."""
from secrets import token_hex

import pytest
from flask_multipass import IdentityInfo, Multipass

from flask_multipass_saml_groups.group_provider.sql import SQLGroup, SQLGroupProvider
from flask_multipass_saml_groups.provider import SAMLGroupsIdentityProvider


@pytest.fixture(name="group_name")
def group_name_fixture():
    """Return a group name"""
    return token_hex(16)


@pytest.fixture(name="provider")
def provider_fixture(app):
    """Create an identity provider"""
    multipass = Multipass(app)
    with app.app_context():
        yield SAMLGroupsIdentityProvider(multipass=multipass, name="saml_groups", settings={})


@pytest.fixture(name="group_provider")
def group_provider_fixture(provider):
    """Create a group provider"""
    return SQLGroupProvider(identity_provider=provider)


@pytest.fixture(name="group")
def group_fixture(provider, group_name):
    """Create a group object.

    The group is not created in the database, only the object is created.
    """
    return SQLGroup(provider=provider, name=group_name)


def test_get_members(group, group_provider, group_name):
    """
    arrange: given group with users
    act: call get_members
    assert: the users are contained in the returned result
    """
    users = [token_hex(16), token_hex(6)]
    group_provider.add_group_member(group_name=group_name, identifier=users[0])
    group_provider.add_group_member(group_name=group_name, identifier=users[1])

    members = list(group.get_members())

    assert members
    assert len(members) == 2
    assert isinstance(members[0], IdentityInfo)
    assert isinstance(members[1], IdentityInfo)

    assert {member.identifier for member in members} == set(users)


def test_get_members_returns_empty_list(group, group_provider, group_name):
    """
    arrange: given no users
    act: call get_members
    assert: get_members returns an empty iterator
    """
    group_provider.add_group(group_name)

    members = list(group.get_members())

    assert not members


def test_get_members_returns_empty_list_for_non_existing_group(group):
    """
    arrange: given no underlying db group
    act: call get_members
    assert: get_members returns an empty iterator
    """
    members = list(group.get_members())

    assert not members


def test_has_member(group, group_provider, group_name):
    """
    arrange: given a user which belongs to a group
    act: call has_member
    assert: has_user returns True
    """
    user_identifier = token_hex(16)
    group_provider.add_group_member(identifier=user_identifier, group_name=group_name)

    assert group.has_member(user_identifier)


def test_has_member_returns_false(group, group_provider, group_name):
    """
    arrange: given a user identifier which does not belong to a group
    act: call has_member
    assert: has_member returns False
    """
    user_identifiers = [token_hex(16), token_hex(6)]
    group_provider.add_group_member(identifier=user_identifiers[0], group_name=group_name)
    assert not group.has_member(user_identifiers[1])


def test_has_member_returns_false_for_non_existing_group(group):
    """
    arrange: given no underlying db group
    act: call has_member
    assert: has_member returns False
    """
    user_identifier = token_hex(16)
    assert not group.has_member(user_identifier)
