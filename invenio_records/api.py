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

"""Record API."""

from __future__ import absolute_import, print_function

from copy import deepcopy

from flask import current_app
from invenio_db import db
from jsonpatch import apply_patch
from sqlalchemy.orm.attributes import flag_modified
from werkzeug.local import LocalProxy

from .errors import MissingModelError
from .models import RecordMetadata
from .signals import after_record_delete, after_record_insert, \
    after_record_revert, after_record_update, before_record_delete, \
    before_record_insert, before_record_revert, before_record_update

_records_state = LocalProxy(lambda: current_app.extensions['invenio-records'])


class RecordBase(dict):
    """Base class for Record and RecordBase."""

    def __init__(self, data, model=None):
        """Initialize instance with dictionary data and SQLAlchemy model.

        :param data: Dict with record metadata.
        :param model: :class:`~invenio_records.models.RecordMetadata` instance.
        """
        self.model = model
        super(RecordBase, self).__init__(data or {})

    @property
    def id(self):
        """Get model identifier."""
        return self.model.id if self.model else None

    @property
    def revision_id(self):
        """Get revision identifier."""
        return self.model.version_id-1 if self.model else None

    @property
    def created(self):
        """Get creation timestamp."""
        return self.model.created if self.model else None

    @property
    def updated(self):
        """Get last updated timestamp."""
        return self.model.updated if self.model else None

    def validate(self, **kwargs):
        r"""Validate record according to schema defined in ``$schema`` key.

        :Keyword Arguments:
          * **format_checker** --
            A ``format_checker`` is an instance of class
            :class:`jsonschema.FormatChecker` containing business logic to
            validate arbitrary formats. For example:

            >>> from jsonschema import FormatChecker
            >>> from jsonschema.validators import validate
            >>> checker = FormatChecker()
            >>> checker.checks('foo')(lambda el: el.startswith('foo'))
            <function <lambda> at ...>
            >>> validate('foo', {'format': 'foo'}, format_checker=checker)

            returns ``None``, which means that the validation was successful,
            while

            >>> validate('bar', {'format': 'foo'}, format_checker=checker)
            Traceback (most recent call last):
            ...
            ValidationError: 'bar' is not a 'foo'
            ...

            raises a :class:`jsonschema.exceptions.ValidationError`.

          * **validator** --
            A :class:`jsonschema.IValidator` class used for record validation.
            It will be used as `cls` argument when calling
            :func:`jsonschema.validate`. For example

            >>> from jsonschema.validators import extend, Draft4Validator
            >>> NoRequiredValidator = extend(
            ... Draft4Validator,
            ... validators={'required': lambda v, r, i, s: None})
            >>> schema = {
            ... 'type': 'object',
            ... 'properties': {
            ...     'name': { 'type': 'string' },
            ...     'email': { 'type': 'string' },
            ...     'address': {'type': 'string' },
            ...     'telephone': { 'type': 'string' }
            ... },
            ... 'required': ['name', 'email']
            ... }
            >>> from jsonschema.validators import validate
            >>> validate({}, schema, NoRequiredValidator)

            returns ``None``, which means that the validation was successful,
            while

            >>> validate({}, schema)
            Traceback (most recent call last):
            ...
            ValidationError: 'name' is a required property
            ...

            raises a :class:`jsonschema.exceptions.ValidationError`.
        """
        if '$schema' in self and self['$schema'] is not None:
            kwargs['cls'] = kwargs.pop('validator', None)
            return _records_state.validate(self, self['$schema'], **kwargs)
        return True

    def replace_refs(self):
        """Replace the ``$ref`` keys within the JSON."""
        return _records_state.replace_refs(self)

    def dumps(self, **kwargs):
        """Return pure Python dictionary with record metadata."""
        return deepcopy(dict(self))


class Record(RecordBase):
    """Define API for metadata creation and manipulation."""

    @classmethod
    def create(cls, data, id_=None, **kwargs):
        r"""Create a record instance and store it in database.

        Procedure followed:

        #. The signal :data:`invenio_records.signals.before_record_insert` is
            called with the data as function parameter.

        #. The record data is validate.

        #. The record is added in the database.

        #. The signal :data:`invenio_records.signals.after_record_insert` is
            called with the data as function parameter.

        :Keyword Arguments:
          * **format_checker** --
            An instance of class :class:`jsonschema.FormatChecker`, which
            contains validation rules for formats. See
            :func:`~invenio_records.api.RecordBase.validate` for details.

          * **validator** --
            A :class:`jsonschema.IValidator` class that will be used to
            validate. See :func:`~invenio_records.api.RecordBase.validate` for
            details.

        :param data: Dict with record metadata.
        :param id_: Force the UUID for the record.
        :returns: A new Record instance.
        """
        from .models import RecordMetadata
        with db.session.begin_nested():
            record = cls(data)

            before_record_insert.send(record)

            record.validate(**kwargs)

            record.model = RecordMetadata(id=id_, json=record)

            db.session.add(record.model)

        after_record_insert.send(record)
        return record

    @classmethod
    def get_record(cls, id_, with_deleted=False):
        """Get record instance.

        Raises database exception if record does not exists.

        :param id_: Record ID.
        :param with_deleted: If `True` then it includes deleted records.
        :returns: The Record instance.
        """
        with db.session.no_autoflush:
            query = RecordMetadata.query.filter_by(id=id_)
            if not with_deleted:
                query = query.filter(RecordMetadata.json != None)  # noqa
            obj = query.one()
            return cls(obj.json, model=obj)

    @classmethod
    def get_records(cls, ids, with_deleted=False):
        """Get multiple record instances.

        :param ids: List of record ID.
        :param with_deleted: If `True` then it includes deleted records.
        :returns: A list od Record instance.
        """
        with db.session.no_autoflush:
            query = RecordMetadata.query.filter(RecordMetadata.id.in_(ids))
            if not with_deleted:
                query = query.filter(RecordMetadata.json != None)  # noqa

            return [cls(obj.json, model=obj) for obj in query.all()]

    def patch(self, patch):
        """Patch record metadata.

        :params patch: Dictionary of record metadata.
        :returns: A new Record instance.
        """
        data = apply_patch(dict(self), patch)
        return self.__class__(data, model=self.model)

    def commit(self, **kwargs):
        r"""Store changes on current instance in database.

        Procedure followed:

        #. The signal :data:`invenio_records.signals.before_record_update` is
            called with the record as function parameter.

        #. The record data is validate.

        #. The record is committed to the database.

        #. The signal :data:`invenio_records.signals.after_record_update` is
            called with the record as function parameter.

        :Keyword Arguments:
          * **format_checker** --
            An instance of class :class:`jsonschema.FormatChecker`, which
            contains validation rules for formats. See
            :func:`~invenio_records.api.RecordBase.validate` for details.

          * **validator** --
            A :class:`jsonschema.IValidator` class that will be used to
            validate. See :func:`~invenio_records.api.RecordBase.validate` for
            details.

        :returns: The Record instance.
        """
        if self.model is None or self.model.json is None:
            raise MissingModelError()

        with db.session.begin_nested():
            before_record_update.send(self)

            self.validate(**kwargs)

            self.model.json = dict(self)
            flag_modified(self.model, 'json')

            db.session.merge(self.model)

        after_record_update.send(self)
        return self

    def delete(self, force=False):
        """Delete a record.

        If `force` is ``False``, the record is soft-deleted, i.e. the record
        stays in the database. This ensures e.g. that the same record
        identifier cannot be used twice, and that you can still retrieve the
        history of an object. If `force` is True, the record is completely
        removed from the database.

        Procedure followed:

        #. The signal :data:`invenio_records.signals.before_record_delete` is
            called with the record as function parameter.

        #. The record is deleted or soft-deleted.

        #. The signal :data:`invenio_records.signals.after_record_delete` is
            called with the record as function parameter.

        :param force: Completely remove record from database.
        :returns: The Record instance.
        """
        if self.model is None:
            raise MissingModelError()

        with db.session.begin_nested():
            before_record_delete.send(self)

            if force:
                db.session.delete(self.model)
            else:
                self.model.json = None
                db.session.merge(self.model)

        after_record_delete.send(self)
        return self

    def revert(self, revision_id):
        """Revert to a specific revision.

        Procedure followed:

        #. The signal :data:`invenio_records.signals.before_record_revert` is
            called with the record as function parameter.

        #. The record is reverted.

        #. The signal :data:`invenio_records.signals.after_record_revert` is
            called with the reverted record as function parameter.

        :param revision_id: Specify with revision the record should be
            reverted.
        :returns: The new Record instance.
        """
        if self.model is None:
            raise MissingModelError()

        revision = self.revisions[revision_id]

        with db.session.begin_nested():
            before_record_revert.send(self)

            self.model.json = dict(revision)

            db.session.merge(self.model)

        after_record_revert.send(self)
        return self.__class__(self.model.json, model=self.model)

    @property
    def revisions(self):
        """Get revision iterator."""
        if self.model is None:
            raise MissingModelError()

        return RevisionsIterator(self.model)


class RecordRevision(RecordBase):
    """API for record revisions."""

    def __init__(self, model):
        """Initialize revision."""
        super(RecordRevision, self).__init__(model.json, model=model)


class RevisionsIterator(object):
    """Iterator for record revisions."""

    def __init__(self, model):
        """Initialize iterator."""
        self._it = None
        self.model = model

    def __len__(self):
        """Get number of revisions."""
        return self.model.versions.count()

    def __iter__(self):
        """Get iterator."""
        self._it = iter(self.model.versions)
        return self

    def next(self):
        """Python 2.7 compatibility."""
        return self.__next__()  # pragma: no cover

    def __next__(self):
        """Get next revision item."""
        return RecordRevision(next(self._it))

    def __getitem__(self, revision_id):
        """Get a specific revision."""
        return RecordRevision(self.model.versions[revision_id])

    def __contains__(self, revision_id):
        """Test if revision exists."""
        try:
            self[revision_id]
            return True
        except IndexError:
            return False
