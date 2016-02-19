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

"""Flask extension for Invenio-Records."""

from __future__ import absolute_import, print_function

from jsonref import JsonRef
from jsonresolver import JSONResolver
from jsonresolver.contrib.jsonref import json_loader_factory
from jsonresolver.contrib.jsonschema import ref_resolver_factory
from jsonschema import validate

from . import config
from .cli import records as records_cmd


class _RecordsState(object):
    """State for record JSON resolver."""

    def __init__(self, app, entry_point_group=None):
        """Initialize state."""
        self.app = app
        self.resolver = JSONResolver(entry_point_group=entry_point_group)
        self.ref_resolver_cls = ref_resolver_factory(self.resolver)
        self.loader_cls = json_loader_factory(self.resolver)

    def validate(self, data, schema):
        """Validate data using schema with ``JSONResolver``."""
        if not isinstance(schema, dict):
            schema = {'$ref': schema}
        return validate(data, schema,
                        types=self.app.config.get(
                            "RECORDS_VALIDATION_TYPES", {}
                        ),
                        resolver=self.ref_resolver_cls.from_schema(schema))

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
        """Flask application initialization."""
        self.init_config(app)
        app.cli.add_command(records_cmd)
        state = _RecordsState(app, entry_point_group=entry_point_group)
        app.extensions['invenio-records'] = state
        return state

    def init_config(self, app):
        """Initialize configuration."""
        app.config.setdefault('SQLALCHEMY_TRACK_MODIFICATIONS', True)
        for k in dir(config):
            if k.startswith('RECORDS_'):
                app.config.setdefault(k, getattr(config, k))
