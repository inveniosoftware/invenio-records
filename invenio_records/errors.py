# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2021 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Errors for Invenio-Records module."""


class RecordsError(Exception):
    """Base class for errors in Invenio-Records module."""


class MissingModelError(RecordsError):
    """Error raised when a record has no model."""


class RecordsRefResolverConfigError(RecordsError):
    """Custom ref resolver configuration it not correct."""
