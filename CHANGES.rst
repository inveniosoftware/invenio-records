..
    This file is part of Invenio.
    Copyright (C) 2015-2019 CERN.

    Invenio is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.

Changes
=======

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
