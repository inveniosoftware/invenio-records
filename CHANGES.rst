..
    This file is part of Invenio.
    Copyright (C) 2015 CERN.

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
