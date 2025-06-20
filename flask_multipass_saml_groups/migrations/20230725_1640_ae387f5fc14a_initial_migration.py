#  Copyright 2024 Canonical Ltd.
#  See LICENSE file for licensing details.

# noqa  disable qa, because file is autogenerated
# flake8: noqa
# type: ignore

"""initial migration

Revision ID: ae387f5fc14a
Revises:
Create Date: 2023-07-25 16:40:17.110259
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql.ddl import CreateSchema, DropSchema

# revision identifiers, used by Alembic.
revision = "ae387f5fc14a"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():  # noqa
    op.execute(CreateSchema("plugin_saml_groups"))
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "saml_groups",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        schema="plugin_saml_groups",
    )
    with op.batch_alter_table("saml_groups", schema="plugin_saml_groups") as batch_op:
        batch_op.create_index(batch_op.f("ix_saml_groups_name"), ["name"], unique=True)

    op.create_table(
        "saml_users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("identifier", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        schema="plugin_saml_groups",
    )
    with op.batch_alter_table("saml_users", schema="plugin_saml_groups") as batch_op:
        batch_op.create_index(batch_op.f("ix_saml_users_identifier"), ["identifier"], unique=True)

    op.create_table(
        "saml_group_members",
        sa.Column("group_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["plugin_saml_groups.saml_groups.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["plugin_saml_groups.saml_users.id"],
        ),
        sa.PrimaryKeyConstraint("group_id", "user_id"),
        schema="plugin_saml_groups",
    )
    with op.batch_alter_table("saml_group_members", schema="plugin_saml_groups") as batch_op:
        batch_op.create_index(
            batch_op.f("ix_saml_group_members_group_id"), ["group_id"], unique=False
        )
        batch_op.create_index(
            batch_op.f("ix_saml_group_members_user_id"), ["user_id"], unique=False
        )
    # ### end Alembic commands ###


def downgrade():  # noqa
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("saml_group_members", schema="plugin_saml_groups") as batch_op:
        batch_op.drop_index(batch_op.f("ix_saml_group_members_user_id"))
        batch_op.drop_index(batch_op.f("ix_saml_group_members_group_id"))

    op.drop_table("saml_group_members", schema="plugin_saml_groups")
    with op.batch_alter_table("saml_users", schema="plugin_saml_groups") as batch_op:
        batch_op.drop_index(batch_op.f("ix_saml_users_identifier"))

    op.drop_table("saml_users", schema="plugin_saml_groups")
    with op.batch_alter_table("saml_groups", schema="plugin_saml_groups") as batch_op:
        batch_op.drop_index(batch_op.f("ix_saml_groups_name"))

    op.drop_table("saml_groups", schema="plugin_saml_groups")
    # ### end Alembic commands ###
    op.execute(DropSchema("plugin_saml_groups"))
