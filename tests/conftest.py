# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.


"""Pytest configuration."""

import pytest
from flask import Flask
from invenio_base import create_app_factory
from invenio_celery import InvenioCelery
from invenio_db import InvenioDB
from invenio_db import db as db_
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.schema import DropConstraint, DropSequence, DropTable
from sqlalchemy_utils.functions import create_database, database_exists

from invenio_records import InvenioRecords


@compiles(DropTable, 'postgresql')
def _compile_drop_table(element, compiler, **kwargs):
    return compiler.visit_drop_table(element) + ' CASCADE'


@compiles(DropConstraint, 'postgresql')
def _compile_drop_constraint(element, compiler, **kwargs):
    return compiler.visit_drop_constraint(element) + ' CASCADE'


@compiles(DropSequence, 'postgresql')
def _compile_drop_sequence(element, compiler, **kwargs):
    return compiler.visit_drop_sequence(element) + ' CASCADE'


@pytest.fixture(scope='module')
def create_app(instance_path):
    """Application factory fixture for use with pytest-invenio."""
    def _create_app(**config):
        app_ = Flask(
            __name__,
            instance_path=instance_path,
        )
        app_.config.update(config)
        InvenioCelery(app_)
        InvenioDB(app_)
        InvenioRecords(app_)
        return app_
    return _create_app


@pytest.fixture(scope='module')
def testapp(base_app, database):
    """Application with just a database.

    Pytest-Invenio also initialises ES with the app fixture.
    """
    yield base_app


@pytest.fixture()
def CustomMetadata(testapp):
    """Class for custom metadata."""
    from invenio_records.models import RecordMetadataBase

    class CustomMetadata(db_.Model, RecordMetadataBase):
        """Custom Record Metadata Model."""

        __tablename__ = 'custom_metadata'
    return CustomMetadata


@pytest.fixture()
def custom_db(testapp, CustomMetadata):
    """Database fixture."""
    InvenioDB(testapp)
    if not database_exists(str(db_.engine.url)):
        create_database(str(db_.engine.url))
    db_.create_all()
    yield db_
    db_.session.remove()
    db_.drop_all()
