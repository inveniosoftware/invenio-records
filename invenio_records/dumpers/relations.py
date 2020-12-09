# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Relations dumper.

Dumper used to dump/load relations to/from an ElasticSearch body.
"""

from ..dictutils import dict_lookup, parse_lookup_key
from .elasticsearch import ElasticsearchDumperExt


class RelationDumper(ElasticsearchDumperExt):
    """Dumper for a relations field."""

    def __init__(self, key, fields=None):
        """Initialize the dumper."""
        self.key = key
        self.fields = fields

    def dump(self, record, data):
        """Dump relations."""
        relations = getattr(record, self.key)
        relations.dereference(fields=self.fields)

    def load(self, data, record_cls):
        """Load relations."""
        # TODO: figure out what/how to load
        pass
