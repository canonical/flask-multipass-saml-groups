#  Copyright 2023 Canonical Ltd.
#  See LICENSE file for licensing details.
"""Defines the interface for a group provider."""

from abc import ABCMeta, abstractmethod
from typing import Iterable, Optional

from flask_multipass import Group, IdentityProvider


class GroupProvider(metaclass=ABCMeta):
    """A group provider is responsible for managing groups and their members.

    Attrs:
        group_class (type): The class to use for groups.
    """

    group_class = Group

    def __init__(self, identity_provider: IdentityProvider):
        """Initialize the group provider.

        Args:
            identity_provider: The associated identity provider. Usually required because the group
                needs to know the identity provider.
        """

    @abstractmethod
    def add_group(self, name: str) -> None:  # pragma: no cover
        """Add a group.

        Args:
            name: The name of the group.
        """

    @abstractmethod
    def get_group(self, name: str) -> Optional[Group]:  # pragma: no cover
        """Get a group.

        Args:
            name: The name of the group.

        Returns:
            The group or None if it does not exist.
        """
        return None

    @abstractmethod
    def get_groups(self) -> Iterable[Group]:  # pragma: no cover
        """Get all groups.

        Returns:
            An iterable of all groups.
        """
        return []

    @abstractmethod
    def get_user_groups(self, identifier: str) -> Iterable[Group]:  # pragma: no cover
        """Get all groups a user is a member of.

        Args:
            identifier: The unique user identifier used by the provider.

        Returns:
                iterable: An iterable of groups the user is a member of.
        """
        return []

    @abstractmethod
    def add_group_member(self, identifier: str, group_name: str) -> None:  # pragma: no cover
        """Add a user to a group.

        Args:
            identifier: The unique user identifier used by the provider.
            group_name: The name of the group.
        """

    @abstractmethod
    def remove_group_member(self, identifier: str, group_name: str) -> None:  # pragma: no cover
        """Remove a user from a group.

        Args:
            identifier: The unique user identifier used by the provider.
            group_name: The name of the group.
        """
