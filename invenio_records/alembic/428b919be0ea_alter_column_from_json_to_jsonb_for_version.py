# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2024 Graz University of Technology.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

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
