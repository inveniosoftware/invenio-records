# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Perform operations with bibliographic records."""

from __future__ import print_function

import argparse
import sys

import six
from flask import current_app
from sqlalchemy import exc
from werkzeug.utils import import_string

from invenio_ext.script import Manager

manager = Manager(usage=__doc__)


def convert_marcxml(source):
    """Convert MARC XML to JSON."""
    from dojson.contrib.marc21 import marc21
    from dojson.contrib.marc21.utils import create_record, split_blob

    for data in split_blob(source.read()):
        yield marc21.do(create_record(data))


@manager.option('source', type=argparse.FileType('r'), default=sys.stdin,
                help="Input file.", nargs='?')
@manager.option('-s', '--schema', dest='schema', default=None,
                help="URL or path to a JSON Schema.")
@manager.option('-t', '--input-type', dest='input_type', default='json',
                help="Format of input file.")
@manager.option('--force', dest='force', action='store_true',
                help="Force insert.")
def create(source, schema=None, input_type='json', force=False):
    """Create new bibliographic record(s)."""
    from .tasks.api import create_record
    processor = current_app.config['RECORD_PROCESSORS'][input_type]
    if isinstance(processor, six.string_types):
        processor = import_string(processor)
    data = processor(source)

    if isinstance(data, dict):
        create_record.delay(json=data, force=force)
    else:
        from celery import group
        job = group([create_record.s(json=item, force=force) for item in data])
        result = job.apply_async()


@manager.option('-p', '--patch', dest='patch',
                type=argparse.FileType('r'), default=sys.stdin,
                help="Input file with patch.", nargs='?')
@manager.option('recid', nargs='+', type=int)
@manager.option('-s', '--schema', dest='schema', default=None,
                help="URL or path to a JSON Schema.")
def patch(patch, recid=None, schema=None, input_type='jsonpatch'):
    """Patch existing bibliographic record."""
    from .api import Record

    patch_content = patch.read()

    for r in recid or []:
        Record.get_record(r).patch(patch_content).commit()

    db.session.commit()


def main():
    """Run manager."""
    from invenio_base.factory import create_app
    app = create_app()
    manager.app = app
    manager.run()

if __name__ == '__main__':
    main()
