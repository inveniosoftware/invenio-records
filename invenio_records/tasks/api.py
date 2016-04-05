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

"""Celery tasks for Inveni-Records."""

from __future__ import absolute_import

from celery import shared_task
from celery.utils.log import get_task_logger
from flask import current_app
from sqlalchemy import exc

from ..api import Record

logger = get_task_logger(__name__)


@shared_task
def create_record(data=None, id_=None, force=False):
    """Create record from given data."""
    from invenio_db import db
    try:
        return str(Record.create(data, id_=id_).id)
    except exc.IntegrityError:
        if force:
            current_app.logger.warning(
                "Trying to force insert: {0}".format(id_))
            record = Record.get_record(id_)
            return str(Record(data, model=record.model).commit().id)
    finally:
        db.session.commit()
