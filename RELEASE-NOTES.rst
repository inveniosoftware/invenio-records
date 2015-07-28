========================
 Invenio-Records v0.2.0
========================

Invenio-Records v0.2.0 was released on July 29, 2015.

About
-----

Invenio-Records is a metadata storage module.

*This is an experimental development preview release.*

New features
------------

- Moves PID provider for recids and Datacite tasks from Invenio.
- Adds new config variable RECORD_PROCESSORS that allows to specify
  which processors to use depending on the input type.

Improved features
-----------------

- If no record is found return `None` instead of raising
  `AttributeError`.

Bug fixes
---------

- Fixes export of records in non HTML formats.

Installation
------------

   $ pip install invenio-records==0.2.0

Documentation
-------------

   http://invenio-records.readthedocs.org/en/v0.2.0

Happy hacking and thanks for flying Invenio-Records.

| Invenio Development Team
|   Email: info@invenio-software.org
|   IRC: #invenio on irc.freenode.net
|   Twitter: http://twitter.com/inveniosoftware
|   GitHub: https://github.com/inveniosoftware/invenio-records
|   URL: http://invenio-software.org
