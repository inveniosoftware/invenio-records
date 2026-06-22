# SPDX-FileCopyrightText: 2020 CERN.
# SPDX-FileCopyrightText: 2026 TU Wien.
# SPDX-License-Identifier: MIT

"""Base class for dumpers."""

from copy import deepcopy


class Dumper:
    """Interface for dumpers."""

    def dump(self, record, data):
        """Dump a record that can be used a source document for the search engine.

        The job of this method is to create a Python dictionary from the record
        provided in the argument.

        If you overwrite this method without calling super, then you should
        ensure that you make a deep copy of the record dictionary, to avoid
        that changes to the dump affects the record.

        :param record: The record to dump.
        :param data: The initial dump data passed in by ``record.dumps()``.
        """
        # We on purpose do not dict merge the record into the data. "data"
        # holds whatever pre_dump() extensions decided to include, pre_dump
        # methods should always write to top-level keys that are not
        # conflicting with any of the record's keys. pre_dump methods can be
        # used to preprocess the record before dumping (e.g. caching/fetching
        # things.
        data.update(self._copy_record(record))
        return data

    def load(self, data, record_cls):
        """Load a record from the source document of a search engine hit.

        The job of this method, is to create a record of type ``record_cls``
        based on the input ``data``.

        :param data: A Python dictionary representing the data to load.
        :param records_cls: The record class to be constructed.
        :returns: A instance of ``record_cls``.
        """
        raise NotImplementedError()

    def _copy_record(self, record):
        """Copy the given record's data sufficiently deeply.

        This method takes care of creating a sufficiently deep copy of the given
        record, to avoid side effects of the dumping to affect the original
        record's data.

        This method can be overridden in implementations to provide simpler copy
        strategies that are still appropriate for the use cases, since ``deepcopy()``
        can be a very costly operation.

        :param record: The record to copy.
        :returns: An appropriately deep copy of the record.
        """
        return deepcopy(dict(record))
