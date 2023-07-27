#  Copyright 2023 Canonical Ltd.
#  See LICENSE file for licensing details.
"""Add common functions for testing."""

from flask import Flask
from indico.core.db import db


def setup_sqlite(app: Flask):
    """Add sqlite to app config and setup the database.

    Args:
        app: The flask app.
    """
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
    with app.app_context():
        db.init_app(app)
        db.session.execute("attach ':memory:' as plugin_saml_groups;")  # pylint: disable=no-member
        db.session.execute(  # pylint: disable=no-member
            "CREATE TABLE plugin_saml_groups.saml_users "
            "(id INTEGER PRIMARY KEY, identifier TEXT UNIQUE);"
        )
        db.session.execute(  # pylint: disable=no-member
            "CREATE TABLE plugin_saml_groups.saml_groups "
            "(id INTEGER PRIMARY KEY, name TEXT UNIQUE);"
        )
        db.session.execute(  # pylint: disable=no-member
            "CREATE TABLE plugin_saml_groups.saml_group_members "
            "(group_id INTEGER, user_id INTEGER);"
        )
        db.session.commit()  # pylint: disable=no-member