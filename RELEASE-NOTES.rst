========================
 Invenio-Records v0.3.4
========================

Invenio-Records v0.3.4 was released on October 5, 2015.

About
-----

Invenio-Records is a metadata storage module.

*This is an experimental developer preview release.*

Incompatible changes
--------------------

- Removes legacy bibrecord dependency. (addresses
  inveniosoftware/invenio#3233) (#18) (addresses
  inveniosoftware/invenio#3508)

New features
------------

- Adds new flag to `inveniomanage record create`, `--force` to force
  saving the record to the database even if the recid is already
  there.
- Adds new celery task to save a new record to the database.

Bug fixes
---------

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

Installation
------------

   $ pip install invenio-records==0.3.4

Documentation
-------------

   http://invenio-records.readthedocs.org/en/v0.3.4

Happy hacking and thanks for flying Invenio-Records.

| Invenio Development Team
|   Email: info@invenio-software.org
|   IRC: #invenio on irc.freenode.net
|   Twitter: http://twitter.com/inveniosoftware
|   GitHub: https://github.com/inveniosoftware/invenio-records
|   URL: http://invenio-software.org
