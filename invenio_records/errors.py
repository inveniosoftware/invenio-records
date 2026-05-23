# SPDX-FileCopyrightText: 2015-2021 CERN.
# SPDX-License-Identifier: MIT

"""Errors for Invenio-Records module."""


class RecordsError(Exception):
    """Base class for errors in Invenio-Records module."""


class MissingModelError(RecordsError):
    """Error raised when a record has no model."""


class RecordsRefResolverConfigError(RecordsError):
    """Custom ref resolver configuration it not correct."""
