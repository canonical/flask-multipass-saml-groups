#  Copyright 2024 Canonical Ltd.
#  See LICENSE file for licensing details.

"""A group provider that persists groups and their members in a SQL database provided by Indico."""

from typing import Iterable, Iterator, Optional

from flask_multipass import Group, IdentityInfo, IdentityProvider
from indico.core.db import db

from flask_multipass_saml_groups.group_provider.base import GroupProvider
from flask_multipass_saml_groups.models.saml_groups import SAMLGroup as DBGroup
from flask_multipass_saml_groups.models.saml_groups import SAMLUser


class SQLGroup(Group):
    """A group whose group membership is persisted in a SQL database.

    Attrs:
        supports_member_list (bool): If the group supports getting the list of members
    """

    supports_member_list = True

    def __init__(self, provider: IdentityProvider, name: str):
        """Initialize the group.

        Args:
            provider: The associated identity provider.
            name: The unique, case-sensitive name of this group.
        """
        super().__init__(provider, name)
        self._provider = provider
        self._name = name

    def get_members(self) -> Iterator[IdentityInfo]:
        """Return the members of the group.

        Returns:
            An iterator over IdentityInfo objects.
        """
        db_group = DBGroup.query.filter_by(name=self._name).first()
        if db_group:
            return iter(
                map(
                    lambda m: IdentityInfo(provider=self._provider, identifier=m.identifier),
                    db_group.members,
                )
            )
        return iter([])

    def has_member(self, identifier: str) -> bool:
        """Check if a given identity is a member of the group.

        Args:
            identifier: The unique user identifier used by the provider.

        Returns:
            True if the user is a member of the group, False otherwise.
        """
        return (
            DBGroup.query.filter_by(name=self._name)
            .join(DBGroup.members)
            .filter_by(identifier=identifier)
            .first()
            is not None
        )


class SQLGroupProvider(GroupProvider):
    """Provide access to Groups persisted with a SQL database.

    Attrs:
        group_class (class): The class to use for groups.
    """

    # pylint does not recognize the methods of db.session, which is a proxy object
    # pylint: disable=no-member

    group_class = SQLGroup

    def __init__(self, identity_provider: IdentityProvider):
        """Initialize the group provider.

        Args:
            identity_provider: The identity provider this group provider is associated with.
        """
        super().__init__(identity_provider)
        self._identity_provider = identity_provider

    def add_group(self, name: str) -> None:
        """Add a group.

        Args:
            name: The name of the group.
        """
        grp = DBGroup.query.filter_by(name=name).first()
        if not grp:
            db.session.add(DBGroup(name=name))
            db.session.commit()

    def get_group(self, name: str) -> Optional[SQLGroup]:
        """Get a group.

        Args:
            name: The name of the group.

        Returns:
            The group or None if it does not exist.
        """
        grp = DBGroup.query.filter_by(name=name).first()
        if grp:
            return SQLGroup(provider=self._identity_provider, name=grp.name)
        return None

    def get_groups(self) -> Iterable[SQLGroup]:
        """Get all groups.

        Returns:
            An iterable of all groups.
        """
        return map(
            lambda g: SQLGroup(provider=self._identity_provider, name=g.name),
            DBGroup.query.all(),
        )

    def get_user_groups(self, identifier: str) -> Iterable[SQLGroup]:
        """Get all groups a user is a member of.

        Args:
            identifier: The unique user identifier used by the provider.

        Returns:
                iterable: An iterable of groups the user is a member of.
        """
        user = SAMLUser.query.filter_by(identifier=identifier).first()
        if user:
            return map(
                lambda g: SQLGroup(name=g.name, provider=self._identity_provider),
                user.groups,
            )
        return []

    def add_group_member(self, identifier: str, group_name: str) -> None:
        """Add a user to a group.

        Args:
            identifier: The unique user identifier used by the provider.
            group_name: The name of the group.
        """
        user = SAMLUser.query.filter_by(identifier=identifier).first()
        grp = DBGroup.query.filter_by(name=group_name).first()

        if not user:
            user = SAMLUser(identifier=identifier)
            db.session.add(user)
        if not grp:
            grp = DBGroup(name=group_name)
            db.session.add(grp)

        if user not in grp.members:
            grp.members.append(user)
        db.session.commit()

    def remove_group_member(self, identifier: str, group_name: str) -> None:
        """Remove a user from a group.

        Args:
            identifier: The unique user identifier used by the provider.
            group_name: The name of the group.
        """
        user = SAMLUser.query.filter_by(identifier=identifier).first()
        grp = DBGroup.query.filter_by(name=group_name).first()

        if grp and user in grp.members:
            grp.members.remove(user)
        db.session.commit()
