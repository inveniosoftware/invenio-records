#!/usr/bin/env bash
# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

# Usage:
#   env DB=postgresql ./run-tests.sh

python -m pydocstyle invenio_records tests docs && \
python -m isort invenio_records tests --check-only --diff && \
python -m check_manifest --ignore ".travis-*" && \
python -m sphinx.cmd.build -qnNW docs docs/_build/html && \
docker-services-cli up ${DB}
python -m pytest
tests_exit_code=$?
docker-services-cli down
exit "$tests_exit_code"
