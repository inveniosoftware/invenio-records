#!/usr/bin/env bash
# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

# Usage:
#   env DB=postgresql SQLALCHEMY_DATABASE_URI=postgresql+psycopg2://invenio:invenio@localhost:5432/invenio POSTGRESQL_VERSION=POSTGRESQL_9_LATEST ./run-tests.sh

# Quit on errors
set -o errexit

# Quit on unbound symbols
set -o nounset

# Always bring down services
function cleanup {
  docker-services-cli down
}
trap cleanup EXIT

python -m check_manifest --ignore ".*-requirements.txt"
python -m sphinx.cmd.build -qnNW docs docs/_build/html
docker-services-cli up ${DB}
python -m pytest
tests_exit_code=$?
exit "$tests_exit_code"
