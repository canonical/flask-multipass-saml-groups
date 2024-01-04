#  Copyright 2024 Canonical Ltd.
#  See LICENSE file for licensing details.

"""Unit tests for the sql group provider."""


from secrets import token_hex

import pytest
from flask_multipass import IdentityProvider, Multipass
from indico.core.db import db

from flask_multipass_saml_groups.group_provider.sql import SQLGroup, SQLGroupProvider
from flask_multipass_saml_groups.models.saml_groups import SAMLGroup as DBGroup
from flask_multipass_saml_groups.models.saml_groups import SAMLUser

NOT_EXISTING_USER_IDENTIFIER = "user-3"
NOT_EXISTING_GRP_NAME = "not_existing"


@pytest.fixture(name="group_names")
def group_names_fixture():
    """Return group names"""
    return [token_hex(16), token_hex(16)]


@pytest.fixture(name="user_identifiers")
def user_identifiers_fixture():
    """Return user identifiers"""
    return [token_hex(16), token_hex(16)]


@pytest.fixture(name="group_provider")
def group_provider_fixture(app, group_names, user_identifiers):
    """Setup a group provider and place groups and users in the database.

    The first user is placed in the first group.
    The second user belongs to no group.
    The second group has no members.
    """
    with app.app_context():
        multipass = Multipass(app=app)
        group_provider = SQLGroupProvider(
            identity_provider=IdentityProvider(
                multipass=multipass, name="saml_groups", settings={}
            ),
        )
        user1 = SAMLUser(identifier=user_identifiers[0])
        user2 = SAMLUser(identifier=user_identifiers[1])

        # pylint does not recognize the methods of db.session, which is a proxy object
        # pylint: disable=no-member
        db.session.add(user1)
        db.session.add(user2)
        grp1 = DBGroup(name=group_names[0])
        grp1.members.append(user1)
        db.session.add(grp1)
        db.session.add(DBGroup(name=group_names[1]))
        db.session.commit()

        yield group_provider


def test_get_group(group_provider, group_names):
    """
    arrange: given a GroupProvider instance
    act: call get_group with a specific group name
    assert: returns a SQLGroup instance with the same name
    """
    grp = group_provider.get_group(group_names[0])

    assert isinstance(grp, SQLGroup)
    assert grp.name == group_names[0]


def test_get_group_not_found(group_provider):
    """
    arrange: given a GroupProvider instance
    act: call get_group with a non existing group name
    assert: returns None
    """
    grp = group_provider.get_group("non-existing")

    assert grp is None


def test_get_groups(group_provider, group_names):
    """
    arrange: given a GroupProvider instance
    act: call get_groups
    assert: returns an iterable of all groups
    """
    grps = list(group_provider.get_groups())

    assert grps
    assert len(grps) == 2
    assert {grp.name for grp in grps} == set(group_names)


def test_get_user_groups(group_provider, user_identifiers, group_names):
    """
    arrange: given a user identifier
    act: call get_user_groups
    assert: returns an iterable of groups the user belongs to
    """
    grps = list(group_provider.get_user_groups(user_identifiers[0]))

    assert grps
    assert len(grps) == 1
    assert grps[0].name == group_names[0]


def test_get_user_groups_without_groups(group_provider, user_identifiers):
    """
    arrange: given a user identifier for a user who belongs to no groups
    act: call get_user_groups
    assert: returns empty list
    """
    grps = list(group_provider.get_user_groups(user_identifiers[1]))

    assert not grps


def test_get_user_groups_for_non_existing_user(group_provider):
    """
    arrange: given a user identifier for a non existing user
    act: call get_user_groups
    assert: returns empty list
    """
    grps = list(group_provider.get_user_groups("non-existing"))

    assert not grps


def test_add_group(group_provider):
    """
    arrange: given a GroupProvider instance
    act: call add_group with a group name
    assert: the group can be retrieved calling get_group
    """
    group_provider.add_group(NOT_EXISTING_GRP_NAME)
    grp = group_provider.get_group(NOT_EXISTING_GRP_NAME)

    assert isinstance(grp, SQLGroup)
    assert grp.name == NOT_EXISTING_GRP_NAME


def test_add_group_group_already_existing(group_provider, group_names):
    """
    arrange: given a group that already exists
    act: call add_group with that group name
    assert: the group can be retrieved calling get_group
    """
    group_name = group_names[0]
    group_provider.add_group(group_name)

    grp = group_provider.get_group(group_name)
    assert isinstance(grp, SQLGroup)
    assert grp.name == group_name


def test_add_group_member(group_provider, user_identifiers, group_names):
    """
    arrange: given a user who does not belong to a group
    act: call add_group_member with that user and group
    assert: the user belongs to the group
    """
    user_identifier = user_identifiers[0]
    group_name = group_names[1]
    group_provider.add_group_member(user_identifier, group_name)

    grp = group_provider.get_group(group_name)
    assert isinstance(grp, SQLGroup)
    assert grp.name == group_name
    members = list(grp.get_members())
    assert len(members) == 1
    assert members[0].identifier == user_identifier


def test_add_group_member_user_non_existing(group_provider, group_names):
    """
    arrange: given a non existing user identifier
    act: call add_group_member with that user and a group name
    assert: the user gets created and belongs to the group
    """
    group_name = group_names[1]
    group_provider.add_group_member(NOT_EXISTING_USER_IDENTIFIER, group_name)

    grp = group_provider.get_group(group_name)
    assert isinstance(grp, SQLGroup)
    assert grp.name == group_name
    members = list(grp.get_members())
    assert len(members) == 1
    assert members[0].identifier == NOT_EXISTING_USER_IDENTIFIER


def test_add_group_member_group_non_existing(group_provider, user_identifiers):
    """
    arrange: given a non existing group
    act: call add_group_member with a user identifier that group
    assert: the group gets created and the user belongs to the group
    """
    user_identifier = user_identifiers[0]
    group_provider.add_group_member(user_identifier, NOT_EXISTING_GRP_NAME)

    grp = group_provider.get_group(NOT_EXISTING_GRP_NAME)
    assert isinstance(grp, SQLGroup)
    assert grp.name == NOT_EXISTING_GRP_NAME
    members = list(grp.get_members())
    assert len(members) == 1
    assert members[0].identifier == user_identifier


def test_add_group_member_pair_already_existing(group_provider, user_identifiers, group_names):
    """
    arrange: given a user and a group to which the user does not belong
    act: call add_group_member twice
    assert: the user belongs to the group, but is returned only once
    """
    user_identifier = user_identifiers[0]
    group_name = group_names[1]

    group_provider.add_group_member(user_identifier, group_name)
    group_provider.add_group_member(user_identifier, group_name)

    grp = group_provider.get_group(group_name)
    assert isinstance(grp, SQLGroup)
    assert grp.name == group_name
    members = list(grp.get_members())
    assert len(members) == 1
    assert members[0].identifier == user_identifier


def test_remove_group_member(group_provider, user_identifiers, group_names):
    """
    arrange: given a user which belongs to a group
    act: call remove_group_member
    assert: the user does not belong to the group anymore
    """
    user_identifier = user_identifiers[0]
    group_name = group_names[0]

    group_provider.remove_group_member(user_identifier, group_name)

    grp = group_provider.get_group(group_name)
    assert isinstance(grp, SQLGroup)
    assert grp.name == group_name
    members = list(grp.get_members())
    assert not members


def test_remove_group_member_user_non_existing(group_provider, user_identifiers, group_names):
    """
    arrange: given a group with a user
    act: call remove_group_member with a non existing user identifier and that group
    assert: the member list without the user is returned
    """
    user_identifier = user_identifiers[0]
    group_name = group_names[0]

    group_provider.remove_group_member(NOT_EXISTING_USER_IDENTIFIER, group_name)

    grp = group_provider.get_group(group_name)
    assert isinstance(grp, SQLGroup)
    assert grp.name == group_name
    members = list(grp.get_members())
    assert len(members) == 1
    assert members[0].identifier == user_identifier


def test_remove_group_member_group_non_existing(group_provider, user_identifiers):
    """
    arrange: given a user and a non existing group
    act: call remove_group_member with that user and the non existing group
    assert: the group does not exist
    """
    user_identifier = user_identifiers[0]

    group_provider.remove_group_member(user_identifier, NOT_EXISTING_GRP_NAME)

    grp = group_provider.get_group(NOT_EXISTING_GRP_NAME)
    assert not grp
