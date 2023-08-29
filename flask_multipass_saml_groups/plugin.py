#  Copyright 2023 Canonical Ltd.
#  See LICENSE file for licensing details.
"""Marks the package in order to be used by the Indico plugin system."""
from datetime import datetime, timezone
from typing import Optional

from flask import current_app, redirect, session, url_for
from indico.core.plugins import IndicoPlugin
from werkzeug import Response

from flask_multipass_saml_groups.provider import EXPIRY_SESSION_KEY


class SAMLGroupsPlugin(IndicoPlugin):
    """SAML Groups Plugin.

    The plugin provides an identity provider for SAML which supports groups.
    """

    def init(self) -> None:
        """Init the plugin."""
        super().init()
        current_app.before_request(self._before_request)

    @staticmethod
    def _before_request() -> Optional[Response]:
        """Signal handler for the before_request signal.

        Clears the session if it has expired.

        Returns:
            A redirect response if the session has expired, None otherwise.
        """
        expires = session.get(EXPIRY_SESSION_KEY)
        if expires and expires < datetime.now(timezone.utc):
            session.clear()

            return redirect(url_for("auth.login"))
        return None
