# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
# Copyright (C) 2024-2025 Graz University of Technology.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test for model field.

This tests needs to live in it's own file to have a clean database session.
"""


from datetime import datetime, timezone

import pytest
from models import Record1Metadata

from invenio_records.api import Record
from invenio_records.dumpers import SearchDumper
from invenio_records.systemfields import ModelField, SystemFieldsMixin


def test_model_field(testapp, database):
    """Test model field with clearing none/empty values."""
    db = database

    class Record1(Record, SystemFieldsMixin):
        model_cls = Record1Metadata
        dumper = SearchDumper()
        # Don't do this at home (two system fields on the same model field):
        expires_at = ModelField()
        expires = ModelField("expires_at", dump=False)

    dt = datetime(2020, 9, 3, 0, 0, tzinfo=timezone.utc)
    dt2 = datetime(2020, 9, 4, 0, 0, tzinfo=timezone.utc)

    # Field itself
    assert isinstance(Record1.expires_at, ModelField)

    # Test creating a record with model
    record = Record1.create({}, expires_at=dt)
    db.session.commit()
    assert record.expires_at == dt
    assert record.model.expires_at == dt

    # Test that another field name can be used:
    record = Record1.create({}, expires=dt)
    db.session.commit()
    assert record.expires == dt
    assert record.model.expires_at == dt

    # Test getting a record
    record = Record1.get_record(record.id)
    assert record.expires_at == dt
    assert record.model.expires_at == dt

    # Test assignment
    record.expires_at = dt2
    db.session.commit()
    assert record.expires_at == dt2
    assert record.model.expires_at == dt2

    # Test creating a record without model
    record = Record1({})
    assert record.expires_at is None
    assert record.model is None

    # Creation without model, but with arg will raise attribute error.
    pytest.raises(AttributeError, Record1, {}, expires_at=dt2)
    # Creation without model and without arg is ok.
    assert Record1({}) == {}

    # Test dumping and loading
    record = Record1.create({}, expires_at=dt)
    dump = record.dumps()
    loaded_record = record.loads(dump)
    assert loaded_record.expires_at == record.expires_at

    # Test dumping with None
    record = Record1.create({})
    dump = record.dumps()
    loaded_record = record.loads(dump)
    assert loaded_record.expires_at is None
