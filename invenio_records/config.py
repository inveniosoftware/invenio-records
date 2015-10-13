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

"""Package configuration."""

RECORD_BREADCRUMB_TITLE_KEY = 'title_statement.title'
"""Key used to extract the breadcrumb title from the record."""

RECORD_PROCESSORS = {
    'json': 'json.load',
    'marcxml': 'invenio_records.cli:_convert_marcxml',
}
"""Processors used to create records."""

RECORD_KEY_ALIASES = {
    'recid': 'control_number',
    '8560_f': 'electronic_location_and_access.electronic_name',
    '980': 'collections',
    '980__a': 'collections.primary',
    '980__b': 'collections.secondary',
}
