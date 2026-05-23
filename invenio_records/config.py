# SPDX-FileCopyrightText: 2015-2021 CERN.
# SPDX-License-Identifier: MIT

"""Default values for records configuration."""

RECORDS_VALIDATION_TYPES = {}
"""Pass additional types when validating a record against a schema.
For more details, see:
`<https://python-jsonschema.readthedocs.io/en/latest/validate/#validating-types>`_.
"""

RECORDS_REFRESOLVER_CLS = None
"""Custom JSONSchemas ref resolver class.

Note that when using a custom ref resolver class you should also set
``RECORDS_REFRESOLVER_STORE`` to point to a JSONSchema ref resolver store.
"""

RECORDS_REFRESOLVER_STORE = None
"""JSONSchemas ref resolver store.

Used together with ``RECORDS_REFRESOLVER_CLS`` to provide a specific
ref resolver store.
"""
