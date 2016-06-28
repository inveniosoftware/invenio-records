# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015, 2016 CERN.
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

"""Test Invenio Records."""

from __future__ import absolute_import, print_function

import uuid

import pytest
from flask_principal import UserNeed
from invenio_access import InvenioAccess
from invenio_access.models import ActionUsers
from invenio_accounts.models import User

from invenio_records import Record
from invenio_records.permissions import create_permission_factory, \
    delete_permission_factory, read_permission_factory, records_create_all, \
    records_delete_all, records_read_all, records_update_all, \
    update_permission_factory


class FakeIdentity(object):
    """Fake class to test DynamicPermission."""

    def __init__(self, *provides):
        """Initialize fake identity."""
        self.provides = provides

perm_params = [
    (records_read_all.value, read_permission_factory),
    (records_create_all.value, create_permission_factory),
    (records_update_all.value, update_permission_factory),
    (records_delete_all.value, delete_permission_factory),
]


@pytest.mark.parametrize("action,permission_factory", perm_params)
def test_permission_factory(app, db, action, permission_factory):
    """Test revisions."""
    InvenioAccess(app)

    rec_uuid = uuid.uuid4()

    with db.session.begin_nested():
        user_all = User(email='all@inveniosoftware.org')
        user_one = User(email='one@inveniosoftware.org')
        user_none = User(email='none@inveniosoftware.org')
        db.session.add(user_all)
        db.session.add(user_one)
        db.session.add(user_none)

        db.session.add(ActionUsers(action=action,
                                   user=user_all, argument=None))
        db.session.add(ActionUsers(action=action,
                                   user=user_one, argument=str(rec_uuid)))

        record = Record.create({'title': 'permission test'}, id_=rec_uuid)

    # Create a record and assign permissions.
    permission = permission_factory(record)

    # Assert which permissions has access.
    assert permission.allows(FakeIdentity(UserNeed(user_all.id)))
    assert permission.allows(FakeIdentity(UserNeed(user_one.id)))
    assert not permission.allows(FakeIdentity(UserNeed(user_none.id)))
