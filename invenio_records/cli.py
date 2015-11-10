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
from flask_cli import with_appcontext
from invenio_db import db


#
# Record management commands
#

@click.group()
def records():
    """Record management commands."""


@records.command()
@click.argument('source', type=click.File('r'), default=sys.stdin)
@click.option('--force', is_flag=True, default=False)
@with_appcontext
def create(source, force):
    """Create new bibliographic record(s)."""
    from .tasks.api import create_record
    data = json.load(source)

    if isinstance(data, dict):
        create_record.delay(data=data, force=force)
    else:
        from celery import group
        job = group([create_record.s(data=item, force=force) for item in data])
        job.apply_async()


@records.command()
@click.argument('patch', type=click.File('r'), default=sys.stdin)
@click.option('-r', '--record', multiple=True)
@with_appcontext
def patch(patch, record):
    """Patch existing bibliographic record."""
    from .api import Record

    patch_content = patch.read()

    if record:
        for rec in record:
            Record.get_record(rec).patch(patch_content).commit()
        db.session.commit()
