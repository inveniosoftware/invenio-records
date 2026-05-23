# SPDX-FileCopyrightText: 2024 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Alter column from json to jsonb."""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "428b919be0ea"
down_revision = "07fb52561c5c"
branch_labels = ()
depends_on = None


def upgrade():
    """Upgrade database."""
    if op._proxy.migration_context.dialect.name == "postgresql":
        op.alter_column(
            "records_metadata_version",
            "json",
            type_=sa.dialects.postgresql.JSONB,
            postgresql_using="json::text::jsonb",
        )


def downgrade():
    """Downgrade database."""
    if op._proxy.migration_context.dialect.name == "postgresql":
        op.alter_column(
            "records_metadata_version",
            "json",
            type_=sa.dialects.postgresql.JSON,
            postgresql_using="json::text::json",
        )
