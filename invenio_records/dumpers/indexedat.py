# SPDX-FileCopyrightText: 2022 CERN.
# SPDX-FileCopyrightText: 2025 Graz University of Technology.
# SPDX-License-Identifier: MIT

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
