# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015 CERN.
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

"""Click command-line interface for record management."""

from __future__ import absolute_import, print_function

import json
import sys

import click
from flask import current_app
from flask_cli import with_appcontext
from invenio_db import db
from sqlalchemy import exc

try:
    from itertools import zip_longest
except ImportError:
    from itertools import izip_longest as zip_longest


#
# Record management commands
#

@click.group()
def records():
    """Record management commands."""


@records.command()
@click.argument('source', type=click.File('r'), default=sys.stdin)
@click.option('-i', '--id', 'ids', multiple=True)
@click.option('--force', is_flag=True, default=False)
@with_appcontext
def create(source, ids, force):
    """Create new bibliographic record(s)."""
    # Make sure that all imports are done with application context.
    from sqlalchemy_continuum import versioning_manager
    from .api import Record
    from .models import RecordMetadata

    data = json.load(source)

    if isinstance(data, dict):
        data = [data]

    if ids:
        assert len(ids) == len(data), 'Not enough identifiers.'

    for record, id_ in zip_longest(data, ids):
        try:
            click.echo(Record.create(record, id_=id_).id)
        except exc.IntegrityError:
            if force:
                current_app.logger.warning(
                    "Trying to force insert: {0}".format(id_))
                # IMPORTANT: We need to create new transtaction for
                # SQLAlchemy-Continuum as we are using no autoflush
                # in Record.get_record.
                uow = versioning_manager.unit_of_work(db.session)
                transaction = uow.create_transaction(db.session)
                # Use low-level database model to retreive an instance.
                model = RecordMetadata.query.get(id_)
                click.echo(Record(record, model=model).commit().id)
            else:
                raise click.BadParameter(
                    'Record with id={0} already exists. If you want to '
                    'override its data use --force.'.format(id_),
                    param_hint='ids',
                )
        db.session.flush()
    db.session.commit()


@records.command()
@click.argument('patch', type=click.File('r'), default=sys.stdin)
@click.option('-i', '--id', 'ids', multiple=True)
@with_appcontext
def patch(patch, ids):
    """Patch existing bibliographic record."""
    from .api import Record

    patch_content = patch.read()

    if ids:
        for id_ in ids:
            Record.get_record(id_).patch(patch_content).commit()
        db.session.commit()
