# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Record module signals."""

from blinker import Namespace

_signals = Namespace()

before_record_insert = _signals.signal('before-record-insert')
"""Signal is sent before a record is inserted.

Example subscriber

.. code-block:: python

    def listener(sender, *args, **kwargs):
        sender['key'] = sum(args)

    from invenio_records.signals import before_record_insert
    before_record_insert.connect(listener)
"""

after_record_insert = _signals.signal('after-record-insert')
"""Signal sent after a record is inserted.

.. note::

   No modification are allowed on record object.
"""

before_record_update = _signals.signal('before-record-update')
"""Signal is sent before a record is update."""

after_record_update = _signals.signal('after-record-update')
"""Signal sent after a record is updated."""

before_record_delete = _signals.signal('before-record-delete')
"""Signal is sent before a record is delete."""

after_record_delete = _signals.signal('after-record-delete')
"""Signal sent after a record is delete."""

before_record_revert = _signals.signal('before-record-revert')
"""Signal is sent before a record is revert."""

after_record_revert = _signals.signal('after-record-revert')
"""Signal sent after a record is revert."""
