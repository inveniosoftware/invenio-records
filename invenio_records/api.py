# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Record API."""


from copy import deepcopy

from flask import current_app
from invenio_db import db
from jsonpatch import apply_patch
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy_continuum.utils import parent_class
from werkzeug.local import LocalProxy

from .errors import MissingModelError
from .models import RecordMetadata
from .signals import after_record_delete, after_record_insert, \
    after_record_revert, after_record_update, before_record_delete, \
    before_record_insert, before_record_revert, before_record_update

_records_state = LocalProxy(lambda: current_app.extensions['invenio-records'])


class RecordBase(dict):
    """Base class for Record and RecordRevision to share common features."""

    model_cls = RecordMetadata
    """SQLAlchemy model class defining which table stores the records."""

    format_checker = None
    """Class-level attribute to specify a default JSONSchema format checker."""

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

            >>> validate('bar', {'format': 'foo'},
            ...    format_checker=checker)  # doctest: +IGNORE_EXCEPTION_DETAIL
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
            ...     Draft4Validator,
            ...     validators={'required': lambda v, r, i, s: None}
            ... )
            >>> schema = {
            ...     'type': 'object',
            ...     'properties': {
            ...         'name': { 'type': 'string' },
            ...         'email': { 'type': 'string' },
            ...         'address': {'type': 'string' },
            ...         'telephone': { 'type': 'string' }
            ...     },
            ...     'required': ['name', 'email']
            ... }
            >>> from jsonschema.validators import validate
            >>> validate({}, schema, NoRequiredValidator)

            returns ``None``, which means that the validation was successful,
            while

            >>> validate({}, schema)  # doctest: +IGNORE_EXCEPTION_DETAIL
            Traceback (most recent call last):
            ...
            ValidationError: 'name' is a required property
            ...

            raises a :class:`jsonschema.exceptions.ValidationError`.
        """
        # For backward compatibility we do not change the method signature
        # (i.e. return a ``None`` value on successful validation).
        # The actual implementation of the validation method is implemented
        # below in _validate() which is also the one used internally to avoid
        # double encoding of the dict to JSON.
        self._validate(**kwargs)

    def _validate(self, **kwargs):
        """Implementation of the JSONSchema validation."""
        # Use the encoder to transform Python dictionary into JSON document
        # prior to validation.
        json = self.model_cls.encode(dict(self))

        if '$schema' in self and self['$schema'] is not None:
            # Prepare args
            if self.format_checker:
                kwargs.setdefault("format_checker", self.format_checker)
            kwargs['cls'] = kwargs.pop('validator', None)

            # Validate (an error will raise an exception)
            _records_state.validate(json, self['$schema'], **kwargs)

        # Return encoded data, so we don't have to double encode.
        return json

    def replace_refs(self):
        """Replace the ``$ref`` keys within the JSON."""
        return _records_state.replace_refs(self)

    def dumps(self, **kwargs):
        """Return pure Python dictionary with record metadata."""
        return deepcopy(dict(self))


class Record(RecordBase):
    """Define API for metadata creation and manipulation."""

    send_signals = True
    """Class-level attribute to control if signals should be sent."""

    @classmethod
    def create(cls, data, id_=None, **kwargs):
        r"""Create a new record instance and store it in the database.

        #. Send a signal :data:`invenio_records.signals.before_record_insert`
           with the new record as parameter.

        #. Validate the new record data.

        #. Add the new record in the database.

        #. Send a signal :data:`invenio_records.signals.after_record_insert`
           with the new created record as parameter.

        :Keyword Arguments:
          * **format_checker** --
            An instance of the class :class:`jsonschema.FormatChecker`, which
            contains validation rules for formats. See
            :func:`~invenio_records.api.RecordBase.validate` for more details.

          * **validator** --
            A :class:`jsonschema.IValidator` class that will be used to
            validate the record. See
            :func:`~invenio_records.api.RecordBase.validate` for more details.

        :param data: Dict with the record metadata.
        :param id_: Specify a UUID to use for the new record, instead of
                    automatically generated.
        :returns: A new :class:`Record` instance.
        """
        with db.session.begin_nested():
            record = cls(data)

            if cls.send_signals:
                before_record_insert.send(
                    current_app._get_current_object(),
                    record=record
                )

            # Validate also encodes the data
            json = record._validate(**kwargs)

            # Thus, we pass the encoded JSON directly to the model.
            record.model = cls.model_cls(id=id_, json=json)

            db.session.add(record.model)

        if cls.send_signals:
            after_record_insert.send(
                current_app._get_current_object(),
                record=record
            )

        return record

    @classmethod
    def get_record(cls, id_, with_deleted=False):
        """Retrieve the record by id.

        Raise a database exception if the record does not exist.

        :param id_: record ID.
        :param with_deleted: If `True` then it includes deleted records.
        :returns: The :class:`Record` instance.
        """
        with db.session.no_autoflush:
            query = cls.model_cls.query.filter_by(id=id_)
            if not with_deleted:
                query = query.filter(cls.model_cls.is_deleted != True)  # noqa
            obj = query.one()
            return cls(obj.data, model=obj)

    @classmethod
    def get_records(cls, ids, with_deleted=False):
        """Retrieve multiple records by id.

        :param ids: List of record IDs.
        :param with_deleted: If `True` then it includes deleted records.
        :returns: A list of :class:`Record` instances.
        """
        with db.session.no_autoflush:
            query = cls.model_cls.query.filter(cls.model_cls.id.in_(ids))
            if not with_deleted:
                query = query.filter(cls.model_cls.is_deleted != True)  # noqa

            return [cls(obj.data, model=obj) for obj in query.all()]

    def patch(self, patch):
        """Patch record metadata.

        :params patch: Dictionary of record metadata.
        :returns: A new :class:`Record` instance.
        """
        data = apply_patch(dict(self), patch)
        return self.__class__(data, model=self.model)

    def commit(self, **kwargs):
        r"""Store changes of the current record instance in the database.

        #. Send a signal :data:`invenio_records.signals.before_record_update`
           with the current record to be committed as parameter.

        #. Validate the current record data.

        #. Commit the current record in the database.

        #. Send a signal :data:`invenio_records.signals.after_record_update`
            with the committed record as parameter.

        :Keyword Arguments:
          * **format_checker** --
            An instance of the class :class:`jsonschema.FormatChecker`, which
            contains validation rules for formats. See
            :func:`~invenio_records.api.RecordBase.validate` for more details.

          * **validator** --
            A :class:`jsonschema.IValidator` class that will be used to
            validate the record. See
            :func:`~invenio_records.api.RecordBase.validate` for more details.

        :returns: The :class:`Record` instance.
        """
        if self.model is None or self.model.is_deleted:
            raise MissingModelError()

        with db.session.begin_nested():
            if self.send_signals:
                before_record_update.send(
                    current_app._get_current_object(),
                    record=self
                )

            # Validate also encodes the data
            json = self._validate(**kwargs)

            # Thus, we pass the encoded JSON directly to the model.
            self.model.json = json
            flag_modified(self.model, 'json')

            db.session.merge(self.model)

        if self.send_signals:
            after_record_update.send(
                current_app._get_current_object(),
                record=self
            )
        return self

    def delete(self, force=False):
        """Delete a record.

        If `force` is ``False``, the record is soft-deleted: record data will
        be deleted but the record identifier and the history of the record will
        be kept. This ensures that the same record identifier cannot be used
        twice, and that you can still retrieve its history. If `force` is
        ``True``, then the record is completely deleted from the database.

        #. Send a signal :data:`invenio_records.signals.before_record_delete`
           with the current record as parameter.

        #. Delete or soft-delete the current record.

        #. Send a signal :data:`invenio_records.signals.after_record_delete`
           with the current deleted record as parameter.

        :param force: if ``True``, completely deletes the current record from
               the database, otherwise soft-deletes it.
        :returns: The deleted :class:`Record` instance.
        """
        if self.model is None:
            raise MissingModelError()

        with db.session.begin_nested():
            if self.send_signals:
                before_record_delete.send(
                    current_app._get_current_object(),
                    record=self
                )

            if force:
                db.session.delete(self.model)
            else:
                self.model.is_deleted = True
                db.session.merge(self.model)

        if self.send_signals:
            after_record_delete.send(
                current_app._get_current_object(),
                record=self
            )
        return self

    def revert(self, revision_id):
        """Revert the record to a specific revision.

        #. Send a signal :data:`invenio_records.signals.before_record_revert`
           with the current record as parameter.

        #. Revert the record to the revision id passed as parameter.

        #. Send a signal :data:`invenio_records.signals.after_record_revert`
           with the reverted record as parameter.

        :param revision_id: Specify the record revision id
        :returns: The :class:`Record` instance corresponding to the revision id
        """
        if self.model is None:
            raise MissingModelError()

        revision = self.revisions[revision_id]

        with db.session.begin_nested():
            if self.send_signals:
                # TODO: arguments to this signal does not make sense.
                # Ought to be both record and revision.
                before_record_revert.send(
                    current_app._get_current_object(),
                    record=self
                )

            # Here we explicitly set the json column in order to not
            # encode/decode the json data via the ``data`` property.
            self.model.json = revision.model.json
            flag_modified(self.model.json, 'json')

            db.session.merge(self.model)

        if self.send_signals:
            # TODO: arguments to this signal does not make sense.
            # Ought to be the class being returned just below and should
            # include the revision.
            after_record_revert.send(
                current_app._get_current_object(),
                record=self
            )
        return self.__class__(self.model.data, model=self.model)

    @property
    def revisions(self):
        """Get revisions iterator."""
        if self.model is None:
            raise MissingModelError()

        return RevisionsIterator(self.model)


class RecordRevision(RecordBase):
    """API for record revisions."""

    def __init__(self, model):
        """Initialize instance with the SQLAlchemy model."""
        super(RecordRevision, self).__init__(
            # The version model class does not have the properties of the
            # parent model class, and thus ``model.data`` won't work (which is
            # a Python property on RecordMetadataBase).
            parent_class(model.__class__).decode(model.json),
            model=model
        )


class RevisionsIterator(object):
    """Iterator for record revisions."""

    def __init__(self, model):
        """Initialize instance with the SQLAlchemy model."""
        self._it = None
        self.model = model

    def __len__(self):
        """Get number of revisions."""
        return self.model.versions.count()

    def __iter__(self):
        """Get iterator."""
        self._it = iter(self.model.versions)
        return self

    def __next__(self):
        """Get next revision item."""
        return RecordRevision(next(self._it))

    def __getitem__(self, revision_id):
        """Get a specific revision.

        Revision id is always smaller by 1 from version_id. This was initially
        to ensure that record revisions was zero-indexed similar to arrays
        (e.g. you could do ``record.revisions[0]``). Due to SQLAlchemy
        increasing the version counter via Python instead of the SQL
        insert/update query it's possible to have an "array with holes" and
        thus having it zero-indexed does not make much sense (thus it's like
        this for historical reasons and has not been changed because it's
        diffcult to change - e.g. implies all indexed records in existing
        instances having to be updated.)
        """
        if revision_id < 0:
            return RecordRevision(self.model.versions[revision_id])
        try:
            return RecordRevision(
                self.model.versions.filter_by(
                    version_id=revision_id + 1
                ).one()
            )
        except NoResultFound:
            raise IndexError

    def __contains__(self, revision_id):
        """Test if revision exists."""
        try:
            self[revision_id]
            return True
        except IndexError:
            return False

    def __reversed__(self):
        """Allows to use reversed operator."""
        for version_index in range(self.model.versions.count()):
            yield RecordRevision(self.model.versions[-(version_index+1)])
