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

"""Define authorization actions and checks."""

import warnings

from collections import MutableMapping

from invenio.base.globals import cfg

try:
    from invenio_collections.cache import get_restricted_collections
except ImportError:  # pragma: no cover
    # remove when invenio-collections>=0.1.3
    from invenio_collections.cache import restricted_collection_cache

    def get_restricted_collections():
        return restricted_collection_cache.cache

from .api import get_record


def check_email_or_group(user_info, email_or_group):
    """Check user email or group matches."""
    if email_or_group in user_info['group']:
        return True
    email = email_or_group.strip().lower()
    if user_info['email'].strip().lower() == email:
        return True


def check_uid(user_info, uid):
    """Check user id matches."""
    return unicode(user_info['id']) == uid


def check_authorized_tags(record, tags, test_func):
    """Check if tags in record matches a given test."""
    authorized_values = []
    for tag in tags:
        if tag in record:
            authorized_values.extend(record.get(tag))

    for value in authorized_values:
        if test_func(value):
            return True
    return False


def is_user_in_tags(record, user_info, user_id_tags, email_or_group_tags):
    """Check if user id or email is found in a records tags."""
    if check_authorized_tags(record, user_id_tags,
                             lambda uid: check_uid(user_info, uid)):
        return True

    return check_authorized_tags(
        record, email_or_group_tags,
        lambda val: check_email_or_group(user_info, val)
    )


def is_user_owner_of_record(user_info, recid):
    """Check if the user is owner of the record.

    I.e. he is the submitter and/or belongs to a owner-like group authorized
    to 'see' the record.

    :param user_info: the user_info dictionary that describe the user.
    :type user_info: user_info dictionary
    :param recid: the record identifier.
    :type recid: positive integer
    :return: True if the user is 'owner' of the record; False otherwise
    """
    from invenio_access.local_config import \
        CFG_ACC_GRANT_AUTHOR_RIGHTS_TO_EMAILS_IN_TAGS, \
        CFG_ACC_GRANT_AUTHOR_RIGHTS_TO_USERIDS_IN_TAGS

    if not isinstance(recid, MutableMapping):
        record = get_record(int(recid))
    else:
        record = recid

    uid_tags = cfg.get('CFG_ACC_GRANT_AUTHOR_RIGHTS_TO_USERIDS_IN_TAGS',
                       CFG_ACC_GRANT_AUTHOR_RIGHTS_TO_EMAILS_IN_TAGS)

    email_tags = cfg.get('CFG_ACC_GRANT_AUTHOR_RIGHTS_TO_USERIDS_IN_TAGS',
                         CFG_ACC_GRANT_AUTHOR_RIGHTS_TO_USERIDS_IN_TAGS)

    return is_user_in_tags(record, user_info, uid_tags, email_tags)


# FIXME: This method needs to be refactored
def is_user_viewer_of_record(user_info, recid):
    """Check if the user is allow to view the record based in the marc tags.

    Checks inside CFG_ACC_GRANT_VIEWER_RIGHTS_TO_EMAILS_IN_TAGS
    i.e. his email is inside the 506__m tag or he is inside an e-group listed
    in the 506__m tag

    :param user_info: the user_info dictionary that describe the user.
    :type user_info: user_info dictionary
    :param recid: the record identifier.
    :type recid: positive integer
    @return: True if the user is 'allow to view' the record; False otherwise
    @rtype: bool
    """
    from invenio_access.local_config import \
        CFG_ACC_GRANT_VIEWER_RIGHTS_TO_EMAILS_IN_TAGS, \
        CFG_ACC_GRANT_VIEWER_RIGHTS_TO_USERIDS_IN_TAGS

    if not isinstance(recid, MutableMapping):
        record = get_record(int(recid))
    else:
        record = recid

    uid_tags = cfg.get('CFG_ACC_GRANT_VIEWER_RIGHTS_TO_USERIDS_IN_TAGS',
                       CFG_ACC_GRANT_VIEWER_RIGHTS_TO_USERIDS_IN_TAGS)

    email_tags = cfg.get('CFG_ACC_GRANT_VIEWER_RIGHTS_TO_EMAILS_IN_TAGS',
                         CFG_ACC_GRANT_VIEWER_RIGHTS_TO_EMAILS_IN_TAGS)

    return is_user_in_tags(record, user_info, uid_tags, email_tags)


def get_restricted_collections_for_record(record):
    """Return the list of restricted collections to which record belongs."""

    return set(record.get('_collections', [])) & set(
        get_restricted_collections()
    )


def is_record_public(record):
    """Return True if the record is public.

    It means that it can be found in the Home collection.
    """
    return cfg['CFG_SITE_NAME'] in record.get('_collections', [])


def check_user_can_view_record(user_info, recid):
    """Check if the user is authorized to view the given recid.

    The function grants access in two cases: either user has author rights on
    this record, or he has view rights to the primary collection this record
    belongs to.

    :param user_info: the user_info dictionary that describe the user.
    :type user_info: user_info dictionary
    :param recid: the record identifier.
    :type recid: positive integer
    :return: (0, ''), when authorization is granted, (>0, 'message') when
    authorization is not granted
    """
    from invenio_access.engine import acc_authorize_action
    from invenio_access.local_config import VIEWRESTRCOLL

    policy = cfg['CFG_WEBSEARCH_VIEWRESTRCOLL_POLICY'].strip().upper()

    if not isinstance(recid, MutableMapping):
        record = get_record(int(recid))
    else:
        record = recid
    # At this point, either webcoll has not yet run or there are some
    # restricted collections. Let's see first if the user own the record.
    if is_user_owner_of_record(user_info, record):
        # Perfect! It's authorized then!
        return (0, '')

    if is_user_viewer_of_record(user_info, record):
        # Perfect! It's authorized then!
        return (0, '')

    restricted_collections = get_restricted_collections_for_record(
        record, recreate_cache_if_needed=False
    )
    if not restricted_collections and is_record_public(record):
        # The record is public and not part of any restricted collection
        return (0, '')
    if restricted_collections:
        # If there are restricted collections the user must be authorized to
        # all/any of them (depending on the policy)
        permitted_restricted_collections = set(user_info.get(
            'precached_permitted_restricted_collections', []
        ))

        if policy != 'ANY':
            not_authorized_collections = (
                restricted_collections - permitted_restricted_collections
            )
            if not_authorized_collections:
                # The user is not authorized to all restricted collections.
                return (1, not_authorized_collections)
        else:
            if not restricted_collections & permitted_restricted_collections:
                # None of restricted collections is authorized.
                return (1, restricted_collections)
        return (0, '')

    # FIXME is record in any collection
    if bool(record.get('_collections', [])):
        # the record is not in any restricted collection
        return (0, '')
    elif record is not None:
        # We are in the case where webcoll has not run.
        # Let's authorize SUPERADMIN
        (auth_code, auth_msg) = acc_authorize_action(
            user_info, VIEWRESTRCOLL, collection=None
        )
        if auth_code == 0:
            return (0, '')
        else:
            # Too bad. Let's print a nice message:
            return (
                1,
                "The record you are trying to access has just been "
                "submitted to the system and needs to be assigned to the "
                "proper collections. It is currently restricted for security "
                "reasons until the assignment will be fully completed. Please "
                "come back later to properly access this record.")
    else:
        # The record either does not exists or has been deleted.
        # Let's handle these situations outside of this code.
        return (0, '')
