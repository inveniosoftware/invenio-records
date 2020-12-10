..
    This file is part of Invenio.
    Copyright (C) 2015-2020 CERN.

    Invenio is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.

Changes
=======

Version 1.5.0 (released TBD)

Version 1.4.0 (released 2020-12-09)

- Backwards incompatible: By default the versioning table is now disabled in
  the ``RecordMetadataBase`` (the ``RecordMetadata`` is still versioned). If
  you subclasses ``RecordMetadataBase`` and needs versioning, you need to add
  the following line in your class:

  .. code-block:: python

        class MyRecordMetadata(db.Model, RecordMetadataBase):
            __versioned__ = {}

- Backwards incompatible: The ``Record.validate()`` method is now split in
  two methods ``validate()`` and ``_validate()``. If you overwrote the
  ``validate()`` method in a subclass, you may need to overwrite instead
  ``_validate()``.

- Backwards incompatible: Due to the JSON encoding/decoding support, the
  Python dictionary representing the record and the SQLAlchemy models are
  separate objects and updating one, won't automatically update the other.
  Normally, you should not have accessed ``record.model.json`` in your code,
  however if you did, you need to rewrite it and rely on the ``create()`` and
  ``commit()`` methods to update the model's ``json`` column.

- Adds a new is_deleted property to the Records API.

- Removes the @ prefix that was used to separate metadata fields from other
  fields.

- Adds a SystemFieldContext which allows knowing the record class when
  accessing the attribute through the class instead of object instance.

- Adds helpers for caching related objects on the record.

- Adds support for JSON encoding/decoding to/from the database. This allows
  e.g. have records with complex data types such as datetime objects.
  JSONSchema validation happens on the JSON encoded version of the record.

- Adds dumpers to support dumping and loading records from secondary copies
  (e.g. records stored in an Elasticsearch index).

- Adds support record extensions as a more strict replacement of signals.
  Allows writing extensions (like the system fields), that integrate into the
  Records API.

- Adds support for system fields that are Python data descriptors on the Record
  which allows for managed access to the Record's dictionary.

- Adds support for disabling signals.

- Adds support for disabling JSONRef replacement.

- Adds support for specifying JSONSchema format checkers and validator class at
  a class-level instead of per validate call.

- Adds support for specifying class-wide JSONSchema format checkers

- Adds a cleaner definition of a what a soft-deleted record using the
  is_deleted hybrid property on the database model.

- Adds support for undeleting a soft-deleted record.

Version 1.3.2 (released 2020-05-27)

- Fixes a bug causing incorrect revisions to be fetched. If ``record.commit()``
  was called multiple times prior to a ``db.session.commit()``, there would be
  gaps in the version ids persisted in the database. This meant that if you
  used ``record.revisions[revision_id]`` to access a revision, it was not
  guaranteed to return that specific revision id. See #221

Version 1.3.1 (released 2020-05-07)

- Deprecated Python versions lower than 3.6.0. Now supporting 3.6.0 and 3.7.0.
- Removed dependency on Invenio-PIDStore and releated documentation.
  Functionality was removed in v1.3.0.

Version 1.3.0 (released 2019-08-01)

- Removed deprecated CLI.

Version 1.2.2 (released 2019-07-11)

- Fix XSS vulnerability in admin interface.

Version 1.2.1 (released 2019-05-14)

- Relax Flask dependency to v0.11.1.

Version 1.2.0 (released 2019-05-08)

- Allow to store RecordMetadata in a custom db table.

Version 1.1.1 (released 2019-07-11)

- Fix XSS vulnerability in admin interface.

Version 1.1.0 (released 2019-02-22)

- Removed deprecated Celery task.
- Deprecated CLI

Version 1.0.2 (released 2019-07-11)

- Fix XSS vulnerability in admin interface.

Version 1.0.1 (released 2018-12-14)

- Fix CliRunner exceptions.
- Fix JSON Schema URL.

Version 1.0.0 (released 2018-03-23)

- Initial public release.
