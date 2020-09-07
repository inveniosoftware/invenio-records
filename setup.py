# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio-Records is a metadata storage module."""

import os

from setuptools import find_packages, setup

readme = open('README.rst').read()
history = open('CHANGES.rst').read()


tests_require = [
    'mock>=3.0.5',
    'pytest-invenio>=1.3.3',
]

extras_require = {
    'docs': [
        'Sphinx>=2.4',
    ],
    'mysql': [
        'invenio-db[mysql,versioning]>=1.0.5',
    ],
    'postgresql': [
        'invenio-db[postgresql,versioning]>=1.0.5',
    ],
    'sqlite': [
        'invenio-db[versioning]>=1.0.5',
    ],
    'admin': [
        'invenio-admin>=1.2.1',
    ],
    'tests': tests_require,
}

extras_require['all'] = []
for name, reqs in extras_require.items():
    if name in ('mysql', 'postgresql', 'sqlite'):
        continue
    extras_require['all'].extend(reqs)

setup_requires = [
    'Babel>=2.8',
]

install_requires = [
    'arrow>=0.16.0',
    'invenio-base>=1.2.2',
    'invenio-celery>=1.2.0',
    'invenio-i18n>=1.2.0',
    'jsonpatch>=1.26',
    'jsonref>=0.2',
    'jsonresolver>=0.3.1',
    'jsonschema>=3.0.0',
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
    license='MIT',
    author='CERN',
    author_email='info@inveniosoftware.org',
    url='https://github.com/inveniosoftware/invenio-records',
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    entry_points={
        'invenio_admin.views': [
            'invenio_records = invenio_records.admin:record_adminview',
        ],
        'invenio_base.apps': [
            'invenio_records = invenio_records:InvenioRecords',
        ],
        'invenio_base.api_apps': [
            'invenio_records = invenio_records:InvenioRecords',
        ],
        'invenio_celery.tasks': [
            'invenio_records = invenio_records.tasks.api',
        ],
        'invenio_db.alembic': [
            'invenio_records = invenio_records:alembic',
        ],
        'invenio_db.models': [
            'invenio_records = invenio_records.models',
        ],
        'invenio_i18n.translations': [
            'messages = invenio_records',
        ],
    },
    extras_require=extras_require,
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
        'Development Status :: 5 - Production/Stable',
    ],
)
