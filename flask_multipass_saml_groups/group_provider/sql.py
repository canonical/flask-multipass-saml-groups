#  Copyright 2023 Canonical Ltd.
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
            provider: The associated identity provider
            name: The name of this group
        """
        super().__init__(provider, name)
        self._provider = provider
        self._name = name

    def get_members(self) -> Iterator[IdentityInfo]:  # noqa: D102,DCO010 docstring in base class
        db_group = DBGroup.query.filter_by(name=self._name).first()
        if db_group:
            return iter(
                map(
                    lambda m: IdentityInfo(provider=self._provider, identifier=m.identifier),
                    db_group.members,
                )
            )
        return iter([])

    def has_member(self, identifier: str) -> bool:  # noqa: D102,DCO010
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

    def add_group(self, name: str) -> None:  # noqa: D102,DCO010 same docstring as in base class
        grp = DBGroup.query.filter_by(name=name).first()
        if not grp:
            db.session.add(DBGroup(name=name))
            db.session.commit()

    def get_group(self, name: str) -> Optional[SQLGroup]:  # noqa: D102,DCO010
        grp = DBGroup.query.filter_by(name=name).first()
        if grp:
            return SQLGroup(provider=self._identity_provider, name=grp.name)
        return None

    def get_groups(self) -> Iterable[SQLGroup]:  # noqa: D102,DCO010
        return map(
            lambda g: SQLGroup(provider=self._identity_provider, name=g.name),
            DBGroup.query.all(),
        )

    def get_user_groups(self, identifier: str) -> Iterable[SQLGroup]:  # noqa: D102,DCO010
        user = SAMLUser.query.filter_by(identifier=identifier).first()
        if user:
            return map(
                lambda g: SQLGroup(name=g.name, provider=self._identity_provider),
                user.groups,
            )
        return []

    def add_group_member(self, identifier: str, group_name: str) -> None:  # noqa: D102,DCO010
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

    def remove_group_member(self, identifier: str, group_name: str) -> None:  # noqa: D102,DCO010
        user = SAMLUser.query.filter_by(identifier=identifier).first()
        grp = DBGroup.query.filter_by(name=group_name).first()

        if grp and user in grp.members:
            grp.members.remove(user)
        db.session.commit()
