# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

import os

from mock import patch

from invenio_testing import InvenioTestCase


class TestProcessor(InvenioTestCase):
    """Test processor."""

    @patch('invenio_records.tasks.api.create_record')
    def test_processor_string(self, create_record):
        """Processor - try import string."""
        from invenio_records.manage import create
        self.app.config['RECORD_PROCESSORS'] = {
            'marcxml': 'invenio_records.manage:convert_marcxml'
        }
        create(open(os.path.join(os.path.dirname(__file__),
               "data/sample-records.xml")), input_type="marcxml")
        self.assertEquals(create_record.s.call_count, 2)

    @patch('invenio_records.tasks.api.create_record')
    def test_processor_callable(self, create_record):
        """Processor - try import callable."""
        from invenio_records.manage import create
        from invenio_records.manage import convert_marcxml
        self.app.config['RECORD_PROCESSORS'] = {
            'marcxml': convert_marcxml
        }
        create(open(os.path.join(os.path.dirname(__file__),
               "data/sample-records.xml")), input_type="marcxml")
        self.assertEquals(create_record.s.call_count, 2)
