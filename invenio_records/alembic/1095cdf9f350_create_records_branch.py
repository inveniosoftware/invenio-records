# SPDX-FileCopyrightText: 2016-2018 CERN.
# SPDX-License-Identifier: MIT

"""Create records branch."""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "1095cdf9f350"
down_revision = None
branch_labels = ("invenio_records",)
depends_on = "dbdbc1b19cf2"


def upgrade():
    """Upgrade database."""


def downgrade():
    """Downgrade database."""
