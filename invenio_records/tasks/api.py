# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Celery tasks for Invenio-Records."""

from __future__ import absolute_import

import warnings

from celery import shared_task
from celery.utils.log import get_task_logger
from flask import current_app
from sqlalchemy import exc

from ..api import Record

logger = get_task_logger(__name__)

warnings.warn(
    "Invenio-Records Celery tasks module will be removed.", DeprecationWarning)


@shared_task
def create_record(data=None, id_=None, force=False):
    """Create a record using a Celery task."""
    from invenio_db import db
    try:
        return str(Record.create(data, id_=id_).id)
    except exc.IntegrityError:
        if force:
            current_app.logger.warning(
                "Trying to force insert: {0}".format(id_))
            record = Record.get_record(id_)
            return str(Record(data, model=record.model).commit().id)
    finally:
        db.session.commit()
