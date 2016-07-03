..
    This file is part of Invenio.
    Copyright (C) 2015, 2016 CERN.

    Invenio is free software; you can redistribute it
    and/or modify it under the terms of the GNU General Public License as
    published by the Free Software Foundation; either version 2 of the
    License, or (at your option) any later version.

    Invenio is distributed in the hope that it will be
    useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Invenio; if not, write to the
    Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
    MA 02111-1307, USA.

    In applying this license, CERN does not
    waive the privileges and immunities granted to it by virtue of its status
    as an Intergovernmental Organization or submit itself to any jurisdiction.

Changes
=======

Version 1.0.0a17 (released 2016-07-03)
--------------------------------------

What's new
~~~~~~~~~~

- Initial public release after architecture change.

Incompatible changes
~~~~~~~~~~~~~~~~~~~~

- Changes primary key of records to UUIDType instead of auto-
  incrementing integers.
- Removes functional interface to records.
- Renames SQLAlchemy model from Record to RecordMetadata to avoid
  naming confusion with API Record class.
- Refactors code to use Invenio-DB and removes legacy code. Web
  interface and REST API will be provided via separate packages.

Bug fixes
~~~~~~~~~

- Fixes typo in configuration variables.

Version 0.3.4 (released 2015-10-05)
-----------------------------------

Incompatible changes
~~~~~~~~~~~~~~~~~~~~

- Removes legacy bibrecord dependency. (addresses
  inveniosoftware/invenio#3233) (#18) (addresses
  inveniosoftware/invenio#3508)

New features
~~~~~~~~~~~~

- Adds new flag to `inveniomanage record create`, `--force` to force
  saving the record to the database even if the recid is already
  there.
- Adds new celery task to save a new record to the database.

Bug fixes
~~~~~~~~~

- Adds missing dependencies to mock>=1.0.0, intbitset>=2.0, invenio-
  ext>=0.2.1, SQLAlchemy>=1.0, invenio-documents>=0.1.0, blinker>=1.4,
  dojson>=0.1.1.
- Uses nested transactions instead of sub-transactions to persist
  record modifications. (#22)
- Moves invenio-testing/data/demo_record_marc_data.xml to invenio-
  records/tests/data/demo_record_marc_data.xml.
- Adds missing dependency to invenio-documents>=0.1.0.
- Enables DataCiteTasksTest class which was marked to be enabled after
  module separation.
- Upgrades invenio-base minimum version to 0.3.0.
- Removes dependencies to invenio.utils and replaces them with
  invenio_utils.
- Removes dependencies to invenio.ext and replaces them with
  invenio_ext.
- Removes dependencies to invenio.testsuite and replaces them with
  invenio_testing.
- Removes calls to PluginManager consider_setuptools_entrypoints()
  removed in PyTest 2.8.0.

Version 0.3.3 (released 2015-09-14)
-----------------------------------

Bug fixes
~~~~~~~~~

- Adds missing `invenio_base` dependency.
- Removes dependency on JSONAlchemy from Invenio package.

Version 0.3.2 (released 2015-09-06)
-----------------------------------

Incompatible changes
~~~~~~~~~~~~~~~~~~~~

- Removes dependency on legacy bibdocfile module.
  (addresses inveniosoftware/invenio#3233)

Bug fixes
~~~~~~~~~

- Disables autoflush when pulling records out of the database, to
  prevent superfluous call to `flush()`. (#24)
- Adds missing `invenio_access` dependency and amends past upgrade
  recipes following its separation into standalone package.
- Loads all recordext functions registered before updating a record
  via `Record.commit()`.

Version 0.3.1 (released 2015-08-25)
-----------------------------------

Bug fixes
~~~~~~~~~

- Adds missing `invenio_upgrader` dependency following its separation
  into standalone package.

- Fixes invenio_upgrader imports.

Version 0.3.0 (released 2015-08-18)
-----------------------------------

New features
~~~~~~~~~~~~

- Ports '/export' handler for formatting multiple records.

Bug fixes
~~~~~~~~~

- Fixes imports of externalized packages and adds
  'invenio-collections' to dependency list.

Version 0.2.1 (released 2015-08-12)
-----------------------------------

Bug fixes
~~~~~~~~~

- Adapts tests for non-repeatable subfields fixed in DoJSON==0.1.1.
- Adds missing dependencies "JSONSchema" and  "invenio-formatter".

Version 0.2.0 (released 2015-07-29)
-----------------------------------

New features
~~~~~~~~~~~~

- Moves PID provider for recids and Datacite tasks from Invenio.
- Adds new config variable RECORD_PROCESSORS that allows to specify
  which processors to use depending on the input type.

Improved features
~~~~~~~~~~~~~~~~~

- If no record is found return `None` instead of raising
  `AttributeError`.

Bug fixes
~~~~~~~~~

- Fixes export of records in non HTML formats.

Version 0.1.0 (released 2015-07-03)
-----------------------------------

- Initial public release.
