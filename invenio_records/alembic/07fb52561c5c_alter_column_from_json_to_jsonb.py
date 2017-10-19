# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Alter column from json to jsonb."""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '07fb52561c5c'
down_revision = '862037093962'
branch_labels = ()
depends_on = None


def upgrade():
    """Upgrade database."""
    if op._proxy.migration_context.dialect.name == 'postgresql':
        op.alter_column(
            'records_metadata',
            'json',
            type_=sa.dialects.postgresql.JSONB,
            postgresql_using='json::text::jsonb'
        )


def downgrade():
    """Downgrade database."""
    if op._proxy.migration_context.dialect.name == 'postgresql':
        op.alter_column(
            'records_metadata',
            'json',
            type_=sa.dialects.postgresql.JSON,
            postgresql_using='json::text::json'
        )
