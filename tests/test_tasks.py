# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016 CERN.
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

"""Test celery task."""

from invenio_records.api import Record
from invenio_records.models import RecordMetadata
from invenio_records.tasks.api import create_record


def test_create_record(app, db):
    """Test create record task."""
    r_id = Record.create({'title': 'existing', 'another_key': 'test2'}).id
    db.session.commit()

    # New record
    assert RecordMetadata.query.count() == 1
    create_record({'title': 'test'})
    assert RecordMetadata.query.count() == 2

    # Existing record id - no overwrite
    create_record({'title': 'new val'}, id_=str(r_id))
    assert RecordMetadata.query.count() == 2
    assert Record.get_record(r_id)['title'] == 'existing'

    # Clean session for SQLite.
    db.session.expunge_all()

    # Existing record id - with overwrite
    create_record({'title': 'new val'}, id_=str(r_id), force=True)
    assert RecordMetadata.query.count() == 2
    r = Record.get_record(r_id)
    assert r['title'] == 'new val'
    assert 'another_key' not in r
