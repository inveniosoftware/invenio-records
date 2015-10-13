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

"""Record API."""

from flask import current_app
from invenio_db import db
from jsonpatch import apply_patch
from jsonschema import validate

from .models import Record as RecordMetadata
from .signals import after_record_insert, after_record_update, \
    before_record_insert, before_record_update


class Record(dict):
    """Define API for metadata creation and manipulation."""

    @property
    def __key_aliases__(self):
        """Return key aliases."""
        return current_app.config.get('RECORD_KEY_ALIASES', {})

    def __getitem__(self, key):
        """Try to get aliased item on ``KeyError``."""
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
        """Try to set first the aliased item if exists."""
        if key in self.__key_aliases__:
            if callable(self.__key_aliases__[key]):
                raise TypeError('Complex aliases can not be set')
            return super(Record, self).__setitem__(
                self.__key_aliases__[key], value
            )
        return super(Record, self).__setitem__(key, value)

    def __init__(self, data, model=None):
        """Initialize instance with dictionary data and SQLAlchemy model.

        :param data: dict with record metadata
        :param model: :class:`~invenio_records.models.Record` instance
        """
        self.model = model
        super(Record, self).__init__(data)

    @classmethod
    def create(cls, data, schema=None, identifier_key='recid'):
        """Create a record instance and store it in database."""
        with db.session.begin_nested():
            record = cls(data)

            before_record_insert.send(record)

            if schema is not None:
                validate(record, schema)
                record['$schema'] = schema

            metadata = dict(json=dict(record))
            if identifier_key is not None and \
                    record.get(identifier_key) is not None:
                metadata['id'] = record.get(identifier_key)

            record.model = model = RecordMetadata(**metadata)
            db.session.add(model)

        after_record_insert.send(record)
        return record

    def patch(self, patch):
        """Patch a record metadata and update database row."""
        model = self.model
        data = apply_patch(dict(self), patch)
        return self.__class__(data, model=model)

    def commit(self):
        """Store changes on current instance in database."""
        with db.session.begin_nested():
            before_record_update.send(self)

            if self.model is None:
                self.model = RecordMetadata.query.get(self['recid'])

            self.model.json = dict(self)

            db.session.merge(self.model)

        after_record_update.send(self)
        return self

    @classmethod
    def get_record(cls, recid, *args, **kwargs):
        """Return record instance.

        Raises database exception if record does not exists.
        """
        with db.session.no_autoflush:
            obj = RecordMetadata.query.filter_by(id=recid).one()
            return cls(obj.json, model=obj)

    def dumps(self, **kwargs):
        """Return pure Python dictionary with record metadata."""
        # FIXME add keywords filtering
        # TODO add signal support
        return dict(self)


# Functional interface
create_record = Record.create
get_record = Record.get_record
