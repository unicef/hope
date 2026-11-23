from typing import Any

from django.core.management import CommandError, call_command
from django.db import connection
from django.db.migrations.recorder import MigrationRecorder
import pytest


@pytest.fixture
def stray_core_row(db: Any, settings: Any) -> int:
    """Migrations visible on disk again, plus one core row that no code on disk knows about."""
    settings.MIGRATION_MODULES = {}
    recorder = MigrationRecorder(connection)
    recorder.record_applied("core", "9999_migration")
    return recorder.migration_qs.count()


@pytest.fixture
def partly_applied_core_chain(db: Any, settings: Any) -> int:
    """Migrations visible on disk again, with a single migration of the replaced core chain applied."""
    settings.MIGRATION_MODULES = {}
    recorder = MigrationRecorder(connection)
    recorder.record_applied("core", "0001_migration")
    return recorder.migration_qs.count()


@pytest.fixture
def stray_core_row_with_hidden_migrations(db: Any) -> None:
    """The same stray core row while the migration modules stay hidden, the way --no-migrations hides them."""
    MigrationRecorder(connection).record_applied("core", "9999_migration")


def test_migrate_skips_the_guard_for_apps_without_visible_migrations(
    stray_core_row_with_hidden_migrations: None,
) -> None:
    # Raises CommandError as soon as the guard looks at an app whose migration modules it cannot see.
    call_command("migrate", check_unapplied=True)


def test_migrate_refuses_database_ahead_of_code_before_recording_anything(
    stray_core_row: int, django_assert_num_queries: Any
) -> None:
    # Two reads of django_migrations (does the table exist, which rows are applied) and nothing else.
    with django_assert_num_queries(2), pytest.raises(CommandError, match=r"core\.9999_migration"):
        call_command("migrate")

    assert MigrationRecorder(connection).migration_qs.count() == stray_core_row


def test_migrate_refuses_partly_applied_old_chain_before_recording_anything(
    partly_applied_core_chain: int, django_assert_num_queries: Any
) -> None:
    with django_assert_num_queries(2), pytest.raises(CommandError, match=r"core\.0002_migration"):
        call_command("migrate")

    assert MigrationRecorder(connection).migration_qs.count() == partly_applied_core_chain
