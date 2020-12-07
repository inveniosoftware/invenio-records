# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Relations system field."""

from ..dictutils import dict_lookup, parse_lookup_key
from .base import SystemField


class RelationBase:
    """Base class for defining relation fields."""

    def __init__(self, key=None, attrs=None, _value_key_suffix='id',
                 _clear_empty=True):
        """Initialize the relation."""
        self.key = key
        self.attrs = attrs
        self._value_key_suffix = _value_key_suffix
        self._clear_empty = _clear_empty

    def resolve(self, id_):
        """Resolve a relation by its ID (has to be implemented)."""
        raise NotImplementedError()

    @property
    def value_key(self):
        """Default stored value key getter."""
        return f'{self.key}.{self._value_key_suffix}'

    def validate(self, relations, record):
        """Validate the field."""
        try:
            val = dict_lookup(record, self.value_key)
            if not self.exists(val):
                raise Exception(f'Invalid value {val}.')
        except KeyError:
            return None

    def exists(self, id_):
        """Default existence check by ID."""
        return self.resolve(id_) is not None

    def exists_many(self, ids):
        """Default multiple existence check by a list of IDs."""
        return [self.exists(i) is not None for i in ids]

    def get_value(self, relations, record):
        """Return the resolved relation from a record."""
        # TODO: Instead of a function, a callable class might be better
        def _func(force=False):
            try:
                val = dict_lookup(record, self.value_key)
                obj = self.resolve(val)
                # TODO: Cache the return value (on the record?)
                return obj
            except KeyError:
                return None
        return _func

    def parse_value(self, value):
        """Parse an object to a resolvable ID to be stored."""
        return value

    def set_value(self, relations, record, value):
        """Set the relation value."""
        store_value = self.parse_value(value)
        if self.exists(store_value):
            # TODO: stolen from `SystemField.set_dictkey`
            keys = parse_lookup_key(self.value_key)
            try:
                parent = dict_lookup(record, keys, parent=True)
            except KeyError as e:
                # TODO: parameterize on the field?
                # if not create_if_missing:
                #     raise
                parent = record
                for k in keys[:-1]:
                    if k not in parent:
                        parent[k] = {}
                    else:
                        if not isinstance(parent[k], dict):
                            raise KeyError(
                                f"Expected a dict at subkey '{k}'. "
                                f"Found '{parent[k].__class__.__name__}'."
                            )
                    parent = parent[k]

            if not isinstance(parent, dict):
                raise KeyError(
                    f"Expected a dict at subkey '{keys[-2]}'. "
                    f"Found '{parent.__class__.__name__}'."
                )

            parent[keys[-1]] = store_value
        else:
            raise Exception("Invalid field")

    def clear_value(self, relations, record):
        """Clear the relation value."""
        keys = parse_lookup_key(self.value_key)
        try:
            parent = dict_lookup(record, keys, parent=True)
        except KeyError as e:
            parent = record
            for k in keys[:-1]:
                if k not in parent:  # Nothing to set
                    return
                parent = parent[k]
        parent.pop(keys[-1], None)
        if self._clear_empty and parent == {}:
            parent = dict_lookup(record, keys[:-1], parent=True)
            parent.pop(keys[-2], None)

    def dereference(self, fields=None):
        """Dereferences relations that contain values."""
        pass


class PKRelation(RelationBase):
    """Primary-key relation type."""

    def __init__(self, *args, record_cls=None, **kwargs):
        """Initialize the PK relation."""
        self.record_cls = record_cls
        super().__init__(*args, **kwargs)

    def resolve(self, id_):
        """Resolve the value using the record class."""
        return self.record_cls.get_record(id_)

    def parse_value(self, value):
        """Parse a record (or ID) to the ID to be stored."""
        if isinstance(value, str):
            return value
        elif isinstance(value, self.record_cls):
            return str(value.id)
        else:
            raise Exception(
                f'Invalid value. Expected "str" or "{self.record_cls}"')

    # TODO: We could have a more efficient "exists" via PK queries
    # def exists(self, id_):
    #     """Check if an ID exists using the record class."""
    #     return bool(self.record_cls.model_cls.query.filter_by(id=id_))
    #
    # def exists_many(self, ids):
    #     """."""
    #     self.record_cls.get_record(id_)


class RelationsMapping:
    """Helper class for managing relation fields."""

    def __init__(self, record, fields):
        """Initialize the relations mapping."""
        super().__setattr__('_record', record)
        super().__setattr__('_fields', fields)

    def __getattr__(self, name):
        """Get a relation field."""
        if name in self._fields:
            return self._fields[name].get_value(self, self._record)
        else:
            raise AttributeError

    def __setattr__(self, name, value):
        """Set a relation field."""
        if name in self._fields:
            field = self._fields[name]
            if value is None:
                field.clear_value(self, self._record)
            else:
                field.set_value(self, self._record, value)
        else:
            raise AttributeError

    def __delattr__(self, name):
        """Clear a relation field."""
        self.__setattr__(name, None)

    def __contains__(self, name):
        """Check if a field is in the mapping."""
        return name in self._fields

    def __iter__(self):
        """Iterate over the relations fields."""
        return iter(getattr(self, f) for f in self._fields)

    def validate(self, fields=None):
        """Validates all relations in the record."""
        for name in self._fields:
            self._fields[name].validate(self, self._record)

    def dereference(self, fields=None):
        """Dereferences relations that contain values."""
        pass


class RelationsField(SystemField):
    """Relations field for connections to external entities."""

    def __init__(self, **fields):
        """Initialize the field.

        :param **fields: Relation fields.
        """
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
        record.relations.validate()
