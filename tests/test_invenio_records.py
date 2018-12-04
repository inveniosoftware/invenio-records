# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test Invenio Records."""

from __future__ import absolute_import, print_function

import json
import os
import uuid

import pytest
from click.testing import CliRunner
from flask import Flask
from flask.cli import ScriptInfo
from invenio_db.utils import drop_alembic_version_table
from jsonschema.exceptions import ValidationError
from sqlalchemy.orm.exc import NoResultFound

from invenio_records import InvenioRecords, Record, cli
from invenio_records.errors import MissingModelError


def test_version():
    """Test version import."""
    from invenio_records import __version__
    assert __version__


def test_init():
    """Test extension initialization."""
    app = Flask('testapp')
    ext = InvenioRecords(app)
    assert 'invenio-records' in app.extensions

    app = Flask('testapp')
    ext = InvenioRecords()
    assert 'invenio-records' not in app.extensions
    ext.init_app(app)
    assert 'invenio-records' in app.extensions


def test_alembic(app, db):
    """Test alembic recipes."""
    ext = app.extensions['invenio-db']

    if db.engine.name == 'sqlite':
        raise pytest.skip('Upgrades are not supported on SQLite.')

    assert not ext.alembic.compare_metadata()
    db.drop_all()
    drop_alembic_version_table()
    ext.alembic.upgrade()

    assert not ext.alembic.compare_metadata()
    ext.alembic.stamp()
    ext.alembic.downgrade(target='96e796392533')
    ext.alembic.upgrade()

    assert not ext.alembic.compare_metadata()
    drop_alembic_version_table()


def test_db(app, db):
    """Test database backend."""
    with app.app_context():
        assert 'records_metadata' in db.metadata.tables
        assert 'records_metadata_version' in db.metadata.tables
        assert 'transaction' in db.metadata.tables

    schema = {
        'type': 'object',
        'properties': {
            'title': {'type': 'string'},
            'field': {'type': 'boolean'},
            'hello': {'type': 'array'},
        },
        'required': ['title'],
    }
    data = {'title': 'Test', '$schema': schema}
    from invenio_records.models import RecordMetadata as RM

    # Create a record
    with app.app_context():
        assert RM.query.count() == 0

        record_uuid = Record.create(data).id
        db.session.commit()

        assert RM.query.count() == 1
        db.session.commit()

    # Retrieve created record
    with app.app_context():
        record = Record.get_record(record_uuid)
        assert record.dumps() == data
        with pytest.raises(NoResultFound):
            Record.get_record(uuid.uuid4())
        record['field'] = True
        record = record.patch([
            {'op': 'add', 'path': '/hello', 'value': ['world']}
        ])
        assert record['hello'] == ['world']
        record.commit()
        db.session.commit()

    with app.app_context():
        record2 = Record.get_record(record_uuid)
        assert record2.model.version_id == 2
        assert record2['field']
        assert record2['hello'] == ['world']
        db.session.commit()

    # Cannot commit record without model (i.e. Record.create_record)
    with app.app_context():
        record3 = Record({'title': 'Not possible'})
        with pytest.raises(MissingModelError):
            record3.commit()

    # Check invalid schema values
    with app.app_context():
        data = {
            '$schema': 'http://json-schema.org/learn/examples/'
                       'geographical-location.schema.json',
            'latitude': 42,
            'longitude': 42,
        }

        record_with_schema = Record.create(data).commit()
        db.session.commit()

        record_with_schema['latitude'] = 'invalid'
        with pytest.raises(ValidationError):
            record_with_schema.commit()

    # Allow types overriding on schema validation
    with app.app_context():
        data = {
            'title': 'Test',
            'hello': tuple(['foo', 'bar']),
            '$schema': schema
        }
        app.config['RECORDS_VALIDATION_TYPES'] = {}
        with pytest.raises(ValidationError):
            Record.create(data).commit()

        app.config['RECORDS_VALIDATION_TYPES'] = {'array': (list, tuple)}
        record_uuid = Record.create(data).commit()
        db.session.commit()


def test_cli(app, db):
    """Test CLI."""
    runner = CliRunner()
    script_info = ScriptInfo(create_app=lambda info: app)

    assert 'records_metadata' in db.metadata.tables
    assert 'records_metadata_version' in db.metadata.tables
    assert 'transaction' in db.metadata.tables

    from invenio_records.models import RecordMetadata as RM
    from invenio_pidstore.models import PersistentIdentifier, PIDStatus

    # Test merging a base another file.
    with runner.isolated_filesystem():
        with open('record.json', 'wb') as f:
            f.write(json.dumps(
                {'title': 'Test'}, ensure_ascii=False
            ).encode('utf-8'))

        with open('records.json', 'wb') as f:
            f.write(json.dumps(
                [{'title': 'Test1'}, {'title': 'Test2'}], ensure_ascii=False
            ).encode('utf-8'))

        with open('record.patch', 'wb') as f:
            f.write(json.dumps([{
                'op': 'replace', 'path': '/title', 'value': 'Patched Test'
            }], ensure_ascii=False).encode('utf-8'))

        result = runner.invoke(cli.records, [], obj=script_info)
        assert result.exit_code == 0

        with app.app_context():
            assert RM.query.count() == 0

        result = runner.invoke(cli.records, ['create', 'record.json',
                                             '--pid-minter', 'recid'],
                               obj=script_info)
        assert result.exit_code == 0
        recid = result.output.split('\n')[0]

        with app.app_context():
            assert RM.query.count() == 1
            record = RM.query.first()
            assert recid
            assert recid == str(record.id)
            assert "1" == record.json['control_number']
            pid = PersistentIdentifier.query.filter_by(
                object_uuid=record.id).one()
            assert pid.status == PIDStatus.REGISTERED
            assert pid.pid_value

        result = runner.invoke(cli.records,
                               ['patch', 'record.patch', '-i', recid],
                               obj=script_info)
        assert result.exit_code == 0

        with app.app_context():
            record = Record.get_record(recid)
            assert record['title'] == 'Patched Test'
            assert record.model.version_id == 2

        # Test generated UUIDs
        recid1 = uuid.uuid4()
        recid2 = uuid.uuid4()
        assert recid1 != recid2

        # More ids than records.
        result = runner.invoke(
            cli.records,
            ['create', 'record.json', '-i', recid1, '--id', recid2],
            obj=script_info
        )
        assert result.exit_code == 1

        result = runner.invoke(
            cli.records,
            ['create', 'record.json', '-i', recid],
            obj=script_info
        )
        assert result.exit_code == 2

        result = runner.invoke(
            cli.records,
            ['create', 'record.json', '-i', recid, '--force'],
            obj=script_info
        )
        assert result.exit_code == 0

        with app.app_context():
            record = Record.get_record(recid)
            assert record.model.version_id == 3

        result = runner.invoke(
            cli.records,
            ['create', 'records.json', '-i', recid1],
            obj=script_info
        )
        assert result.exit_code == 1

        result = runner.invoke(
            cli.records,
            ['create', 'records.json', '-i', recid1, '-i', recid2],
            obj=script_info
        )
        assert result.exit_code == 0
        with app.app_context():
            assert 3 == RM.query.count()

        # Check metadata after force insert.
        result = runner.invoke(
            cli.records,
            ['create', 'record.json', '-i', recid1, '--force'],
            obj=script_info
        )
        assert result.exit_code == 0
        with app.app_context():
            record = Record.get_record(recid1)
            assert 'Test' == record['title']
            assert 'Test1' == record.revisions[0]['title']

        # More modifications of record 1.
        result = runner.invoke(
            cli.records,
            ['create', 'records.json', '-i', recid1, '--id', recid2,
             '--force'],
            obj=script_info
        )
        assert result.exit_code == 0
        with app.app_context():
            record = Record.get_record(recid1)
            assert 'Test1' == record['title']
            assert 'Test' == record.revisions[1]['title']
            assert 'Test1' == record.revisions[0]['title']

        # Delete records.
        result = runner.invoke(
            cli.records,
            ['delete', '-i', recid1],
            obj=script_info
        )
        assert result.exit_code == 0
        with app.app_context():
            assert RM.query.get(recid1).json is None

        result = runner.invoke(
            cli.records,
            ['delete', '-i', recid1, '--force'],
            obj=script_info
        )
        assert result.exit_code == 0
        with app.app_context():
            assert RM.query.get(recid1) is None

        result = runner.invoke(
            cli.records,
            ['delete', '-i', recid2, '--force'],
            obj=script_info
        )
        assert result.exit_code == 0
        with app.app_context():
            assert RM.query.get(recid2) is None
            assert RM.query.get(recid) is not None
