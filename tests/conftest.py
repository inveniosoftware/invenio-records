# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
# Copyright (C) 2025 Graz University of Technology.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.


"""Pytest configuration."""

import pytest
from invenio_app.factory import create_app as _create_app
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.schema import DropConstraint, DropSequence, DropTable

from invenio_records.api import Record
from invenio_records.systemfields import SystemFieldsMixin

pytest_plugins = ("celery.contrib.pytest",)


@compiles(DropTable, "postgresql")
def _compile_drop_table(element, compiler, **kwargs):
    return compiler.visit_drop_table(element) + " CASCADE"


@compiles(DropConstraint, "postgresql")
def _compile_drop_constraint(element, compiler, **kwargs):
    return compiler.visit_drop_constraint(element) + " CASCADE"


@compiles(DropSequence, "postgresql")
def _compile_drop_sequence(element, compiler, **kwargs):
    return compiler.visit_drop_sequence(element) + " CASCADE"


@pytest.fixture(scope="module")
def app_config(app_config):
    """Override pytest-invenio app_config fixture."""
    app_config["THEME_FRONTPAGE"] = False
    return app_config


@pytest.fixture(scope="module")
def extra_entry_points():
    """Extra entrypoints."""
    return {
        "invenio_db.models": [
            "mock_models = models",
        ],
    }


@pytest.fixture(scope="module")
def create_app(instance_path, entry_points):
    """Application factory fixture for use with pytest-invenio."""
    return _create_app


@pytest.fixture(scope="module")
def testapp(base_app, database):
    """Application with just a database.

    Pytest-Invenio also initialises ES with the app fixture.
    """
    yield base_app


@pytest.fixture()
def languages(db):
    """Languages fixture."""

    class Language(Record, SystemFieldsMixin):
        pass

    languages_data = (
        {
            "title": "English",
            "iso": "en",
            "information": {"native_speakers": "400 million", "ethnicity": "English"},
        },
        {
            "title": "French",
            "iso": "fr",
            "information": {"native_speakers": "76.8 million", "ethnicity": "French"},
        },
        {
            "title": "Spanish",
            "iso": "es",
            "information": {"native_speakers": "489 million", "ethnicity": "Spanish"},
        },
        {
            "title": "Italian",
            "iso": "it",
            "information": {"native_speakers": "67 million", "ethnicity": "Italians"},
        },
        {
            "title": "Old English",
            "iso": "oe",
            "information": {
                "native_speakers": "400 million",
                "ethnicity": ["English", "Old english"],
            },
        },
    )

    languages = {}
    for lang in languages_data:
        lang_rec = Language.create(lang)
        languages[lang["iso"]] = lang_rec
    db.session.commit()
    return Language, languages
