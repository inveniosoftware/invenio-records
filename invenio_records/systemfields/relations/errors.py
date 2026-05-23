# SPDX-FileCopyrightText: 2020-2021 CERN.
# SPDX-License-Identifier: MIT

"""Relations system field errors."""

from ...errors import RecordsError


class RelationError(RecordsError):
    """Base relation error class."""


class InvalidRelationValue(RelationError):
    """Invalid relation value."""


class InvalidCheckValue(RelationError):
    """Invalid check value."""
