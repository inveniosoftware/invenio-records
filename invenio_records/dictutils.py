# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Dictionary utilities."""

from copy import deepcopy


def clear_none(d):
    """Clear None values and empty dicts from a dict."""
    del_keys = []
    for k, v in d.items():
        if v is None:
            del_keys.append(k)
        elif isinstance(v, dict):
            clear_none(v)
            if v == {}:
                del_keys.append(k)
        elif isinstance(v, list):
            clear_none_list(v)
            if v == []:
                del_keys.append(k)

    # Delete the keys (cannot be done during the dict iteration)
    for k in del_keys:
        del d[k]


def clear_none_list(ls):
    """Clear values from a list (in-place)."""
    del_idx = []
    for i, v in enumerate(ls):
        if v is None:
            del_idx.append(i)
        elif isinstance(v, list):
            clear_none_list(v)
            if v == []:
                del_idx.append(i)
        elif isinstance(v, dict):
            clear_none(v)
            if v == {}:
                del_idx.append(i)

    # Delete the keys (reverse so index stays stable).
    for i in reversed(del_idx):
        del ls[i]


def parse_lookup_key(lookup_key):
    """Parse a lookup key."""
    if not lookup_key:
        raise KeyError("No lookup key specified")

    # Parse the list of keys
    if isinstance(lookup_key, str):
        keys = lookup_key.split('.')
    elif isinstance(lookup_key, list):
        keys = lookup_key
    else:
        raise TypeError('lookup must be string or list')

    return keys


def dict_lookup(source, lookup_key, parent=False):
    """Make a lookup into a dict based on a dot notation.

    Examples of the supported dot notation:

    - ``'a'`` - Equivalent to ``source['a']``
    - ``'a.b'`` - Equivalent to ``source['a']['b']``
    - ``'a.b.0'`` - Equivalent to ``source['a']['b'][0]`` (for lists)

    List notation is also supported:

    - `['a']``
    - ``['a','b']``
    - ``['a','b', 0]``

    :param source: The dictionary object to perform the lookup in.
    :param parent: If parent argument is True, returns the parent node of
                   matched object.
    :param lookup_key: A string using dot notation, or a list of keys.
    """
    # Copied from dictdiffer (CERN contributed part) and slightly modified.
    keys = parse_lookup_key(lookup_key)

    if parent:
        keys = keys[:-1]

    # Lookup the key
    value = source
    for key in keys:
        try:
            if isinstance(value, list):
                key = int(key)
            value = value[key]
        except (TypeError, IndexError, ValueError) as exc:
            raise KeyError(lookup_key) from exc
    return value
