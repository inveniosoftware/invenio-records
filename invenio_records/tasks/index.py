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

from invenio_celery import celery
from invenio_ext.es import es


@celery.task
def index_record(recid, json):
    """Index a record in elasticsearch."""
    es.index(
        index='records',
        doc_type='record',
        body=json,
        id=recid
    )


@celery.task
def index_collection_percolator(name, dbquery):
    """Create an elasticsearch percolator for a given query."""
    from invenio_search.api import Query
    from invenio_search.walkers.elasticsearch import ElasticSearchDSL
    es.index(
        index='records',
        doc_type='.percolator',
        body={'query': Query(dbquery).query.accept(ElasticSearchDSL())},
        id=name
    )
