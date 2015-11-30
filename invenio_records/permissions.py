# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015 CERN.
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

"""Permissions for records.

Note, the permissions are dependent on Invenio-Access so you must install
Invenio-Records with this extra dependency:

.. code-block:: console

   $ pip install invenio-records[access]
"""

from functools import partial

from invenio_access.permissions import DynamicPermission, \
    ParameterizedActionNeed

RecordReadActionNeed = partial(ParameterizedActionNeed, 'records-read')
"""Action need for reading a record."""

records_read_all = RecordReadActionNeed(None)
"""Read all records action need."""


class RecordPermission(DynamicPermission):
    """General dynamic permission for a record."""

    def __init__(self, record):
        """Initialize permission."""
        super(RecordPermission, self).__init__(
            RecordReadActionNeed(str(record.id)))


def permission_factory(record):
    """Factory for creating permissions for records."""
    return RecordPermission(record)
