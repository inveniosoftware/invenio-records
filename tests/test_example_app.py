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

"""Test example app."""

import os
import signal
import subprocess
import sys
import time


def setup_module():
    """Set up before all tests."""
    # switch to examples/app.py
    exampleappdir = os.path.join(os.path.split(sys.path[0])[0],
                                 'examples')
    os.chdir(exampleappdir)


def teardown_module():
    """Tear down after all tests."""
    cmd = 'FLASK_APP=app.py flask db drop --yes-i-know'
    subprocess.call(cmd, shell=True)


def test_example_app():
    """Test example app."""
    # Testing database creation
    for cmd in ['mkdir -p instance',
                'FLASK_APP=app.py flask db init',
                'FLASK_APP=app.py flask db drop --yes-i-know',
                'FLASK_APP=app.py flask db create']:
        exit_status = subprocess.call(cmd, shell=True)
        assert exit_status == 0

    # Testing record creation
    cmd = """echo '{"title": "Test title"}' | \
        FLASK_APP=app.py flask records create \
        -i deadbeef-9fe4-43d3-a08f-38c2b309afba"""
    output = subprocess.check_output(cmd, shell=True)
    assert 'deadbeef-9fe4-43d3-a08f-38c2b309afba' in str(output)

    # Testing record retrieval via shell
    cmd = """echo "from invenio_records.api import Record; \
Record.get_record('deadbeef-9fe4-43d3-a08f-38c2b309afba')" | \
    FLASK_APP=app.py flask shell"""
    output = subprocess.check_output(cmd, shell=True)
    assert 'Test title' in str(output)

    # Starting example web app
    cmd = 'FLASK_APP=app.py flask run'
    webapp = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                              preexec_fn=os.setsid, shell=True)
    time.sleep(5)

    # Testing record retrieval via web
    cmd = 'curl http://127.0.0.1:5000/deadbeef-9fe4-43d3-a08f-38c2b309afba'
    output = subprocess.check_output(cmd, shell=True)
    assert 'Test title' in str(output)

    # Stopping example web app
    os.killpg(webapp.pid, signal.SIGTERM)
