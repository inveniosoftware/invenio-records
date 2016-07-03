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

"""Invenio-Records is a metadata storage module."""

import os

from setuptools import find_packages, setup

readme = open('README.rst').read()
history = open('CHANGES.rst').read()


tests_require = [
    'check-manifest>=0.25',
    'coverage>=4.0',
    'isort>=4.2.2',
    'mock>=1.0.0',
    'pydocstyle>=1.0.0',
    'pytest-cache>=1.0',
    'pytest-cov>=1.8.0',
    'pytest-pep8>=1.0.6',
    'pytest>=2.8.0',
]

extras_require = {
    'access': [
        'invenio-access>=1.0.0a8',
    ],
    'pidstore': [
        'invenio-pidstore>=1.0.0a9',
    ],
    'docs': [
        'Sphinx>=1.4.2',
    ],
    'mysql': [
        'invenio-db[mysql,versioning]>=1.0.0a10',
    ],
    'postgresql': [
        'invenio-db[postgresql,versioning]>=1.0.0a10',
    ],
    'sqlite': [
        'invenio-db[versioning]>=1.0.0a10',
    ],
    'admin': [
        'Flask-Admin>=1.3.0',
    ],
    'tests': tests_require,
}

extras_require['all'] = []
for name, reqs in extras_require.items():
    if name in ('mysql', 'postgresql', 'sqlite'):
        continue
    extras_require['all'].extend(reqs)

setup_requires = [
    'Babel>=1.3',
    'pytest-runner>=2.6.2',
]

install_requires = [
    'blinker>=1.4',
    'flask-celeryext>=0.1.0',
    'jsonpatch>=1.11',
    'jsonresolver>=0.1.0',
    'jsonref>=0.1',
    'jsonschema>=2.5.1',
    'sqlalchemy-utils>=0.31.0',
]

packages = find_packages()

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
    keywords='invenio metadata',
    license='GPLv2',
    author='CERN',
    author_email='info@inveniosoftware.org',
    url='https://github.com/inveniosoftware/invenio-records',
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    entry_points={
        'invenio_base.apps': [
            'invenio_records = invenio_records:InvenioRecords',
        ],
        'invenio_base.api_apps': [
            'invenio_records = invenio_records:InvenioRecords',
        ],
        'invenio_celery.tasks': [
            'invenio_records = invenio_records.tasks.api',
        ],
        'invenio_db.models': [
            'invenio_records = invenio_records.models',
        ],
        'invenio_i18n.translations': [
            'messages = invenio_records',
        ],
        'invenio_access.actions': [
            'records_read_all'
            ' = invenio_records.permissions:records_read_all',
            'records_create_all'
            ' = invenio_records.permissions:records_create_all',
            'records_update_all'
            ' = invenio_records.permissions:records_update_all',
            'records_delete_all'
            ' = invenio_records.permissions:records_delete_all',
        ],
        'invenio_admin.views': [
            'invenio_records = invenio_records.admin:record_adminview',
        ],
    },
    extras_require=extras_require,
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Development Status :: 3 - Alpha',
    ],
)
