# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-Records-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Persistent identifier system field for record."""

from invenio_records.dictutils import clear_none, dict_lookup
from invenio_records.systemfields import SystemField


class DictField(SystemField):
    """Dictionary field.

    Provides a shortcut for getting/setting a specific key on a record.
    """

    def __init__(self, key=None, clear_none=False, create_if_missing=True):
        """Initialise the dict field.

        :param key: Key to set (dot notation supported).
        :param clear_none: Boolean to control if empty/None values should be
                           removed.
        :param create_if_missing: If a subkey is missing it will be created if
                                  this option is set to true.
        """
        self.clear_none = clear_none
        self.create_if_missing = create_if_missing
        super().__init__(key=key)

    def __get__(self, instance, class_):
        """Getting the attribute value."""
        if instance is None:
            return self
        return self.get_dictkey(instance)

    def __set__(self, instance, value):
        """Setting a new value."""
        if self.clear_none:
            clear_none(value)
        self.set_dictkey(
            instance, value, create_if_missing=self.create_if_missing)
