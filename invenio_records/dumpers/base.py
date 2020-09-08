# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Base class for dumpers."""

from copy import deepcopy


class Dumper:
    """Interface for dumpers."""

    def dump(self, record):
        """Dump a record that can be used a source document for Elasticsearch.

        The job of this method is to create a Python dictionary from the record
        provided in the argument.

        If you overwrite this method without calling super, then you should
        ensure that you make a deep copy of the record dictionary, to avoid
        that changes to the dump affects the record.

        :param record: The record to dump.
        """
        return deepcopy(dict(record))

    def load(self, data, record_cls):
        """Load a record from the source document of an Elasticsearch hit.

        The job of this method, is to create a record of type ``record_cls``
        based on the input ``data``.

        :param data: A Python dictionary representing the data to load.
        :param records_cls: The record class to be constructed.
        :returns: A instance of ``record_cls``.
        """
        raise NotImplementedError()
