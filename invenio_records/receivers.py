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

from flask import current_app
from flask_sqlalchemy import models_committed


# FIXME add after_delete
@models_committed.connect
def record_modification(sender, changes):
    from .models import RecordMetadata
    from .tasks.index import index_record
    for obj, change in changes:
        if isinstance(obj, RecordMetadata) and change in ('insert', 'update'):
            index_record.delay(obj.id, obj.json)


def new_collection(mapper, connection, target):
    from .tasks.index import index_collection_percolator
    if target.dbquery is not None:
        index_collection_percolator.delay(target.name, target.dbquery)
