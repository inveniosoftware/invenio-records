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

"""Invenio-Records is a metadata storage module."""

import os
import sys

from setuptools import setup
from setuptools.command.test import test as TestCommand

readme = open('README.rst').read()
history = open('CHANGES.rst').read()

requirements = [
    'blinker>=1.4',
    'dojson>=0.1.1',
    'Flask>=0.10.1',
    'six>=1.7.2',
    'jsonpatch>=1.11',
    'jsonschema>=2.5.1',
    'dojson>=0.1.1',
    'intbitset>=2.0',
    'invenio-access>=0.2.0',
    'invenio-base>=0.3.0',
    'invenio-collections>=0.1.2',
    'invenio-ext>=0.3.0',
    'invenio-formatter>=0.2.1',
    'invenio-pidstore>=0.1.2',
    'invenio-search>=0.1.3',
    'invenio-upgrader>=0.1.0',
    'invenio-celery>=0.1.0',
    'SQLAlchemy>=1.0',
]

test_requirements = [
    'unittest2>=1.1.0',
    'httpretty>=0.8.10',
    'Flask_Testing>=0.4.1',
    'pytest>=2.8.0',
    'pytest-cov>=2.1.0',
    'pytest-pep8>=1.0.6',
    'coverage>=4.0.0',
    'invenio-accounts>=0.1.2',
    'invenio-documents>=0.1.0.post2',
    'invenio-testing>=0.1.0',
    'mock>=1.0.0',
]

extras_require = {
    'docs': [
        'Sphinx>=1.3',
        'sphinx_rtd_theme>=0.1.7',
    ],
    'documents': [
        'invenio-documents>=0.1.0',
    ],
    'tests': test_requirements,
}


class PyTest(TestCommand):

    """PyTest Test."""

    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        """Init pytest."""
        TestCommand.initialize_options(self)
        self.pytest_args = []
        try:
            from ConfigParser import ConfigParser
        except ImportError:
            from configparser import ConfigParser
        config = ConfigParser()
        config.read('pytest.ini')
        self.pytest_args = config.get('pytest', 'addopts').split(' ')

    def finalize_options(self):
        """Finalize pytest."""
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        """Run tests."""
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)

# Get the version string. Cannot be done with import!
g = {}
with open(os.path.join('invenio_records', 'version.py'), 'rt') as fp:
    exec(fp.read(), g)
    version = g['__version__']

setup(
    name='invenio-records',
    version=version,
    description=__doc__,
    long_description=readme + '\n\n' + history,
    keywords='invenio records',
    license='GPLv2',
    author='CERN',
    author_email='info@invenio-software.org',
    url='https://github.com/inveniosoftware/invenio-records',
    packages=[
        'invenio_records',
    ],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=requirements,
    extras_require=extras_require,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        "Programming Language :: Python :: 2",
        # 'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        # 'Programming Language :: Python :: 3',
        # 'Programming Language :: Python :: 3.3',
        # 'Programming Language :: Python :: 3.4',
        'Development Status :: 1 - Planning',
    ],
    tests_require=test_requirements,
    cmdclass={'test': PyTest},
)
