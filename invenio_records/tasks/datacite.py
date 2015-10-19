# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2014, 2015 CERN.
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

"""Define tasks for managing Datacite DOIs."""

from __future__ import absolute_import

from celery.utils.log import get_task_logger

from flask import current_app

from invenio_base.globals import cfg

from invenio_celery import InvenioCelery

from invenio_formatter import format_record

from invenio_pidstore.models import PersistentIdentifier

from ..api import get_record

# Setup Celery logger
celery = InvenioCelery(current_app)

logger = get_task_logger(__name__)


@celery.celery.task(ignore_result=True, max_retries=6,
                    default_retry_delay=10 * 60, rate_limit="100/m")
def datacite_sync(recid):
    """Check DOI in DataCite."""
    record = get_record(recid)

    if record is None:
        logger.debug("Record %s not found" % recid)
        return

    doi_val = record.get(cfg['PIDSTORE_DATACITE_RECORD_DOI_FIELD'], None)
    logger.debug("Found DOI %s in record %s" % (doi_val, recid))

    pid = PersistentIdentifier.get("doi", doi_val)
    if not pid:
        logger.debug("DOI not locally managed.")
        return
    else:
        logger.debug("DOI locally managed.")

    if pid.sync_status():
        logger.info("Successfully synchronized DOI %s." % doi_val)


@celery.celery.task(ignore_result=True, max_retries=6,
                    default_retry_delay=10 * 60, rate_limit="100/m")
def datacite_update(recid):
    """Update DOI in DataCite.

    If it fails, it will retry every 10 minutes for 1 hour.
    """
    record = get_record(recid)

    if record is None:
        logger.debug("Record %s not found" % recid)
        return

    doi_val = record.get(cfg['PIDSTORE_DATACITE_RECORD_DOI_FIELD'], None)
    logger.debug("Found DOI %s in record %s" % (doi_val, recid))

    pid = PersistentIdentifier.get("doi", doi_val)
    if not pid:
        logger.debug("DOI not locally managed.")
        return
    else:
        logger.debug("DOI locally managed.")

    if not pid.has_object("rec", recid):
        raise Exception(
            "DOI %s is not assigned to record %s." % (doi_val, recid))

    if pid.is_registered() or pid.is_deleted():
        logger.info("Updating DOI %s for record %s" % (doi_val, recid))

        url = "%s/record/%s" % (cfg['PIDSTORE_DATACITE_SITE_URL'], recid)
        doc = format_record(record, cfg['PIDSTORE_DATACITE_OUTPUTFORMAT'])

        if not pid.update(url=url, doc=doc):
            m = "Failed to update DOI %s" % doi_val
            logger.error(m + "\n%s\n%s" % (url, doc))
            if not datacite_update.request.is_eager:
                raise datacite_update.retry(exc=Exception(m))
        else:
            logger.info("Successfully updated DOI %s." % doi_val)


@celery.celery.task(ignore_result=True)
def datacite_update_all(recids=None):
    """Update many DOIs in DataCite.

    :param recids: List of record ids to update. Defaults to all
        registered DOIs.
    """
    pid_query = PersistentIdentifier.query.filter_by(
        object_type='rec', pid_type='doi',
        status=cfg['PIDSTORE_STATUS_REGISTERED']
    )

    if recids is not None:
        pid_query = pid_query.filter(
            PersistentIdentifier.object_value.in_(
                map(lambda x: unicode(x), recids)
            )
        )

    for pid in pid_query.all():
        datacite_update.delay(pid.object_value)


@celery.celery.task(ignore_result=True, max_retries=6,
                    default_retry_delay=10 * 60, rate_limit="100/m")
def datacite_delete(recid):
    """Delete DOI in DataCite.

    If it fails, it will retry every 10 minutes for 1 hour.
    """
    record = get_record(recid)

    if record is None:
        logger.debug("Record %s not found" % recid)
        return

    doi_val = record.get(cfg['PIDSTORE_DATACITE_RECORD_DOI_FIELD'], None)
    logger.debug("Found DOI %s in record %s" % (doi_val, recid))

    pid = PersistentIdentifier.get("doi", doi_val)
    if not pid:
        logger.debug("DOI not locally managed.")
        return
    else:
        logger.debug("DOI locally managed.")

    if not pid.has_object("rec", recid):
        raise Exception(
            "DOI %s is not assigned to record %s." % (doi_val, recid))

    if pid.is_registered():
        logger.info("Inactivating DOI %s for record %s" % (doi_val, recid))

        if not pid.delete():
            m = "Failed to inactive DOI %s" % doi_val
            logger.error(m)
            if not datacite_delete.request.is_eager:
                raise datacite_delete.retry(exc=Exception(m))
        else:
            logger.info("Successfully inactivated DOI %s." % doi_val)


@celery.celery.task(ignore_result=True, max_retries=6,
                    default_retry_delay=10 * 60, rate_limit="100/m")
def datacite_register(recid):
    """Register a DOI for new publication.

    If it fails, it will retry every 10 minutes for 1 hour.
    """
    record = get_record(recid)

    if record is None:
        logger.debug("Record %s not found" % recid)
        return

    doi_val = record.get(cfg['PIDSTORE_DATACITE_RECORD_DOI_FIELD'], None)
    logger.debug("Found DOI %s in record %s" % (doi_val, recid))

    pid = PersistentIdentifier.get("doi", doi_val)
    if not pid:
        logger.debug("DOI not locally managed.")
        return
    else:
        logger.debug("DOI locally managed.")

    if not pid.has_object("rec", recid):
        raise Exception(
            "DOI %s is not assigned to record %s." % (doi_val, recid))

    if pid.is_new() or pid.is_reserved():
        logger.info("Registering DOI %s for record %s" % (doi_val, recid))

        url = "%s/record/%s" % (
            cfg.get('PIDSTORE_DATACITE_SITE_URL', cfg['CFG_SITE_URL']),
            recid
        )
        doc = format_record(record, cfg['PIDSTORE_DATACITE_OUTPUTFORMAT'])

        if not pid.register(url=url, doc=doc):
            m = "Failed to register DOI %s" % doi_val
            logger.error(m + "\n%s\n%s" % (url, doc))
            if not datacite_register.request.is_eager:
                raise datacite_register.retry(exc=Exception(m))
        else:
            logger.info("Successfully registered DOI %s." % doi_val)
