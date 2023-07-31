#  Copyright 2023 Canonical Ltd.
#  See LICENSE file for licensing details.

"""The database models for the SAML Groups plugin."""

from typing import List

from indico.core.db import db
from sqlalchemy.orm import Mapped

SCHEMA = "plugin_saml_groups"
group_members_table = db.Table(
    "saml_group_members",
    db.metadata,
    db.Column(
        "group_id",
        db.Integer,
        db.ForeignKey(f"{SCHEMA}.saml_groups.id"),
        primary_key=True,
        nullable=False,
        index=True,
    ),
    db.Column(
        "user_id",
        db.Integer,
        db.ForeignKey(f"{SCHEMA}.saml_users.id"),
        primary_key=True,
        nullable=False,
        index=True,
    ),
    schema=SCHEMA,
)


class SAMLGroup(db.Model):  # pylint: disable=too-few-public-methods
    """The model containing the groups.

    Attrs:
        id: The group's ID
        name: The group's name
    """

    __tablename__ = "saml_groups"
    __table_args__ = {"schema": SCHEMA}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True, index=True)


class SAMLUser(db.Model):  # pylint: disable=too-few-public-methods
    """The model containing the user identifiers.

    Attrs:
        id: The user's ID in the database
        identifier: The user's identifier from the identity provider
        groups: The groups the user is a member of
    """

    __tablename__ = "saml_users"
    __table_args__ = {"schema": SCHEMA}

    id = db.Column(db.Integer, primary_key=True)
    identifier = db.Column(db.String, nullable=False, unique=True, index=True)
    groups: Mapped[List[SAMLGroup]] = db.relationship(
        SAMLGroup,
        secondary=group_members_table,
        back_populates="members",
    )


SAMLGroup.members = db.relationship(
    SAMLUser,
    secondary=group_members_table,
    back_populates="groups",
)
