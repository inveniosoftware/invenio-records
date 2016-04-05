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

"""Test admin interface."""

from __future__ import absolute_import, print_function

import uuid

from flask import url_for
from flask_admin import Admin, menu
from mock import patch
from sqlalchemy.exc import SQLAlchemyError

from invenio_records.admin import record_adminview
from invenio_records.api import Record


def test_admin(app, db):
    """Test flask-admin interace."""
    admin = Admin(app, name="Test")

    assert 'model' in record_adminview
    assert 'modelview' in record_adminview

    # Register both models in admin
    model = record_adminview.pop('model')
    view = record_adminview.pop('modelview')
    admin.add_view(view(model, db.session, **record_adminview))

    # Check if generated admin menu contains the correct items
    menu_items = {str(item.name): item for item in admin.menu()}
    assert 'Records' in menu_items
    assert menu_items['Records'].is_category()

    submenu_items = {
        str(item.name): item for item in menu_items['Records'].get_children()}
    assert 'Record Metadata' in submenu_items
    assert isinstance(submenu_items['Record Metadata'], menu.MenuView)

    # Create a test record.
    rec_uuid = str(uuid.uuid4())
    Record.create({'title': 'test'}, id_=rec_uuid)
    db.session.commit()

    with app.test_request_context():
        index_view_url = url_for('recordmetadata.index_view')
        delete_view_url = url_for('recordmetadata.delete_view')
        detail_view_url = url_for(
            'recordmetadata.details_view', id=rec_uuid)

    with app.test_client() as client:
        # List index view and check record is there.
        res = client.get(index_view_url)
        assert res.status_code == 200

        # Fake a problem with SQLAlchemy.
        with patch('invenio_records.admin.Record') as db_mock:
            db_mock.side_effect = SQLAlchemyError()
            res = client.post(
                delete_view_url, data={'id': rec_uuid}, follow_redirects=True)
            assert res.status_code == 200

        # Delete it.
        res = client.post(
            delete_view_url, data={'id': rec_uuid}, follow_redirects=True)
        assert res.status_code == 200

        # View the delete record
        res = client.get(detail_view_url)
        assert res.status_code == 200
        assert '<pre>null</pre>' in res.get_data(as_text=True)

        # Delete it again
        res = client.post(
            delete_view_url, data={'id': rec_uuid}, follow_redirects=True)
        assert res.status_code == 200
