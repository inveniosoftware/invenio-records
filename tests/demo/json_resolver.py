# SPDX-FileCopyrightText: 2015-2018 CERN.
# SPDX-License-Identifier: MIT
"""Test JSON resolver."""

import jsonresolver


@jsonresolver.route("/<item>", host="nest.ed")
def test_resolver(item):
    """Create a nested JSON."""
    next_ = (
        {
            "$ref": "http://nest.ed/{}".format(item[1:]),
        }
        if len(item[1:])
        else "."
    )
    return {"letter": item[0], "next": next_}
