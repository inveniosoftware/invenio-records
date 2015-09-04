========================
 Invenio-Records v0.3.2
========================

Invenio-Records v0.3.2 was released on September 6, 2015.

About
-----

Invenio-Records is a metadata storage module.

*This is an experimental developer preview release.*

Incompatible changes
--------------------

- Removes dependency on legacy bibdocfile module.
  (addresses inveniosoftware/invenio#3233)

Bug fixes
---------

- Disables autoflush when pulling records out of the database, to
  prevent superfluous call to `flush()`. (#24)
- Adds missing `invenio_access` dependency and amends past upgrade
  recipes following its separation into standalone package.
- Loads all recordext functions registered before updating a record
  via `Record.commit()`.

Installation
------------

   $ pip install invenio-records==0.3.2

Documentation
-------------

   http://invenio-records.readthedocs.org/en/v0.3.2

Happy hacking and thanks for flying Invenio-Records.

| Invenio Development Team
|   Email: info@invenio-software.org
|   IRC: #invenio on irc.freenode.net
|   Twitter: http://twitter.com/inveniosoftware
|   GitHub: https://github.com/inveniosoftware/invenio-records
|   URL: http://invenio-software.org
