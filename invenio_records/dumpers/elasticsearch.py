# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Elasticsearch source dumper.

Dumper used to dump/load an the body of an Elasticsearch document.
"""

from copy import deepcopy
from datetime import date, datetime
from uuid import UUID

import arrow
import pytz

from .base import Dumper


class ElasticsearchDumperExt:
    """Interface for Elasticsearch dumper extensions."""

    def dump(self, record, data):
        """Dump the data."""

    def load(self, data, record_cls):
        """Load the data.

        Reverse the changes made by the dump method.
        """


class ElasticsearchDumper(Dumper):
    """Elasticsearch source dumper."""

    def __init__(self, extensions=None, model_fields=None):
        """."""
        self._extensions = extensions or []
        self._model_fields = {
            'id': ('@uuid', UUID),
            'version_id': ('@version_id', int),
            'created': ('created', datetime),
            'updated': ('updated', datetime),
        }
        self._model_fields.update(model_fields or {})

    def _dump_model_field(self, field, key, cast, data, record):
        """Helper method to dump model fields."""
        if record.model:
            val = getattr(record.model, field, None)
        else:
            val = None
        if val is not None and cast:
            if cast in (str, int, bool):
                data[key] = cast(val)
            elif cast in (datetime, date):
                data[key] = pytz.utc.localize(val).isoformat()
            elif cast in (UUID, ):
                data[key] = str(val)
        else:
            data[key] = val

    def _load_model_field(self, key, cast, data):
        """Helper method to load model fields from dump."""
        val = data.pop(key)
        if val is not None and cast:
            if cast in (datetime, date):
                val = arrow.get(val)
                if cast == date:
                    val = val.date
                else:
                    val = val.datetime.replace(tzinfo=None)
            elif cast in (UUID,):
                val = cast(val)
        return val

    def dump(self, record):
        """Dump a record.

        The method adds the following keys (if the record has an associated
        model):

        - ``@uuid`` - UUID of the record.
        - ``@revision`` -  the revision id of the record.
        - ``created`` - Creation timestamp in UTC.
        - ``updated`` - Modification timestamp in UTC.
        """
        # Copy data first, otherwise we modify the record.
        data = super().dump(record)

        # Dump model fields.
        for field, (key, cast) in self._model_fields.items():
            self._dump_model_field(field, key, cast, data, record)

        # Allow extensions to integrate as well.
        for e in self._extensions:
            e.dump(record, data)

        return data

    def load(self, data, record_cls):
        """Load a record from an Elasticsearch document source.

        The method reverses the changes made during the dump. If a model was
        associated, a model will also be initialized.

        .. warning::
            The model is not added to the SQLAlchemy session. If you plan on
            using the model, you must merge it into the session using e.g.:

            .. code-block:: python

                db.session.merge(record.model)
        """
        # First allow extensions to modify the data.
        for e in self._extensions:
            e.load(data, record_cls)

        # Next, extract model fields
        fields_data = {}
        for field, (key, cast) in self._model_fields.items():
            print(field)
            fields_data[field] = self._load_model_field(key, cast, data)

        # Initialize model if an id was provided.
        if fields_data.get('id') is not None:
            fields_data['data'] = data
            print(fields_data)
            model = record_cls.model_cls(**fields_data)
        else:
            model = None

        return record_cls(data, model=model)
