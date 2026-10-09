# SPDX-FileCopyrightText: 2026 Mudassir Uddin.
# SPDX-License-Identifier: MIT

"""Test that the migrations work if the versioning tables do not exist.

With ``DB_VERSIONING = False`` the database has no ``records_metadata_version`` table.
"""

import importlib.util
from pathlib import Path
from unittest import mock

import pytest
import sqlalchemy as sa

import invenio_records

ALEMBIC_DIR = Path(invenio_records.__file__).parent / "alembic"
JSONB_MIGRATION = "428b919be0ea_alter_column_from_json_to_jsonb_for_version"
DATETIME_MIGRATION = "66db9c49c699_change_datetime_types"


def _load_migration(name):
    spec = importlib.util.spec_from_file_location(name, ALEMBIC_DIR / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def make_connection():
    """Create a connection to a database with the given tables."""
    engines = []

    def _make(*table_names):
        engine = sa.create_engine("sqlite://")
        engines.append(engine)
        metadata = sa.MetaData()
        for table_name in table_names:
            sa.Table(
                table_name, metadata, sa.Column("id", sa.Integer, primary_key=True)
            )
        metadata.create_all(engine)
        return engine.connect()

    yield _make
    for engine in engines:
        engine.dispose()


def _mock_op(connection, dialect="postgresql"):
    op = mock.MagicMock()
    op.get_bind.return_value = connection
    op._proxy.migration_context.dialect.name = dialect
    return op


@pytest.mark.parametrize("direction", ["upgrade", "downgrade"])
def test_jsonb_migration_of_versioning_table(make_connection, direction):
    """The json column of the versioning table is only altered if the table exists."""
    migration = _load_migration(JSONB_MIGRATION)

    # with versioning
    op = _mock_op(make_connection("records_metadata", "records_metadata_version"))
    with mock.patch.object(migration, "op", op):
        getattr(migration, direction)()
    assert [call.args[0] for call in op.alter_column.call_args_list] == [
        "records_metadata_version"
    ]

    # without versioning
    op = _mock_op(make_connection("records_metadata"))
    with mock.patch.object(migration, "op", op):
        getattr(migration, direction)()
    op.alter_column.assert_not_called()

    # other databases than PostgreSQL are not touched in any case
    op = _mock_op(
        make_connection("records_metadata", "records_metadata_version"),
        dialect="sqlite",
    )
    with mock.patch.object(migration, "op", op):
        getattr(migration, direction)()
    op.alter_column.assert_not_called()


@pytest.mark.parametrize(
    "direction,helper",
    [
        ("upgrade", "update_table_columns_column_type_to_utc_datetime"),
        ("downgrade", "update_table_columns_column_type_to_datetime"),
    ],
)
def test_datetime_migration_of_versioning_table(make_connection, direction, helper):
    """The datetime columns of the versioning table are only changed if the table exists."""
    migration = _load_migration(DATETIME_MIGRATION)

    # with versioning
    with mock.patch.object(
        migration,
        "op",
        _mock_op(make_connection("records_metadata", "records_metadata_version")),
    ):
        with mock.patch.object(migration, helper) as update:
            getattr(migration, direction)()
    assert [call.args for call in update.call_args_list] == [
        ("records_metadata", "created"),
        ("records_metadata", "updated"),
        ("records_metadata_version", "created"),
        ("records_metadata_version", "updated"),
    ]

    # without versioning
    with mock.patch.object(
        migration, "op", _mock_op(make_connection("records_metadata"))
    ):
        with mock.patch.object(migration, helper) as update:
            getattr(migration, direction)()
    assert [call.args for call in update.call_args_list] == [
        ("records_metadata", "created"),
        ("records_metadata", "updated"),
    ]
