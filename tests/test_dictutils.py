# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test of dictionary utilities."""

from copy import deepcopy

import pytest

from invenio_records.dictutils import clear_none, dict_lookup


def test_clear_none():
    """Test clearning of the dictionary."""
    d = {
        'a': None,
        'b': {
            'c': None
        },
        'd': ['1', None, []],
        'e': [{'a': None, 'b': []}],
    }

    clear_none(d)
    # Modifications are done in place, so gotta test after the function call.
    assert d == {'d': ['1']}

    d = {
        'a': None,
        'b': [
            {'a': '1', 'b': None},
        ],
    }
    clear_none(d)
    # Modifications are done in place, so gotta test after the function call.
    assert d == {'b': [{'a': '1'}]}


def test_dict_lookup():
    """Test lookup by a key."""
    d = {
        'a': 1,
        'b': {
            'c': None
        },
        'd': ['1', '2'],
    }
    assert dict_lookup(d, 'a') == d['a']
    assert dict_lookup(d, 'b') == d['b']
    assert dict_lookup(d, 'b.c') == d['b']['c']
    assert dict_lookup(d, 'd') == d['d']
    assert dict_lookup(d, 'd.0') == d['d'][0]
    assert dict_lookup(d, 'd.1') == d['d'][1]
    assert dict_lookup(d, 'd.-1') == d['d'][-1]

    assert pytest.raises(KeyError, dict_lookup, d, 'x')
    assert pytest.raises(KeyError, dict_lookup, d, 'a.x')
    assert pytest.raises(KeyError, dict_lookup, d, 'b.x')
    assert pytest.raises(KeyError, dict_lookup, d, 'b.c.0')
    assert pytest.raises(KeyError, dict_lookup, d, 'd.3')
