===========================
 Invenio-Records v1.0.0a13
===========================

Invenio-Records v1.0.0a13 was released on April 1, 2016.

About
-----

Invenio-Records is a metadata storage module.

*This is an experimental developer preview release.*

What's new
----------

- Initial public release after architecture change.

Incompatible changes
--------------------

- Changes primary key of records to UUIDType instead of auto-
  incrementing integers.
- Removes functional interface to records.
- Renames SQLAlchemy model from Record to RecordMetadata to avoid
  naming confusion with API Record class.
- Refactors code to use Invenio-DB and removes legacy code. Web
  interface and REST API will be provided via separate packages.

Bug fixes
---------

- Fixes typo in configuration variables.

Installation
------------

   $ pip install invenio-records==1.0.0a13

Documentation
-------------

   http://pythonhosted.org/invenio-records/

Happy hacking and thanks for flying Invenio-Records.

| Invenio Development Team
|   Email: info@invenio-software.org
|   IRC: #invenio on irc.freenode.net
|   Twitter: http://twitter.com/inveniosoftware
|   GitHub: https://github.com/inveniosoftware/invenio-records
|   URL: http://invenio-software.org
