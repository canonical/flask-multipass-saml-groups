#  Copyright 2024 Canonical Ltd.
#  See LICENSE file for licensing details.
#
"""SAML Groups Identity Provider."""
import operator
from datetime import datetime, timedelta, timezone
from typing import Dict, Iterable, Optional, Type
from urllib.parse import urlsplit

from flask import current_app, redirect, request, session, url_for
from flask_multipass import (
    AuthInfo,
    Group,
    IdentityInfo,
    IdentityProvider,
    IdentityRetrievalFailed,
    Multipass,
)
from werkzeug import Response

from flask_multipass_saml_groups.group_provider.base import GroupProvider
from flask_multipass_saml_groups.group_provider.sql import SQLGroupProvider

DEFAULT_IDENTIFIER_FIELD = "_saml_nameid_qualified"
SAML_GRP_ATTR_NAME = "urn:oasis:names:tc:SAML:2.0:profiles:attribute:DCE:groups"
SESSION_EXPIRY_SETTING = "session_expiry"
DEFAULT_SESSION_EXPIRY = 24 * 60 * 60  # 24 hours
EXPIRY_SESSION_KEY = "_flask_multipass_saml_groups_session_expiry"


class SAMLGroupsIdentityProvider(IdentityProvider):
    """Provides identity information using SAML and supports groups.

    Attrs:
        supports_get (bool): If the provider supports getting identity information
            based from an identifier
        supports_groups (bool): If the provider also provides groups and membership information
        supports_get_identity_groups (bool): If the provider supports getting the list of groups an
         identity belongs to
        group_class (class): The class to use for groups. Defaults to flask_multipass.Group but
            concrete class will be used from group_provider_class
    """

    supports_get = False
    supports_groups = True
    supports_get_identity_groups = True

    group_class = Group

    def __init__(
        self,
        multipass: Multipass,
        name: str,
        settings: Dict,
        group_provider_class: Type[GroupProvider] = SQLGroupProvider,
    ):
        """Initialize the identity provider.

        Args:
            multipass: The Flask-Multipass instance
            name: The name of this identity provider instance
            settings: The settings dictionary for this identity
                    provider instance
            group_provider_class: The class to use for the group provider.

        Raise:
            ValueError: If the session_expiry setting is not a positive integer.
        """
        super().__init__(multipass=multipass, name=name, settings=settings)
        self.id_field = self.settings.setdefault("identifier_field", DEFAULT_IDENTIFIER_FIELD)
        self._group_provider = group_provider_class(identity_provider=self)
        self.group_class = self._group_provider.group_class

        self.session_expiry: int = self.settings.get(
            SESSION_EXPIRY_SETTING, DEFAULT_SESSION_EXPIRY
        )
        if not isinstance(self.session_expiry, int) or self.session_expiry <= 0:
            raise ValueError(
                f"{SESSION_EXPIRY_SETTING} {self.session_expiry} must be a positive integer"
            )
        current_app.before_request(self._invalidate_session)

    def get_identity_from_auth(self, auth_info: AuthInfo) -> IdentityInfo:
        """Retrieve identity information after authentication.

        Args:
            auth_info: An AuthInfo instance from an auth provider.

        Raise:
            IdentityRetrievalFailed: If the identifier is missing or there do exist multiple
                in the saml response.

        Returns:
            IdentityInfo: An IdentityInfo instance containing identity information
                          or None if no identity was found.

        """
        identifier = auth_info.data.get(self.id_field)
        if isinstance(identifier, list):
            if len(identifier) != 1:
                raise IdentityRetrievalFailed("Identifier has multiple elements", provider=self)
            identifier = identifier[0]
        if not identifier:
            raise IdentityRetrievalFailed("Identifier missing in saml response", provider=self)

        identity_info = IdentityInfo(self, identifier=identifier, **auth_info.data)

        grp_names = auth_info.data.get(SAML_GRP_ATTR_NAME)

        if grp_names:
            if isinstance(grp_names, str):
                # If only one group is returned, it is returned as a string by saml auth provider
                grp_names = [grp_names]

            if self.session_expiry:
                self._set_flask_session_expiry(self.session_expiry)

        else:
            grp_names = []

        user_groups = self._group_provider.get_user_groups(identifier=identifier)
        for group in user_groups:
            if group.name not in grp_names:
                self._group_provider.remove_group_member(
                    group_name=group.name, identifier=identifier
                )

        for grp_name in grp_names:
            self._group_provider.add_group_member(group_name=grp_name, identifier=identifier)

        return identity_info

    def get_group(self, name: str) -> Optional[Group]:
        """Return a specific group.

        Args:
            name: The name of the group.

        Returns:
            group: An instance of group_class or None if the group does not exist.
        """
        return self._group_provider.get_group(name)

    def search_groups(self, name: str, exact: bool = False) -> Iterable[Group]:
        """Search groups by name.

        Args:
            name: The name to search for.
            exact (bool, optional): If True, the name needs to match exactly,
                                    i.e., no substring matches are performed.

        Yields:
            a matching group_class object.

        """
        compare = operator.eq if exact else operator.contains
        for group in self._group_provider.get_groups():
            if compare(group.name, name):
                yield group

    def get_identity_groups(self, identifier: str) -> Iterable[Group]:
        """Retrieve the groups a user identity belongs to.

        Args:
            identifier: The unique user identifier used by the
                           provider.

        Returns:
             iterable: An iterable of groups
        """
        return self._group_provider.get_user_groups(identifier=identifier)

    def _set_flask_session_expiry(self, expiry: int) -> None:
        """Set the flask session expiry.

        Args:
            expiry: The expiry time in seconds.
        """
        session[EXPIRY_SESSION_KEY] = datetime.now(timezone.utc) + timedelta(seconds=expiry)

    @staticmethod
    def _invalidate_session() -> Optional[Response]:
        """Clear the session if it has expired and redirect to login.

        Returns:
            A redirect response if the session has expired, None otherwise.
        """
        expires = session.get(EXPIRY_SESSION_KEY)
        if expires and expires < datetime.now(timezone.utc):
            session.clear()
            redirect_url = url_for(current_app.config["MULTIPASS_LOGIN_ENDPOINT"])
            next_url = request.url
            url_info = urlsplit(next_url)
            url_is_valid = not url_info.netloc or url_info.netloc == request.host
            if next_url and url_is_valid:
                redirect_url += f"?next={next_url}"
            return redirect(redirect_url)
        return None
