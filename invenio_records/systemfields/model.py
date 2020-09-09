# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Constant system field."""

from ..dictutils import dict_lookup
from .base import SystemField


class ModelField(SystemField):
    """Model field for providing get and set access on a model field."""

    def __init__(self, field_name=None):
        """Initialize the field.

        :param field_name: Name of field on the database model.
        """
        self._field_name = field_name

    #
    # Helpers
    #
    @property
    def field_name(self):
        """Propert that uses class attribute name if no field name was set."""
        return self._field_name or self.attr_name

    def _set(self, model, value):
        """Internal method to set value on the model's field."""
        setattr(model, self.field_name, value)

    #
    # Data descriptor
    #
    def __get__(self, instance, class_):
        """Accessing the attribute."""
        # Class access
        if instance is None:
            return self
        # Instance access
        try:
            return getattr(instance.model, self.field_name)
        except AttributeError:
            return None

    def __set__(self, instance, value):
        """Accessing the attribute."""
        self._set(instance.model, value)

    #
    # Record extension
    #
    def post_init(self, record, data, model=None, field_data=None):
        """Initialise the model field."""
        if field_data is not None:
            self._set(model, field_data)
