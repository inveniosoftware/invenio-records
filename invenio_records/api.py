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

"""Record API."""

from flask import current_app

from invenio.base.globals import cfg
from invenio.base.helpers import unicodifier
from invenio.base.utils import toposort_send
from invenio.ext.sqlalchemy import db
from invenio.utils.datastructures import SmartDict


from jsonpatch import apply_patch

from jsonschema import validate

from .models import RecordMetadata
from .signals import (
    after_record_insert, after_record_update,
    before_record_insert, before_record_update
)


class Record(SmartDict):

    @property
    def __key_aliases__(self):
        return cfg['RECORD_KEY_ALIASES']

    def __getitem__(self, key):
        try:
            return super(Record, self).__getitem__(key)
        except KeyError:
            if key in self.__key_aliases__:
                if callable(self.__key_aliases__[key]):
                    return self.__key_aliases__[key](self, key)
                else:
                    return super(Record, self).__getitem__(
                        self.__key_aliases__[key]
                    )
            raise

    def __setitem__(self, key, value):
        if key in self.__key_aliases__:
            if callable(self.__key_aliases__[key]):
                raise TypeError('Complex aliases can not be set')
            return super(Record, self).__setitem__(
                self.__key_aliases__[key], value
            )
        return super(Record, self).__setitem__(key, value)

    def __init__(self, data, model=None):
        self.model = model
        super(Record, self).__init__(data)

    @classmethod
    def create(cls, data, schema=None):
        db.session.begin(subtransactions=True)
        try:
            record = cls(unicodifier(data))

            from invenio.modules.jsonalchemy.registry import functions
            list(functions('recordext'))

            toposort_send(before_record_insert, record)

            if schema is not None:
                validate(record, schema)

            metadata = dict(json=dict(record))
            if record.get('recid', None) is not None:
                metadata['id'] = record.get('recid')

            db.session.add(RecordMetadata(**metadata))
            db.session.commit()

            toposort_send(after_record_insert, record)

            return record
        except Exception:
            current_app.logger.exception("Problem creating a record.")
            db.session.rollback()
            raise

    def patch(self, patch):
        model = self.model
        data = apply_patch(dict(self), patch)
        return self.__class__(data, model=model)

    def commit(self):
        db.session.begin(subtransactions=True)
        try:
            toposort_send(before_record_update, self)

            if self.model is None:
                self.model = RecordMetadata.query.get(self['recid'])

            self.model.json = dict(self)

            db.session.add(self.model)
            db.session.commit()

            toposort_send(after_record_update, self)

            return self
        except Exception:
            db.session.rollback()
            raise

    @classmethod
    def get_record(cls, recid, *args, **kwargs):
        obj = RecordMetadata.query.get(recid)
        return cls(obj.json, model=obj) if obj else None

    def dumps(self, **kwargs):
        # FIXME add keywords filtering
        return dict(self)


# Functional interface
create_record = Record.create
get_record = Record.get_record
