# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2024-2026 Graz University of Technology.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Alter datetime columns to utc aware datetime columns."""

from invenio_db.utils import (
    update_table_columns_column_type_to_datetime,
    update_table_columns_column_type_to_utc_datetime,
)

# revision identifiers, used by Alembic.
revision = "66db9c49c699"
down_revision = "428b919be0ea"
branch_labels = ()
depends_on = None


def upgrade():
    """Upgrade database."""
    for table_name in ["records_metadata", "records_metadata_version"]:
        update_table_columns_column_type_to_utc_datetime(table_name, "created")
        update_table_columns_column_type_to_utc_datetime(table_name, "updated")


def downgrade():
    """Downgrade database."""
    for table_name in ["records_metadata", "records_metadata_version"]:
        update_table_columns_column_type_to_datetime(table_name, "created")
        update_table_columns_column_type_to_datetime(table_name, "updated")
