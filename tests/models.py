# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2025 Graz University of Technology.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Mock models."""

from invenio_db import db
from sqlalchemy.dialects import mysql
from sqlalchemy_utils.types import UUIDType

from invenio_records.models import RecordMetadataBase


class CustomMetadata(db.Model, RecordMetadataBase):
    """Custom Metadata."""

    __tablename__ = "custom_metadata"


class TypeModel(db.Model, RecordMetadataBase):
    """Type model."""

    string = db.Column(db.String(255))
    text = db.Column(db.Text)
    biginteger = db.Column(db.BigInteger)
    integer = db.Column(db.Integer)
    boolean = db.Column(db.Boolean(name="boolean"))
    text_variant = db.Column(db.Text().with_variant(mysql.VARCHAR(255), "mysql"))


class Record1Metadata(db.Model, RecordMetadataBase):
    """Record 1 metadata."""

    __tablename__ = "record1_metadata"
    expires_at = db.Column(db.UTCDateTime())


class Record3Metadata(db.Model, RecordMetadataBase):
    """Record 3 metadata."""

    __tablename__ = "record3_metadata"


class Record2Metadata(db.Model, RecordMetadataBase):
    """Record 2 metadata."""

    __tablename__ = "record2_metadata"

    record3_id = db.Column(UUIDType, db.ForeignKey(Record3Metadata.id))
