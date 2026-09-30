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


def test_forwards_renames_btree_found_by_column_despite_drifted_name(
    project_state: ProjectState, drifted_created_at_index: int, index_oid
) -> None:
    operation = RenameDbIndex(model_name="hope", column="created_at", new_name="migration_created_idx")

    with connection.schema_editor() as editor:
        operation.database_forwards("migration_operations", editor, project_state, project_state)

    assert index_oid("migration_created_idx") == drifted_created_at_index
    assert index_oid("legacy_hope_created_at_1a2b3c4d") is None
