# SPDX-FileCopyrightText: 2024-2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Alter datetime columns to utc aware datetime columns."""

import sqlalchemy as sa
from alembic import op
from invenio_db.utils import (
    update_table_columns_column_type_to_datetime,
    update_table_columns_column_type_to_utc_datetime,
)

# revision identifiers, used by Alembic.
revision = "66db9c49c699"
down_revision = "428b919be0ea"
branch_labels = ()
depends_on = None


def _existing_tables():
    """Tables to update, the versioning table does not exist with ``DB_VERSIONING = False``."""
    inspector = sa.inspect(op.get_bind())
    return [
        table_name
        for table_name in ["records_metadata", "records_metadata_version"]
        if inspector.has_table(table_name)
    ]


def upgrade():
    """Upgrade database."""
    for table_name in _existing_tables():
        update_table_columns_column_type_to_utc_datetime(table_name, "created")
        update_table_columns_column_type_to_utc_datetime(table_name, "updated")


def downgrade():
    """Downgrade database."""
    for table_name in _existing_tables():
        update_table_columns_column_type_to_datetime(table_name, "created")
        update_table_columns_column_type_to_datetime(table_name, "updated")
