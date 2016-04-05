# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015, 2016 CERN.
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

"""Record models."""

import uuid

from invenio_db import db
from sqlalchemy.dialects import postgresql
from sqlalchemy_utils.models import Timestamp
from sqlalchemy_utils.types import JSONType, UUIDType


class RecordMetadata(db.Model, Timestamp):
    """Represent a record metadata inside the SQL database.

    Additionally it contains two columns ``created`` and ``updated``
    with automatically managed timestamps.
    """

    # Enables SQLAlchemy-Continuum versioning
    __versioned__ = {}

    __tablename__ = 'records_metadata'

    id = db.Column(
        UUIDType,
        primary_key=True,
        default=uuid.uuid4,
    )
    """Record identifier."""

    json = db.Column(
        JSONType().with_variant(
            postgresql.JSON(none_as_null=True),
            'postgresql',
        ),
        default=lambda: dict(),
        nullable=True
    )
    """Store metadata in JSON format.

    When you create new ``Record`` the ``json`` field value should
    never be ``NULL``.  Default value is an empty dict.  ``NULL``
    value means that the record metadata has been deleted.
    """

    version_id = db.Column(db.Integer, nullable=False)
    """It is used by SQLAlchemy for optimistic concurrency control."""

    __mapper_args__ = {
        'version_id_col': version_id
    }


__all__ = (
    'RecordMetadata',
)
