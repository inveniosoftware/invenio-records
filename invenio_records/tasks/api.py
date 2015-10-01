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

from __future__ import absolute_import


from celery.utils.log import get_task_logger
from sqlalchemy import exc

from invenio_celery import celery

from ..api import Record

logger = get_task_logger(__name__)


@celery.task
def create_record(json, force=False):
    from invenio_ext.sqlalchemy import db
    try:
        return Record.create(json).get('recid')
    except exc.IntegrityError:
        if force:
            current_app.logger.warning(
                "Trying to force insert: {0}".format(json))
            return Record(json).commit().get('recid')
    finally:
        db.session.commit()
