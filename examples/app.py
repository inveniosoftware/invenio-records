# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Minimal Invenio-Records application example for development.

SPHINX-START

Prepare the example app:

.. code-block:: console

   $ pip install -e .[all,sqlite]
   $ cd examples
   $ ./app-setup.sh
   $ export FLASK_APP=app.py FLASK_DEBUG=1
   $ flask run

Now, you can use `invenio-records`. Create a test record via CLI:

.. code-block:: console

   $ echo '{"title": "Test title"}' | flask records create \
      -i deadbeef-9fe4-43d3-a08f-38c2b309afba

Run the development server:

.. code-block:: console

   $ flask run

Retrieve a record via web:

.. code-block:: console

   $ curl http://127.0.0.1:5000/deadbeef-9fe4-43d3-a08f-38c2b309afba

To reset the example application run:

.. code-block:: console

   $ ./app-teardown.sh

See :doc:`usage` for the extensive list of commands.

SPHINX-END
"""

from __future__ import absolute_import, print_function

import os

import pkg_resources
from flask import Flask, jsonify
from flask_celeryext import create_celery_app
from invenio_db import InvenioDB

from invenio_records import InvenioRecords

try:
    pkg_resources.get_distribution('invenio_pidstore')
except pkg_resources.DistributionNotFound:
    HAS_PIDSTORE = False
else:
    HAS_PIDSTORE = True
    from invenio_pidstore import InvenioPIDStore

# Create Flask application
app = Flask(__name__)
app.config.update(
    CELERY_ALWAYS_EAGER=True,
    CELERY_CACHE_BACKEND="memory",
    CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
    CELERY_RESULT_BACKEND="cache",
    SECRET_KEY="CHANGE_ME",
    SECURITY_PASSWORD_SALT="CHANGE_ME_ALSO",
)

db_uri = os.environ.get('SQLALCHEMY_DATABASE_URI')
if db_uri is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri

InvenioDB(app)
InvenioRecords(app)

if HAS_PIDSTORE:
    InvenioPIDStore(app)

celery = create_celery_app(app)


@app.route("/<uuid>")
def index(uuid):
    """Retrieve record."""
    from invenio_records.api import Record
    return jsonify(Record.get_record(uuid))
