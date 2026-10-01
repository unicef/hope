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
def unusable_drifted_name_index(request: pytest.FixtureRequest, drifted_name_index: int) -> None:
    """The drifted btree left behind by a failed ``CREATE INDEX CONCURRENTLY``, with the given flag cleared."""
    with connection.cursor() as cursor:
        cursor.execute(f"UPDATE pg_index SET {request.param} = false WHERE indexrelid = %s", [drifted_name_index])


@pytest.fixture
def drifted_name_like_index(hope_table: None, index_oid) -> int:
    """The ``varchar_pattern_ops`` twin that ``db_index=True`` adds next to the btree of a char column."""
    with connection.cursor() as cursor:
        cursor.execute(
            'CREATE INDEX "legacy_hope_name_5e6f7a8b_like" ON "migration_operations_hope" ("name" varchar_pattern_ops)'
        )
    return index_oid("legacy_hope_name_5e6f7a8b_like")


@pytest.fixture
def target_created_at_index(hope_table: None, index_oid) -> int:
    """A btree that already has the target name, as after a previous run of the migration."""
    with connection.cursor() as cursor:
        cursor.execute('CREATE INDEX "migration_created_idx" ON "migration_operations_hope" ("created_at")')
    return index_oid("migration_created_idx")


@pytest.fixture
def target_name_index(request: pytest.FixtureRequest, hope_table: None) -> None:
    """Statements that leave an index named ``migration_name_idx`` behind, with the definition under test."""
    with connection.cursor() as cursor:
        for statement in request.param:
            cursor.execute(statement)


@pytest.fixture
def other_name_index(request: pytest.FixtureRequest, hope_table: None, index_oid) -> int:
    """An index on ``name`` that ``db_index=True`` cannot have created, e.g. added by hand on a long-lived database."""
    with connection.cursor() as cursor:
        cursor.execute(request.param)
    return index_oid("other_name_idx")


def test_forwards_renames_btree_found_by_column_despite_drifted_name(
    project_state: ProjectState, drifted_created_at_index: int, index_oid
) -> None:
    operation = RenameDbIndex(model_name="hope", column="created_at", new_name="migration_created_idx")

    with connection.schema_editor() as editor:
        operation.database_forwards("migration_operations", editor, project_state, project_state)

    assert index_oid("migration_created_idx") == drifted_created_at_index
    assert index_oid("legacy_hope_created_at_1a2b3c4d") is None


def test_forwards_is_noop_when_target_name_exists_with_expected_definition(
    project_state: ProjectState, target_created_at_index: int, drifted_created_at_index: int, index_oid
) -> None:
    operation = RenameDbIndex(model_name="hope", column="created_at", new_name="migration_created_idx")

    with connection.schema_editor() as editor:
        operation.database_forwards("migration_operations", editor, project_state, project_state)

    assert index_oid("migration_created_idx") == target_created_at_index
    assert index_oid("legacy_hope_created_at_1a2b3c4d") == drifted_created_at_index


@pytest.mark.parametrize(
    "target_name_index",
    [
        pytest.param(
            [
                'CREATE TABLE "migration_operations_other" ("name" varchar(100))',
                'CREATE INDEX "migration_name_idx" ON "migration_operations_other" ("name")',
            ],
            id="other-table",
        ),
        pytest.param(
            ['CREATE INDEX "migration_name_idx" ON "migration_operations_hope" ("created_at")'], id="other-column"
        ),
        pytest.param(
            ['CREATE INDEX "migration_name_idx" ON "migration_operations_hope" ("name", "created_at")'],
            id="multi-column",
        ),
        pytest.param(
            ['CREATE INDEX "migration_name_idx" ON "migration_operations_hope" (lower("name"))'], id="expression"
        ),
        pytest.param(
            ['CREATE INDEX "migration_name_idx" ON "migration_operations_hope" USING hash ("name")'], id="hash"
        ),
        pytest.param(
            ['CREATE INDEX "migration_name_idx" ON "migration_operations_hope" ("name" varchar_pattern_ops)'],
            id="pattern-opclass",
        ),
        pytest.param(
            ['CREATE INDEX "migration_name_idx" ON "migration_operations_hope" ("name" COLLATE "C")'], id="collation"
        ),
        pytest.param(['CREATE INDEX "migration_name_idx" ON "migration_operations_hope" ("name" DESC)'], id="desc"),
        pytest.param(
            ['CREATE INDEX "migration_name_idx" ON "migration_operations_hope" ("name" NULLS FIRST)'], id="nulls-first"
        ),
        pytest.param(
            ['CREATE INDEX "migration_name_idx" ON "migration_operations_hope" ("name") INCLUDE ("created_at")'],
            id="include",
        ),
        pytest.param(
            [
                (
                    'CREATE INDEX "migration_name_idx" ON "migration_operations_hope" ("name") '
                    'WHERE "created_at" IS NOT NULL'
                )
            ],
            id="partial",
        ),
        pytest.param(['CREATE UNIQUE INDEX "migration_name_idx" ON "migration_operations_hope" ("name")'], id="unique"),
        pytest.param(
            [
                'CREATE INDEX "migration_name_idx" ON "migration_operations_hope" ("name")',
                "UPDATE pg_index SET indisvalid = false WHERE indexrelid = 'migration_name_idx'::regclass",
            ],
            id="invalid",
        ),
        pytest.param(
            [
                'CREATE INDEX "migration_name_idx" ON "migration_operations_hope" ("name")',
                "UPDATE pg_index SET indisready = false WHERE indexrelid = 'migration_name_idx'::regclass",
            ],
            id="not-ready",
        ),
    ],
    indirect=True,
)
def test_forwards_raises_when_target_name_exists_with_other_definition(
    project_state: ProjectState, target_name_index: None
) -> None:
    operation = RenameDbIndex(model_name="hope", column="name", new_name="migration_name_idx")

    with (
        connection.schema_editor() as editor,
        pytest.raises(
            ValueError,
            match=(
                r"Index migration_name_idx already exists but is not the btree index on "
                r"migration_operations_hope\(name\)"
            ),
        ),
    ):
        operation.database_forwards("migration_operations", editor, project_state, project_state)


@pytest.mark.parametrize(
    "target_name_index",
    [
        pytest.param(
            ['CREATE INDEX "migration_name_idx" ON "migration_operations_hope" ("name" varchar_pattern_ops)'],
            id="varchar-pattern-opclass",
        ),
    ],
    indirect=True,
)
def test_forwards_with_like_suffix_is_noop_when_target_name_exists_with_expected_definition(
    project_state: ProjectState, target_name_index: None, drifted_name_like_index: int, index_oid
) -> None:
    target_oid = index_oid("migration_name_idx")
    operation = RenameDbIndex(model_name="hope", column="name", new_name="migration_name_idx", suffix="_like")

    with connection.schema_editor() as editor:
        operation.database_forwards("migration_operations", editor, project_state, project_state)

    assert index_oid("migration_name_idx") == target_oid
    assert index_oid("legacy_hope_name_5e6f7a8b_like") == drifted_name_like_index


@pytest.mark.parametrize(
    "target_name_index",
    [
        pytest.param(
            ['CREATE INDEX "migration_name_idx" ON "migration_operations_hope" ("name")'], id="default-opclass"
        ),
        pytest.param(
            ['CREATE INDEX "migration_name_idx" ON "migration_operations_hope" ("name" text_pattern_ops)'],
            id="text-pattern-opclass",
        ),
    ],
    indirect=True,
)
def test_forwards_with_like_suffix_raises_when_target_name_exists_with_other_opclass(
    project_state: ProjectState, target_name_index: None
) -> None:
    operation = RenameDbIndex(model_name="hope", column="name", new_name="migration_name_idx", suffix="_like")

    with (
        connection.schema_editor() as editor,
        pytest.raises(
            ValueError,
            match=(
                r"Index migration_name_idx already exists but is not the varchar_pattern_ops btree index on "
                r"migration_operations_hope\(name\)"
            ),
        ),
    ):
        operation.database_forwards("migration_operations", editor, project_state, project_state)


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


@pytest.mark.parametrize(
    "other_name_index",
    [
        pytest.param(
            'CREATE INDEX "other_name_idx" ON "migration_operations_hope" ("name", "created_at")', id="multi-column"
        ),
        pytest.param(
            'CREATE INDEX "other_name_idx" ON "migration_operations_hope" ("name") INCLUDE ("created_at")',
            id="include",
        ),
        pytest.param(
            'CREATE INDEX "other_name_idx" ON "migration_operations_hope" ("name") WHERE "created_at" IS NOT NULL',
            id="partial",
        ),
        pytest.param('CREATE UNIQUE INDEX "other_name_idx" ON "migration_operations_hope" ("name")', id="unique"),
        pytest.param('CREATE INDEX "other_name_idx" ON "migration_operations_hope" USING hash ("name")', id="hash"),
        pytest.param(
            'CREATE INDEX "other_name_idx" ON "migration_operations_hope" ("name" COLLATE "C")', id="collation"
        ),
        pytest.param('CREATE INDEX "other_name_idx" ON "migration_operations_hope" ("name" DESC)', id="desc"),
        pytest.param(
            'CREATE INDEX "other_name_idx" ON "migration_operations_hope" ("name" NULLS FIRST)', id="nulls-first"
        ),
        pytest.param(
            'CREATE INDEX "other_name_idx" ON "migration_operations_hope" ("name" varchar_ops)',
            id="non-default-opclass",
        ),
    ],
    indirect=True,
)
def test_forwards_renames_btree_and_skips_other_index_on_column(
    project_state: ProjectState, drifted_name_index: int, other_name_index: int, index_oid
) -> None:
    operation = RenameDbIndex(model_name="hope", column="name", new_name="migration_name_idx")

    with connection.schema_editor() as editor:
        operation.database_forwards("migration_operations", editor, project_state, project_state)

    assert index_oid("migration_name_idx") == drifted_name_index
    assert index_oid("other_name_idx") == other_name_index


@pytest.mark.parametrize(
    "other_name_index",
    [
        pytest.param(
            'CREATE INDEX "other_name_idx" ON "migration_operations_hope" ("name" text_pattern_ops)',
            id="text-pattern-opclass",
        ),
    ],
    indirect=True,
)
def test_forwards_with_like_suffix_renames_like_twin_and_skips_other_pattern_index(
    project_state: ProjectState, drifted_name_like_index: int, other_name_index: int, index_oid
) -> None:
    operation = RenameDbIndex(model_name="hope", column="name", new_name="migration_name_lk", suffix="_like")

    with connection.schema_editor() as editor:
        operation.database_forwards("migration_operations", editor, project_state, project_state)

    assert index_oid("migration_name_lk") == drifted_name_like_index
    assert index_oid("other_name_idx") == other_name_index


@pytest.mark.parametrize("unusable_drifted_name_index", ["indisvalid", "indisready"], indirect=True)
def test_forwards_raises_when_btree_candidate_is_invalid(
    project_state: ProjectState, unusable_drifted_name_index: None
) -> None:
    operation = RenameDbIndex(model_name="hope", column="name", new_name="migration_name_idx")

    with (
        connection.schema_editor() as editor,
        pytest.raises(
            ValueError,
            match=r"Index legacy_hope_name_5e6f7a8b on migration_operations_hope\(name\) is invalid or not ready",
        ),
    ):
        operation.database_forwards("migration_operations", editor, project_state, project_state)


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
