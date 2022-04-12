# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020-2021 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Relation manager instance returned from the record."""


class RelationsMapping:
    """Helper class for managing relation fields."""

    def __init__(self, record, fields):
        """Initialize the relations mapping."""
        # Needed because we overwrite __setattr__
        cache = {}
        super().__setattr__('_inverse_map', {})
        super().__setattr__('_record', record)
        super().__setattr__('_fields', fields)
        super().__setattr__('_cache', cache)
        for name, field in fields.items():
            field.inject_cache(cache, name)
            inv_key = getattr(field, "inv_key", None)
            if inv_key:
                if not self._inverse_map.get(inv_key, None):
                    self._inverse_map[inv_key] = [field.key]
                else:
                    self._inverse_map[inv_key].append([field.key])

    def __getattr__(self, name):
        """Get a relation field."""
        if name in self._fields:
            return self._fields[name].get_value(self._record)
        else:
            raise AttributeError

    def __setattr__(self, name, value):
        """Set a relation field."""
        if name in self._fields:
            field = self._fields[name]
            if value is None:
                field.clear_value(self._record)
            else:
                field.set_value(self._record, value)
        else:
            raise AttributeError

    def __delattr__(self, name):
        """Clear a relation field."""
        setattr(self, name, None)

    def __contains__(self, name):
        """Check if a field is in the mapping."""
        return name in self._fields

    def __iter__(self):
        """Iterate over the relations fields."""
        return iter(self._fields)

    def validate(self, fields=None):
        """Validates all relations in the record."""
        for name in (fields or self):
            getattr(self, name).validate()

    def dereference(self, fields=None):
        """Dereferences relation fields."""
        for name in (fields or self):
            getattr(self, name).dereference()

    def clean(self, fields=None):
        """Clean dereferenced relation fields."""
        for name in (fields or self):
            getattr(self, name).clean()

    def inverse_get(self, inv_key):
        """Get the inverse relations of a field."""
        return self._inverse_map.get(inv_key, None)
