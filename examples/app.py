# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015, 2016 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Minimal Invenio-Records application example for development.

Create database and tables::

   $ cd examples
   $ export FLASK_APP=app.py
   $ mkdir -p instance
   $ flask db init
   $ flask db create

Create test record::

   $ echo '{"title": "Test title"}' | flask records create \
      -i deadbeef-9fe4-43d3-a08f-38c2b309afba

Run the development server::

   $ flask --debug run --debugger

Retrieve record via web::

   $ curl http://127.0.0.1:5000/deadbeef-9fe4-43d3-a08f-38c2b309afba

Retrieve record via shell::

   $ flask shell
   >>> from invenio_records.api import Record
   >>> Record.get_record('deadbeef-9fe4-43d3-a08f-38c2b309afba')
"""

from __future__ import absolute_import, print_function

import os

import pkg_resources
from flask import Flask, jsonify, render_template
from flask_celeryext import create_celery_app
from flask_cli import FlaskCLI
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

if not hasattr(app, 'cli'):
    from flask_cli import FlaskCLI
    FlaskCLI(app)
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
