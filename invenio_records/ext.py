# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2021 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module for metadata storage."""


from invenio_base.utils import obj_or_import_string
from jsonref import JsonRef
from jsonresolver import JSONResolver
from jsonresolver.contrib.jsonref import json_loader_factory
from jsonresolver.contrib.jsonschema import ref_resolver_factory
from jsonschema import validate
from jsonschema.compat import lru_cache

from invenio_records.errors import RecordsRefResolverConfigError
from invenio_records.resolver import urljoin_with_custom_scheme

from . import config


class _RecordsState(object):
    """State for record JSON resolver."""

    def __init__(self, app, entry_point_group=None):
        """Initialize state."""
        self.app = app
        self.resolver = JSONResolver(entry_point_group=entry_point_group)
        self.refresolver_cls = ref_resolver_factory(self.resolver)
        self.refresolver_store = None
        if (
            self.app.config.get("RECORDS_REFRESOLVER_CLS")
        ):
            self.refresolver_cls = obj_or_import_string(
                self.app.config.get("RECORDS_REFRESOLVER_CLS"),
            )
            self.refresolver_store = obj_or_import_string(
                self.app.config.get("RECORDS_REFRESOLVER_STORE")
            )

        self.loader_cls = json_loader_factory(self.resolver)

    def validate(self, data, schema, **kwargs):
        """Validate data using schema with ``JSONResolver``."""
        if not isinstance(schema, dict):
            schema = {'$ref': schema}
        refresolver_cls_kwargs = {}
        if self.refresolver_store:
            refresolver_cls_kwargs['store'] = self.refresolver_store
            refresolver_cls_kwargs['urljoin_cache'] = \
                lru_cache(1024)(urljoin_with_custom_scheme)
        return validate(
            data,
            schema,
            resolver=self.refresolver_cls.from_schema(
                schema, **refresolver_cls_kwargs),
            types=self.app.config.get('RECORDS_VALIDATION_TYPES', {}),
            **kwargs
        )

    def replace_refs(self, data):
        """Replace the JSON reference objects with ``JsonRef``."""
        return JsonRef.replace_refs(data, loader=self.loader_cls())


class InvenioRecords(object):
    """Invenio-Records extension."""

    def __init__(self, app=None, **kwargs):
        """Extension initialization."""
        if app:
            self._state = self.init_app(app, **kwargs)

    def init_app(self, app,
                 entry_point_group='invenio_records.jsonresolver', **kwargs):
        """Flask application initialization.

        :param app: The Flask application.
        :param entry_point_group: The entrypoint for jsonresolver extensions.
            (Default: ``'invenio_records.jsonresolver'``)
        """
        self.init_config(app)
        state = _RecordsState(app, entry_point_group=entry_point_group)
        app.extensions['invenio-records'] = state
        return state

    def init_config(self, app):
        """Initialize configuration.

        :param app: The Flask application.
        """
        app.config.setdefault('SQLALCHEMY_TRACK_MODIFICATIONS', True)
        for k in dir(config):
            if k.startswith('RECORDS_'):
                app.config.setdefault(k, getattr(config, k))

        if (
            app.config.get("RECORDS_REFRESOLVER_CLS")
            and not app.config.get("RECORDS_REFRESOLVER_STORE")
        ):
            raise RecordsRefResolverConfigError(
                "RECORDS_REFRESOLVER_CLS config requires "
                "RECORDS_REFRESOLVER_STORE to be set."
            )
