# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test for system fields."""


from datetime import date, datetime

import pytest

from invenio_records.api import Record
from invenio_records.systemfields import ConstantField, SystemFieldsMeta, \
    SystemFieldsMixin


def test_constant_field(testapp):
    """Test the constant field."""
    testschema = {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
        },
        "required": ["title"]
    }

    # Make two Record classes so we can test inheritance of system fields.
    class SystemRecord(Record, SystemFieldsMixin):
        test = ConstantField("test", "test")

    class MyRecord(SystemRecord):
        schema = ConstantField("$schema", testschema)

    record = MyRecord.create({'title': 'test'})

    # Test that constant field value was set, and is accessible
    assert record['$schema'] == testschema
    assert record.schema == testschema

    # Test that inherited constant field is also set.
    assert record['test'] == 'test'
    assert record.test == 'test'

    # Test that class access is returning the field
    assert isinstance(MyRecord.schema, ConstantField)
    assert isinstance(MyRecord.test, ConstantField)

    # Test that constant fields cannot have values assigned.
    try:
        record.schema = testschema
        assert False
    except AttributeError:
        pass

    # Explicit remove the set value ($schema) after the record creation.
    record = MyRecord({'title': 'test'})
    del record['$schema']

    # Now test, that accessing the field returns None.
    assert record.schema is None


def test_systemfields_mro(testapp):
    """Test overwriting of system fields according to MRO."""
    class A(Record, SystemFieldsMixin):
        test = ConstantField("test", "a")

    class B(A):
        test = ConstantField("test", "b")

    class C(A):
        pass

    class D(B, C):
        test = ConstantField("test", "d")

    class E(B, C):
        pass

    class F(C):
        pass

    class G(C, B):
        pass

    # A defines field itself
    assert A({}).test == "a"
    # B inherits from A  (overwrites field)
    assert B({}).test == "b"
    # C inherits from A
    assert C({}).test == "a"
    # D inherits from B and C (overwrites field)
    assert D({}).test == "d"
    # E inherits from B and C
    assert E({}).test == "b"
    # F inherits from C which inherits from A.
    assert F({}).test == "a"
    # G inherits from C (which inherits from A) and B.
    assert G({}).test == "b"
