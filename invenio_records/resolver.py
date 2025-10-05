# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 TU Wien.
# Copyright (C) 2025 Northwestern University.
# Copyright (C) 2025 Graz University of Technology.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""InvenioRefResolver."""

import urllib.parse

from jsonresolver.contrib.jsonschema import RefResolverBase
from referencing.exceptions import Unresolvable


class InvenioRefResolver(RefResolverBase):
    """Local Invenio JSONSchemas ref resolver class."""

    def resolve_remote(self, uri):
        """Block remote ref resolve."""
        raise Unresolvable(f"{uri} not found in local registry.")


def urljoin_with_custom_scheme(*args, **kwargs):
    """Patch urljoin call when using local store with custom schemes.

    Allows using custom schemes by extending urllib.parse
    configuration (work-around suggested in
    https://bugs.python.org/issue18828). This patch won't
    be needed once https://github.com/Julian/jsonschema/issues/649
    gets fixed.
    """
    for arg in args:
        if isinstance(arg, str) and "://" in arg:
            scheme = arg.split("://")[0]
            if scheme not in urllib.parse.uses_relative:
                urllib.parse.uses_relative.append(scheme)
            if scheme not in urllib.parse.uses_netloc:
                urllib.parse.uses_netloc.append(scheme)

    result = urllib.parse.urljoin(*args, **kwargs)
    # Python 3.14+ has changed the behavior to allow empty fragments,
    # querystrings, ... as per RFC definition
    # (see https://github.com/python/cpython/pull/123273).
    # There is interest in giving more control over the behavior in
    # https://github.com/python/cpython/pull/123305, so it's something to
    # keep an eye on.
    # The generated URLs are supposed to be equivalent, but we strip the
    # anchor here for compatibility with tests and until deemed fine.
    return result.rstrip("#")
