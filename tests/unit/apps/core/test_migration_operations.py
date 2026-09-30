from django.db import connection, models
from django.db.migrations.state import ModelState, ProjectState
import pytest

from hope.apps.core.migration_operations import RenameDbIndex

pytestmark = pytest.mark.django_db


@pytest.fixture
def project_state() -> ProjectState:
    state = ProjectState()
    state.add_model(
        ModelState(
            "migration_operations",
            "Hope",
            [
                ("id", models.AutoField(primary_key=True)),
                ("created_at", models.DateTimeField()),
                ("name", models.CharField(max_length=100)),
            ],
        )
    )
    return state


@pytest.fixture
def hope_table(project_state: ProjectState) -> None:
    with connection.schema_editor() as editor:
        editor.create_model(project_state.apps.get_model("migration_operations", "Hope"))


@pytest.fixture
def index_oid():
    def _index_oid(name: str) -> int | None:
        with connection.cursor() as cursor:
            cursor.execute("SELECT to_regclass(%s)::oid", [connection.ops.quote_name(name)])
            return cursor.fetchone()[0]

    return _index_oid


@pytest.fixture
def drifted_created_at_index(hope_table: None, index_oid) -> int:
    """A ``db_index`` btree whose name predates a model rename, so it matches no name Django computes today."""
    with connection.cursor() as cursor:
        cursor.execute('CREATE INDEX "legacy_hope_created_at_1a2b3c4d" ON "migration_operations_hope" ("created_at")')
    return index_oid("legacy_hope_created_at_1a2b3c4d")


@pytest.fixture
def drifted_name_index(hope_table: None, index_oid) -> int:
    with connection.cursor() as cursor:
        cursor.execute('CREATE INDEX "legacy_hope_name_5e6f7a8b" ON "migration_operations_hope" ("name")')
    return index_oid("legacy_hope_name_5e6f7a8b")


@pytest.fixture
def drifted_name_like_index(hope_table: None, index_oid) -> int:
    """The ``varchar_pattern_ops`` twin that ``db_index=True`` adds next to the btree of a char column."""
    with connection.cursor() as cursor:
        cursor.execute(
            'CREATE INDEX "legacy_hope_name_5e6f7a8b_like" ON "migration_operations_hope" ("name" varchar_pattern_ops)'
        )
    return index_oid("legacy_hope_name_5e6f7a8b_like")


def test_forwards_renames_btree_found_by_column_despite_drifted_name(
    project_state: ProjectState, drifted_created_at_index: int, index_oid
) -> None:
    operation = RenameDbIndex(model_name="hope", column="created_at", new_name="migration_created_idx")

    with connection.schema_editor() as editor:
        operation.database_forwards("migration_operations", editor, project_state, project_state)

    assert index_oid("migration_created_idx") == drifted_created_at_index
    assert index_oid("legacy_hope_created_at_1a2b3c4d") is None


def test_forwards_with_like_suffix_renames_like_twin_and_keeps_btree(
    project_state: ProjectState, drifted_name_index: int, drifted_name_like_index: int, index_oid
) -> None:
    operation = RenameDbIndex(model_name="hope", column="name", new_name="migration_name_lk", suffix="_like")

    with connection.schema_editor() as editor:
        operation.database_forwards("migration_operations", editor, project_state, project_state)

    assert index_oid("migration_name_lk") == drifted_name_like_index
    assert index_oid("legacy_hope_name_5e6f7a8b") == drifted_name_index


def test_forwards_renames_btree_and_keeps_its_like_twin(
    project_state: ProjectState, drifted_name_index: int, drifted_name_like_index: int, index_oid
) -> None:
    operation = RenameDbIndex(model_name="hope", column="name", new_name="migration_name_idx")

    with connection.schema_editor() as editor:
        operation.database_forwards("migration_operations", editor, project_state, project_state)

    assert index_oid("migration_name_idx") == drifted_name_index
    assert index_oid("legacy_hope_name_5e6f7a8b_like") == drifted_name_like_index


def test_forwards_with_like_suffix_is_noop_when_twin_is_missing(
    project_state: ProjectState, drifted_name_index: int, index_oid
) -> None:
    operation = RenameDbIndex(model_name="hope", column="name", new_name="migration_name_lk", suffix="_like")

    with connection.schema_editor() as editor:
        operation.database_forwards("migration_operations", editor, project_state, project_state)

    assert index_oid("migration_name_lk") is None
    assert index_oid("legacy_hope_name_5e6f7a8b") == drifted_name_index


def test_forwards_raises_when_column_has_no_btree(project_state: ProjectState, hope_table: None) -> None:
    operation = RenameDbIndex(model_name="hope", column="created_at", new_name="migration_created_idx")

    with (
        connection.schema_editor() as editor,
        pytest.raises(ValueError, match=r"Found no btree index on migration_operations_hope\(created_at\)"),
    ):
        operation.database_forwards("migration_operations", editor, project_state, project_state)


def test_init_rejects_unknown_suffix() -> None:
    with pytest.raises(ValueError, match=r"suffix must be '' or '_like', got '_lk'"):
        RenameDbIndex(model_name="hope", column="name", new_name="migration_name_lk", suffix="_lk")
