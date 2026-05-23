# SPDX-FileCopyrightText: 2020 CERN.
# SPDX-FileCopyrightText: 2026 CESNET i.a.l.e.
# SPDX-License-Identifier: MIT

"""Constant system field."""

from ..dictutils import dict_lookup
from .base import SystemField


class ConstantField(SystemField):
    """Constant fields add a constant value to a key in the record."""

    def __init__(self, key=None, value=""):
        """Initialize the field.

        :param key: The key to set in the dictionary (dot notation supported
                    for nested lookup).
        :param value: The value to set for the key.
        """
        self.value = value
        super().__init__(key=key)

    def pre_init(self, record, data, model=None, **kwargs):
        """Sets the key in the record during record instantiation."""
        if data is None:
            # A deleted record.
            return
        try:
            dict_lookup(data, self.key)
        except KeyError:
            # Key is not present, so add it.
            data[self.key] = self.value

    def post_undelete(self, record):
        """Restore the constant value after a soft-deleted record is undeleted.

        Soft-deleted records are loaded with ``data=None``, so ``pre_init``
        skips them and the constant key is missing. Repopulate it here.
        """
        try:
            dict_lookup(record, self.key)
        except KeyError:
            record[self.key] = self.value

    def __get__(self, record, owner=None):
        """Accessing the attribute."""
        # Class access
        if record is None:
            return self
        # Instance access
        try:
            return dict_lookup(record, self.key)
        except KeyError:
            return None
