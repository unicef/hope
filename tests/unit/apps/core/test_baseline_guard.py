from django.db.migrations import Migration
import pytest

from hope.apps.core.baseline_guard import baseline_violations

ACCOUNT_OLD = [("account", "0001_migration"), ("account", "0002_migration"), ("account", "0003_migration")]
CORE_OLD = [("core", "0001_migration"), ("core", "0002_migration")]
ALL_OLD = ACCOUNT_OLD + CORE_OLD
BASELINE = [
    ("account", "0004_baseline_models"),
    ("account", "0005_baseline_relations"),
    ("core", "0003_baseline_models"),
]
LABELS = {"account", "core", "utils"}


@pytest.fixture
def disk_migrations() -> dict[tuple[str, str], Migration]:
    """Two apps with baseline files and disjoint ``replaces``; ``utils`` has no migrations at all."""

    def migration(app_label: str, name: str, replaces: list[str]) -> Migration:
        instance = Migration(name, app_label)
        instance.replaces = [(app_label, replaced) for replaced in replaces]
        return instance

    migrations = [
        migration("account", "0004_baseline_models", ["0002_migration", "0003_migration"]),
        migration("account", "0005_baseline_relations", ["0001_migration"]),
        migration("account", "0006_migration", []),
        migration("core", "0003_baseline_models", ["0001_migration", "0002_migration"]),
        migration("geo", "0002_baseline_models", ["0001_migration"]),
    ]
    return {(instance.app_label, instance.name): instance for instance in migrations}


@pytest.mark.parametrize(
    "applied",
    [
        pytest.param([], id="empty database"),
        pytest.param(ALL_OLD, id="whole old chain"),
        pytest.param(ALL_OLD + BASELINE, id="whole old chain and baseline rows"),
        pytest.param(BASELINE, id="baseline rows only, old rows pruned"),
        pytest.param(ALL_OLD + BASELINE + [("account", "0006_migration")], id="migration added after the baseline"),
        pytest.param(ALL_OLD + [("core", "0023_migration")], id="tolerated stray row"),
        pytest.param(ALL_OLD + [("reporting", "0001_migration")], id="row of a removed app"),
        pytest.param(ALL_OLD + [("geo", "0099_migration")], id="stray row of a label that is not checked"),
        pytest.param(ACCOUNT_OLD, id="one app migrated, the other not started"),
    ],
)
def test_baseline_violations_returns_nothing_for_consistent_database(
    disk_migrations: dict[tuple[str, str], Migration], applied: list[tuple[str, str]]
) -> None:
    assert baseline_violations(disk_migrations, applied, LABELS) == []


@pytest.mark.parametrize(
    ("applied", "named", "not_named"),
    [
        pytest.param(
            [("account", "0001_migration"), ("account", "0003_migration")] + CORE_OLD,
            "account.0002_migration",
            "account.0001_migration",
            id="one old migration missing",
        ),
        pytest.param(
            [("account", "0002_migration"), ("account", "0003_migration")],
            "account.0001_migration",
            "account.0002_migration",
            id="only the first baseline file's list applied",
        ),
        pytest.param(
            ALL_OLD + [("account", "0099_migration")],
            "account.0099_migration",
            "account.0001_migration",
            id="stray first-party row",
        ),
        pytest.param(
            ALL_OLD + [("core", "0023_migration_x")],
            "core.0023_migration_x",
            "core.0001_migration",
            id="near miss of the tolerated name",
        ),
        pytest.param(
            ALL_OLD + [("account", "0023_migration")],
            "account.0023_migration",
            "core.0001_migration",
            id="tolerated name in another app",
        ),
        pytest.param(
            ALL_OLD + [("utils", "0001_migration")],
            "utils.0001_migration",
            "account.0001_migration",
            id="row of a checked label without migrations on disk",
        ),
    ],
)
def test_baseline_violations_names_offending_migrations(
    disk_migrations: dict[tuple[str, str], Migration],
    applied: list[tuple[str, str]],
    named: str,
    not_named: str,
) -> None:
    violations = baseline_violations(disk_migrations, applied, LABELS)

    assert len(violations) == 1
    assert named in violations[0]
    assert not_named not in violations[0]


def test_baseline_violations_reports_every_app(disk_migrations: dict[tuple[str, str], Migration]) -> None:
    applied = [("account", "0001_migration"), ("core", "0001_migration"), ("core", "0099_migration")]

    violations = baseline_violations(disk_migrations, applied, LABELS)

    assert len(violations) == 3
