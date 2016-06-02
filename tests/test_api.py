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

"""Test Invenio Records API."""

from __future__ import absolute_import, print_function

import copy
import uuid
from datetime import datetime, timedelta

import pytest
from jsonresolver import JSONResolver
from jsonresolver.contrib.jsonref import json_loader_factory
from sqlalchemy.orm.exc import NoResultFound

from invenio_records import Record
from invenio_records.errors import MissingModelError


def strip_ms(dt):
    """Strip microseconds."""
    return dt - timedelta(microseconds=dt.microsecond)


def test_get_records(app, db):
    """Test bulk record fetching."""
    # Create test records
    test_records = [
        Record.create({'title': 'test1'}),
        Record.create({'title': 'to_be_deleted'}),
        Record.create({'title': 'test3'}),
    ]
    db.session.commit()
    test_ids = [record.id for record in test_records]

    # Fetch test records
    assert len(Record.get_records(test_ids)) == 3

    test_records[1].delete()

    # should not show deleted
    db.session.commit()
    assert len(Record.get_records(test_ids)) == 2

    # should show deleted
    assert len(Record.get_records(test_ids, with_deleted=True)) == 3


def test_revision_id_created_updated_properties(app, db):
    """Test properties."""
    record = Record.create({'title': 'test'})
    assert record.revision_id == 0
    dt_c = record.created
    assert dt_c
    dt_u = record.updated
    assert dt_u
    record['title'] = 'test 2'
    record.commit()
    db.session.commit()
    assert record.revision_id == 1
    assert strip_ms(record.created) == strip_ms(dt_c)
    assert strip_ms(record.updated) >= strip_ms(dt_u)

    assert dt_u.tzinfo is None
    utcnow = datetime.utcnow()
    assert dt_u > utcnow - timedelta(seconds=10)
    assert dt_u < utcnow + timedelta(seconds=10)


def test_delete(app, db):
    """Test delete a record."""
    # Create a record, revise it and delete it.
    record = Record.create({'title': 'test 1'})
    db.session.commit()
    record['title'] = 'test 2'
    record.commit()
    db.session.commit()
    record.delete()
    db.session.commit()

    # Deleted records a not retrievable by default
    pytest.raises(NoResultFound, Record.get_record, record.id)

    # Deleted records can be retrieved if you explicit request it
    record = Record.get_record(record.id, with_deleted=True)

    # Deleted records are empty
    assert record == {}
    assert record.model.json is None

    # Deleted records *cannot* be modified
    record['title'] = 'deleted'
    assert pytest.raises(MissingModelError, record.commit)

    # Deleted records *can* be reverted
    record = record.revert(-2)
    assert record['title'] == 'test 2'
    db.session.commit()

    # The "undeleted" record can now be retrieve again
    record = Record.get_record(record.id)
    assert record['title'] == 'test 2'

    # Force deleted record cannot be retrieved again
    record.delete(force=True)
    db.session.commit()
    pytest.raises(
        NoResultFound, Record.get_record, record.id,
        with_deleted=True)


def test_revisions(app, db):
    """Test revisions."""
    # Create a record and make modifications to it.
    record = Record.create({'title': 'test 1'})
    rec_uuid = record.id
    db.session.commit()
    record['title'] = 'test 2'
    record.commit()
    db.session.commit()
    record['title'] = 'test 3'
    record.commit()
    db.session.commit()

    # Get the record
    record = Record.get_record(rec_uuid)
    assert record['title'] == 'test 3'
    assert record.revision_id == 2

    # Retrieve specific revisions
    rev1 = record.revisions[0]
    assert rev1['title'] == 'test 1'
    assert rev1.revision_id == 0

    rev2 = record.revisions[1]
    assert rev2['title'] == 'test 2'
    assert rev2.revision_id == 1

    # Latest revision is identical to record.
    rev_latest = record.revisions[-1]
    assert dict(rev_latest) == dict(record)

    # Revert to a specific revision
    record = record.revert(rev1.revision_id)
    assert record['title'] == 'test 1'
    assert record.created == rev1.created
    assert record.updated != rev1.updated
    assert record.revision_id == 3
    db.session.commit()

    # Get the record again and check it
    record = Record.get_record(rec_uuid)
    assert record['title'] == 'test 1'
    assert record.revision_id == 3

    # Make a change and ensure revision id is changed as well.
    record['title'] = 'modification'
    record.commit()
    db.session.commit()
    assert record.revision_id == 4

    # Iterate over revisions
    assert len(record.revisions) == 5
    revs = list(record.revisions)
    assert revs[0]['title'] == 'test 1'
    assert revs[1]['title'] == 'test 2'
    assert revs[2]['title'] == 'test 3'
    assert revs[3]['title'] == 'test 1'
    assert revs[4]['title'] == 'modification'

    assert 2 in record.revisions
    assert 5 not in record.revisions


def test_record_update_mutable(app, db):
    """Test updating mutables in a record."""
    recid = uuid.UUID('262d2748-ba41-456f-a844-4d043a419a6f')

    # Create a new record with two mutables, a list and a dict
    rec = Record.create(
            {
                'title': 'Title',
                'list': ['foo', ],
                'dict': {'moo': 'boo'},
            },
            id_=recid)
    # Make sure mutables are there before and after commit
    assert rec == {
        'title': 'Title',
        'list': ['foo', ],
        'dict': {'moo': 'boo'}
    }
    db.session.commit()
    db.session.expunge_all()
    rec = Record.get_record(recid)
    assert rec == {
        'title': 'Title',
        'list': ['foo', ],
        'dict': {'moo': 'boo'}
    }

    # Set the mutables under key
    rec['list'] = ['bar', ]
    rec['dict'] = {'eggs': 'bacon'}
    rec.commit()
    # Make sure it commits to DB
    assert rec == {
        'title': 'Title',
        'list': ['bar', ],
        'dict': {'eggs': 'bacon'}
    }
    db.session.commit()
    db.session.expunge_all()
    rec = Record.get_record(recid)
    assert rec == {
        'title': 'Title',
        'list': ['bar', ],
        'dict': {'eggs': 'bacon'}
    }

    # Update the mutables under key
    rec['list'].append('spam')
    rec['dict']['ham'] = 'chicken'
    rec.commit()
    # Make sure it commits to DB
    assert rec == {
        'title': 'Title',
        'list': ['bar', 'spam'],
        'dict': {'eggs': 'bacon', 'ham': 'chicken'}
    }
    db.session.commit()
    db.session.expunge_all()
    rec = Record.get_record(recid)
    assert rec == {
        'title': 'Title',
        'list': ['bar', 'spam'],
        'dict': {'eggs': 'bacon', 'ham': 'chicken'}
    }


def test_missing_model(app, db):
    """Test revisions."""
    record = Record({})
    assert record.id is None
    assert record.revision_id is None
    assert record.created is None
    assert record.updated is None

    try:
        record.revisions
        assert False
    except MissingModelError:
        assert True

    pytest.raises(MissingModelError, record.commit)
    pytest.raises(MissingModelError, record.delete)
    pytest.raises(MissingModelError, record.revert, -1)


def test_record_replace_refs(app, db):
    """Test the replacement of JSON references using JSONResolver."""
    record = Record.create({
        'one': {'$ref': 'http://nest.ed/A'},
        'three': {'$ref': 'http://nest.ed/ABC'}
    })
    app.extensions['invenio-records'].loader_cls = json_loader_factory(
        JSONResolver(plugins=['demo.json_resolver']))
    out_json = record.replace_refs()
    expected_json = {
        'one': {
            'letter': 'A',
            'next': '.',
        },
        'three': {
            'letter': 'A',
            'next': {
                'letter': 'B',
                'next': {
                    'letter': 'C',
                    'next': '.',
                },
            },
        },
    }
    assert out_json == expected_json


def test_replace_refs_deepcopy(app):
    """Test problem with replace_refs and deepcopy."""
    with app.app_context():
        assert copy.deepcopy(Record({'recid': 1}).replace_refs()) \
            == {'recid': 1}


def test_record_dump(app, db):
    """Test record dump method."""
    with app.app_context():
        record = Record.create({'foo': {'bar': 'Bazz', }, })
        record_dump = record.dumps()
        record_dump['foo']['bar'] = 'Spam'
        assert record_dump['foo']['bar'] != record['foo']['bar']
