# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020-2021 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Relations system field."""

from ..base import SystemField
from .mapping import RelationsMapping
from .relations import RelationBase


#
# System field
#
class RelationsField(SystemField):
    """Relations field for connections to external entities."""

    def __init__(self, **fields):
        """Initialize the field."""
        assert all(isinstance(f, RelationBase) for f in fields.values())
        self._fields = fields

    def __getattr__(self, name):
        """Get a field definition."""
        if name in self._fields:
            return self._fields[name]
        raise AttributeError

    def __iter__(self):
        """Iterate over the configured fields."""
        return iter(getattr(self, f) for f in self._fields)

    def __contains__(self, name):
        """Return if a field exists in the configured fields."""
        return name in self._fields

    #
    # Helpers
    #
    def obj(self, instance):
        """Get the relations object."""
        # Check cache
        obj = self._get_cache(instance)
        if obj:
            return obj
        obj = RelationsMapping(record=instance, fields=self._fields)
        self._set_cache(instance, obj)
        return obj

    #
    # Data descriptor
    #
    def __get__(self, record, owner=None):
        """Accessing the attribute."""
        # Class access
        if record is None:
            return self
        return self.obj(record)

    def __set__(self, instance, values):
        """Setting the attribute."""
        obj = self.obj(instance)
        for k, v in values.items():
            setattr(obj, k, v)

    #
    # Record extension
    #
    def pre_commit(self, record):
        """Initialise the model field."""
        self.obj(record).validate()
        self.obj(record).clean()
