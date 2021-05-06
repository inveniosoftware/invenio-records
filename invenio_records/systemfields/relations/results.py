# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020-2021 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Relations system field."""

from ...dictutils import dict_lookup, parse_lookup_key
from .errors import InvalidRelationValue


class RelationResult:
    """Relation access result."""

    def __init__(self, field, record):
        """Initialize the relation result."""
        self.field = field
        self.record = record

    def _lookup_id(self):
        return dict_lookup(self.record, self.value_key)

    def _lookup_data(self):
        return dict_lookup(self.record, self.key)

    def __call__(self, force=True):
        """Resolve the relation."""
        try:
            val = self._lookup_id()
            obj = self.resolve(val)
            return obj
        except KeyError:
            return None

    def __getattr__(self, name):
        """Proxy attribute access to field."""
        return getattr(self.field, name)

    def validate(self):
        """Validate the field."""
        try:
            val = self._lookup_id()
            if not self.exists(val):
                raise InvalidRelationValue(f'Invalid value {val}.')
        except KeyError:
            return None

    def dereference(self, attrs=None):
        """Dereference the relation field object inside the record."""
        try:
            data = self._lookup_data()
            return self._dereference_one(data, attrs or self.attrs)
        except KeyError:
            return None

    def clean(self, attrs=None):
        """Clean the dereferenced attributes inside the record."""
        try:
            data = self._lookup_data()
            return self._clean_one(data, attrs or self.attrs)
        except KeyError:
            return None

    def _dereference_one(self, data, attrs):
        """Dereference a single object into a dict."""
        # Don't dereference if already referenced.
        if '@v' in data:
            return
        # Get related record
        obj = self.resolve(data[self.field._value_key_suffix])
        # Inject selected key/values from related record into
        # the current record.
        data.update({
            k: v for k, v in obj.items()
            if attrs is None or k in attrs
        })
        # Add a version counter "@v" used for optimistic
        # concurrency control. It allows to search for all
        # outdated records and reindex them.
        data['@v'] = f'{obj.id}::{obj.revision_id}'
        return data

    def _clean_one(self, data, attrs):
        """Remove all but "id" key for a dereferenced related object."""
        relation_id = data[self.field._value_key_suffix]
        del_keys = ['@v'] + [k for k in data if attrs is None or k in attrs]
        for k in del_keys:
            del data[k]
        data[self.field._value_key_suffix] = relation_id
        return data


class RelationListResult(RelationResult):
    """Relation access result."""

    def __call__(self, force=True):
        """Resolve the relation."""
        try:
            values = self._lookup_data()
            return (self.resolve(v[self._value_key_suffix]) for v in values)
        except KeyError:
            return None

    def _lookup_id(self, data):
        return dict_lookup(data, self.field._value_key_suffix)

    def validate(self):
        """Validate the field."""
        try:
            values = self._lookup_data()
            if values and not isinstance(values, list):
                raise InvalidRelationValue(
                    f'Invalid value {values}, should be list.')

            for v in values:
                relation_id = self._lookup_id(v)
                if not self.exists(relation_id):
                    raise InvalidRelationValue(f'Invalid value {relation_id}.')
        except KeyError:
            return None

    def _apply_items(self, func, attrs=None):
        """Iterate over the list of objects."""
        # The attributes we want to get from the related record.
        attrs = attrs or self.attrs
        try:
            # Get the list of objects we have to dereference/clean.
            values = self._lookup_data()
            if values:
                for v in values:
                    # Only dereference/clean if "id" key is present in parent.
                    # Note, we control via the JSONSchema if a record can have
                    # only related records (by requiring precense of "id" key),
                    # or if you can mix non-linked records.
                    if self.field._value_key_suffix in v:
                        func(v, attrs)
                return values
        except KeyError:
            return None

    def dereference(self, attrs=None):
        """Dereference the relation field object inside the record.

        Dereferences a list of ids::

            [{"id": "eng"}]

        Into

            [{"id": "eng", "title": ..., "@v": ...}]
        """
        return self._apply_items(self._dereference_one, attrs)

    def clean(self, attrs=None):
        """Clean the dereferenced attributes inside the record.

        Reverses changes made by dereference.
        """
        return self._apply_items(self._clean_one, attrs)

    def append(self, value):
        """Append a relation to the list."""
        raise NotImplementedError()

    def insert(self, index, value):
        """Insert a relation to the list."""
        raise NotImplementedError()
