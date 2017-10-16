==========================
 Invenio-Records v1.0.0b3
==========================

Invenio-Records v1.0.0b3 was released on October 16, 2017.

About
-----

Invenio-Records is a metadata storage module.

What's new
----------

- Introduce JSONB for postgreSQL

Incompatible changes
--------------------

- Changes the signals by sending the Flask app as an object instead of proxy.
  More infos http://flask.pocoo.org/docs/0.12/signals/#sending-signals

Bug fixes
---------

- Allows to fully delete a record that was already soft-deleted.
- Fixes bibliographic demo records with invalid MARCXML.

Installation
------------

   $ pip install invenio-records==1.0.0b3

Documentation
-------------

   https://invenio-records.readthedocs.io/

Happy hacking and thanks for flying Invenio-Records.

| Invenio Development Team
|   Email: info@inveniosoftware.org
|   IRC: #invenio on irc.freenode.net
|   Twitter: https://twitter.com/inveniosoftware
|   GitHub: https://github.com/inveniosoftware/invenio-records
|   URL: http://inveniosoftware.org
