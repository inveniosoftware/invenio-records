# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Constant system field."""

from .base import SystemField


class ConstantField(SystemField):
    """Constant fields add a constant value to a key in the record."""

    def __init__(self, key, value):
        """Initialize the field.

        :param key: The key to set in the dictionary (only top-level keys
                    supported currently).
        :param value: The value to set for the key.
        """
        self.key = key
        self.value = value

    def pre_init(self, record, data, model=None):
        """Sets the key in the record during record instantiation."""
        if self.key not in data:
            data[self.key] = self.value

    def __get__(self, instance, class_):
        """Accessing the attribute."""
        # Class access
        if instance is None:
            return self
        # Instance access
        if self.key in instance:
            return instance[self.key]
        return None
