from typing import Any

from django.apps import apps
from django.db.migrations.loader import MigrationLoader
import pytest


@pytest.fixture
def names_on_disk_and_replaced(settings: Any) -> tuple[set[tuple[str, str]], list[tuple[str, str]]]:
    """First-party migrations read from disk; the suite itself runs with migrations disabled."""
    settings.MIGRATION_MODULES = {}
    loader = MigrationLoader(None, load=False)
    loader.load_disk()
    first_party = {cfg.label for cfg in apps.get_app_configs() if cfg.name == "hope" or cfg.name.startswith("hope.")}
    on_disk = {key: migration for key, migration in loader.disk_migrations.items() if key[0] in first_party}
    replaced = [replaced_key for migration in on_disk.values() for replaced_key in migration.replaces]
    return set(on_disk), replaced


def test_no_migration_on_disk_has_a_name_replaced_by_the_baseline(
    names_on_disk_and_replaced: tuple[set[tuple[str, str]], list[tuple[str, str]]],
) -> None:
    # Such a migration is recorded as applied on every existing database and would never run.
    on_disk, replaced = names_on_disk_and_replaced

    assert on_disk
    assert on_disk & set(replaced) == set()


def test_no_old_migration_is_replaced_by_two_baseline_files(
    names_on_disk_and_replaced: tuple[set[tuple[str, str]], list[tuple[str, str]]],
) -> None:
    _, replaced = names_on_disk_and_replaced

    assert len(replaced) == len(set(replaced))
