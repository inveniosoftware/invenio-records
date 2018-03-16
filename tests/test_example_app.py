# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test example app."""

import os
import signal
import subprocess
import time
from os.path import abspath, dirname, join

import pytest


@pytest.fixture
def example_app():
    """Example app fixture."""
    current_dir = os.getcwd()

    project_dir = dirname(dirname(abspath(__file__)))
    exampleapp_dir = join(project_dir, 'examples')
    os.chdir(exampleapp_dir)

    # Setup example
    cmd = './app-setup.sh'
    exit_status = subprocess.call(cmd, shell=True)
    assert exit_status == 0

    # Starting example web app
    cmd = 'FLASK_APP=app.py FLASK_DEBUG=1 flask run'
    webapp = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                              preexec_fn=os.setsid, shell=True)
    time.sleep(5)

    yield webapp

    # Stop server
    os.killpg(webapp.pid, signal.SIGTERM)

    # Tear down example app
    cmd = './app-teardown.sh'
    subprocess.call(cmd, shell=True)

    # Return to the original directory
    os.chdir(current_dir)


def test_example_app_record_creation(example_app):
    """Test example app record creation."""
    # Testing record creation
    cmd = """echo '{"title": "Test title"}' | """
    cmd += """FLASK_APP=app.py FLASK_DEBUG=1 """
    cmd += """flask records create -i deadbeef-9fe4-43d3-a08f-38c2b309afba"""
    output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
    assert 'deadbeef-9fe4-43d3-a08f-38c2b309afba' in str(output)

    # Testing record retrieval via web
    cmd = 'curl http://127.0.0.1:5000/deadbeef-9fe4-43d3-a08f-38c2b309afba'
    output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
    assert 'Test title' in str(output)

    # Testing record retrieval via shell
    cmd = """echo "from invenio_records.api import Record;"""
    cmd += """Record.get_record('deadbeef-9fe4-43d3-a08f-38c2b309afba')" | """
    cmd += """FLASK_APP=app.py FLASK_DEBUG=1 """
    cmd += """flask shell"""
    output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
    assert 'Test title' in str(output)
