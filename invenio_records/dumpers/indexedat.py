# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2022 CERN.
# Copyright (C) 2025 Graz University of Technology.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Indexed timestamp dumper.

Dumper used to dump/load the indexed time of a record to/from a search engine body.
"""

from datetime import datetime, timezone

from .search import SearchDumperExt


class IndexedAtDumperExt(SearchDumperExt):
    """Dumper for the indexed_at field."""

    def __init__(self, key="indexed_at"):
        """Initialize the dumper."""
        self.key = key

    def dump(self, record, data):
        """Dump relations."""
        data[self.key] = datetime.now(timezone.utc).isoformat()

    def load(self, data, record_cls):
        """Load (remove) indexed data."""
        data.pop(self.key, None)
