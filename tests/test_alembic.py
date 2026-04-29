# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
# Copyright (C) 2026 CESNET z.s.p.o.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test Invenio Records."""

import pytest
from invenio_db.utils import drop_alembic_version_table


def test_alembic(testapp, db):
    """Test alembic recipes."""
    ext = testapp.extensions["invenio-db"]

    if db.engine.name == "sqlite":
        raise pytest.skip("Upgrades are not supported on SQLite.")

    def assert_no_unexpected_migrations():
        # names created by by other tests and registered to sqlalchemy
        extra_names = [
            "custom_metadata",
            "record1_metadata",
            "record2_metadata",
            "record3_metadata",
            "type_model",
        ]
        unexpected_migrations = [
            m
            for m in ext.alembic.compare_metadata()
            if "mock" not in m[1].name.lower() and m[1].name.lower() not in extra_names
        ]
        assert unexpected_migrations == []

    assert_no_unexpected_migrations()
    db.drop_all()
    drop_alembic_version_table()
    ext.alembic.upgrade()

    assert_no_unexpected_migrations()
    ext.alembic.stamp()
    ext.alembic.downgrade(target="96e796392533")
    ext.alembic.upgrade()

    assert_no_unexpected_migrations()
    drop_alembic_version_table()
