from django.db import connection, models
from django.db.migrations import Migration
from django.db.migrations.operations import AddIndex, SeparateDatabaseAndState
from django.db.migrations.state import ModelState, ProjectState
from django.db.migrations.writer import OperationWriter
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
                ("timestamp", models.DateTimeField()),
            ],
        )
    )
    return state


@pytest.fixture
def hope_table(project_state: ProjectState) -> None:
    with connection.schema_editor() as editor:
        editor.create_model(project_state.apps.get_model("migration_operations", "Hope"))


@pytest.fixture
def hope_app_routed_to_other_database(settings) -> None:
    settings.DATABASE_APPS_MAPPING = {"migration_operations": "other"}


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
def drifted_timestamp_index(hope_table: None, index_oid) -> int:
    with connection.cursor() as cursor:
        cursor.execute('CREATE INDEX "legacy_hope_timestamp_9c0d1e2f" ON "migration_operations_hope" ("timestamp")')
    return index_oid("legacy_hope_timestamp_9c0d1e2f")


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
def canonical_created_at_index(hope_table: None, index_oid) -> int:
    """The btree under the name a fresh ``migrate`` gives it, next to a duplicate added by hand under another name."""
    with connection.schema_editor() as editor:
        name = editor._create_index_name("migration_operations_hope", ["created_at"])
        editor.execute(f'CREATE INDEX "{name}" ON "migration_operations_hope" ("created_at")')
    return index_oid(name)


@pytest.fixture
def duplicate_created_at_index(hope_table: None, index_oid) -> int:
    with connection.cursor() as cursor:
        cursor.execute('CREATE INDEX "manual_created_at_idx" ON "migration_operations_hope" ("created_at")')
    return index_oid("manual_created_at_idx")


@pytest.fixture
def canonical_name_like_index(hope_table: None, index_oid) -> int:
    with connection.schema_editor() as editor:
        name = editor._create_index_name("migration_operations_hope", ["name"], "_like")
        editor.execute(f'CREATE INDEX "{name}" ON "migration_operations_hope" ("name" varchar_pattern_ops)')
    return index_oid(name)


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


def test_forwards_renames_canonically_named_btree_and_keeps_duplicate(
    project_state: ProjectState, canonical_created_at_index: int, drifted_created_at_index: int, index_oid
) -> None:
    operation = RenameDbIndex(model_name="hope", column="created_at", new_name="migration_created_idx")

    with connection.schema_editor() as editor:
        operation.database_forwards("migration_operations", editor, project_state, project_state)

    assert index_oid("migration_created_idx") == canonical_created_at_index
    assert index_oid("legacy_hope_created_at_1a2b3c4d") == drifted_created_at_index


def test_forwards_with_like_suffix_renames_canonically_named_twin_and_keeps_duplicate(
    project_state: ProjectState, canonical_name_like_index: int, drifted_name_like_index: int, index_oid
) -> None:
    operation = RenameDbIndex(model_name="hope", column="name", new_name="migration_name_lk", suffix="_like")

    with connection.schema_editor() as editor:
        operation.database_forwards("migration_operations", editor, project_state, project_state)

    assert index_oid("migration_name_lk") == canonical_name_like_index
    assert index_oid("legacy_hope_name_5e6f7a8b_like") == drifted_name_like_index


def test_forwards_raises_when_no_duplicate_btree_has_canonical_name(
    project_state: ProjectState, drifted_created_at_index: int, duplicate_created_at_index: int
) -> None:
    operation = RenameDbIndex(model_name="hope", column="created_at", new_name="migration_created_idx")

    with (
        connection.schema_editor() as editor,
        pytest.raises(
            ValueError,
            match=(
                r"Found 2 btree indexes on migration_operations_hope\(created_at\) and none is named "
                r"migration_operations_hope_created_at_\w+: legacy_hope_created_at_1a2b3c4d, manual_created_at_idx"
            ),
        ),
    ):
        operation.database_forwards("migration_operations", editor, project_state, project_state)


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


def test_backwards_renames_target_to_canonical_name(
    project_state: ProjectState, target_created_at_index: int, index_oid
) -> None:
    operation = RenameDbIndex(model_name="hope", column="created_at", new_name="migration_created_idx")

    with connection.schema_editor() as editor:
        operation.database_backwards("migration_operations", editor, project_state, project_state)
        canonical_name = editor._create_index_name("migration_operations_hope", ["created_at"])

    assert index_oid(canonical_name) == target_created_at_index
    assert index_oid("migration_created_idx") is None


@pytest.mark.parametrize(
    "target_name_index",
    [
        pytest.param(
            ['CREATE INDEX "migration_name_lk" ON "migration_operations_hope" ("name" varchar_pattern_ops)'],
            id="varchar-pattern-opclass",
        ),
    ],
    indirect=True,
)
def test_backwards_with_like_suffix_renames_target_to_canonical_like_name(
    project_state: ProjectState, target_name_index: None, index_oid
) -> None:
    target_oid = index_oid("migration_name_lk")
    operation = RenameDbIndex(model_name="hope", column="name", new_name="migration_name_lk", suffix="_like")

    with connection.schema_editor() as editor:
        operation.database_backwards("migration_operations", editor, project_state, project_state)
        canonical_name = editor._create_index_name("migration_operations_hope", ["name"], "_like")

    assert index_oid(canonical_name) == target_oid


def test_backwards_with_like_suffix_is_noop_when_target_is_missing(
    project_state: ProjectState, drifted_name_index: int, index_oid
) -> None:
    """Forwards skipped the missing twin, so backwards finds nothing under the target name either."""
    operation = RenameDbIndex(model_name="hope", column="name", new_name="migration_name_lk", suffix="_like")

    with connection.schema_editor(collect_sql=True) as editor:
        operation.database_backwards("migration_operations", editor, project_state, project_state)

    assert editor.collected_sql == []


@pytest.mark.parametrize(
    "target_name_index",
    [
        pytest.param(
            ['CREATE INDEX "migration_name_idx" ON "migration_operations_hope" ("created_at")'], id="other-column"
        ),
    ],
    indirect=True,
)
def test_backwards_raises_when_target_has_other_definition(
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
        operation.database_backwards("migration_operations", editor, project_state, project_state)


def test_forwards_sets_lock_timeout_before_rename(project_state: ProjectState, drifted_created_at_index: int) -> None:
    operation = RenameDbIndex(model_name="hope", column="created_at", new_name="migration_created_idx")

    with connection.schema_editor(collect_sql=True) as editor:
        operation.database_forwards("migration_operations", editor, project_state, project_state)

    assert editor.collected_sql == [
        "SET LOCAL lock_timeout = '5s';",
        'ALTER INDEX "legacy_hope_created_at_1a2b3c4d" RENAME TO "migration_created_idx";',
    ]


def test_backwards_sets_lock_timeout_before_rename(project_state: ProjectState, target_created_at_index: int) -> None:
    operation = RenameDbIndex(model_name="hope", column="created_at", new_name="migration_created_idx")

    with connection.schema_editor(collect_sql=True) as editor:
        operation.database_backwards("migration_operations", editor, project_state, project_state)
        canonical_name = editor._create_index_name("migration_operations_hope", ["created_at"])

    assert editor.collected_sql == [
        "SET LOCAL lock_timeout = '5s';",
        f'ALTER INDEX "migration_created_idx" RENAME TO "{canonical_name}";',
    ]


def test_forwards_is_noop_when_router_disallows_migrating_model(
    project_state: ProjectState, drifted_created_at_index: int, hope_app_routed_to_other_database: None
) -> None:
    operation = RenameDbIndex(model_name="hope", column="created_at", new_name="migration_created_idx")

    with connection.schema_editor(collect_sql=True) as editor:
        operation.database_forwards("migration_operations", editor, project_state, project_state)

    assert editor.collected_sql == []


def test_backwards_is_noop_when_router_disallows_migrating_model(
    project_state: ProjectState, target_created_at_index: int, hope_app_routed_to_other_database: None
) -> None:
    operation = RenameDbIndex(model_name="hope", column="created_at", new_name="migration_created_idx")

    with connection.schema_editor(collect_sql=True) as editor:
        operation.database_backwards("migration_operations", editor, project_state, project_state)

    assert editor.collected_sql == []


def test_forwards_renames_btree_on_column_named_after_sql_keyword(
    project_state: ProjectState, drifted_timestamp_index: int, index_oid
) -> None:
    operation = RenameDbIndex(model_name="hope", column="timestamp", new_name="migration_timestamp_idx")

    with connection.schema_editor() as editor:
        operation.database_forwards("migration_operations", editor, project_state, project_state)

    assert index_oid("migration_timestamp_idx") == drifted_timestamp_index


def test_writer_serializes_operation_with_its_module_path() -> None:
    """Migrations import the operation by this path forever, so moving or renaming it breaks them."""
    operation = RenameDbIndex(model_name="hope", column="name", new_name="migration_name_lk", suffix="_like")

    serialized = OperationWriter(operation, indentation=0).serialize()

    assert serialized == (
        "hope.apps.core.migration_operations.RenameDbIndex(\n"
        "    model_name='hope',\n"
        "    column='name',\n"
        "    new_name='migration_name_lk',\n"
        "    suffix='_like',\n"
        "),",
        {"import hope.apps.core.migration_operations"},
    )


@pytest.mark.parametrize(
    ("suffix", "description"),
    [
        pytest.param("", "Rename btree index on hope.name to migration_name_idx", id="btree"),
        pytest.param("_like", "Rename varchar_pattern_ops btree index on hope.name to migration_name_idx", id="like"),
    ],
)
def test_describe_names_index_kind_column_and_target(suffix: str, description: str) -> None:
    operation = RenameDbIndex(model_name="hope", column="name", new_name="migration_name_idx", suffix=suffix)

    assert operation.describe() == description


def test_separate_database_and_state_backwards_restores_canonical_name_and_keeps_duplicate(
    project_state: ProjectState, canonical_created_at_index: int, duplicate_created_at_index: int, index_oid
) -> None:
    operation = SeparateDatabaseAndState(
        state_operations=[AddIndex("hope", models.Index(fields=["created_at"], name="migration_created_idx"))],
        database_operations=[RenameDbIndex(model_name="hope", column="created_at", new_name="migration_created_idx")],
    )
    new_state = project_state.clone()
    operation.state_forwards("migration_operations", new_state)

    with connection.schema_editor() as editor:
        operation.database_forwards("migration_operations", editor, project_state, new_state)
        operation.database_backwards("migration_operations", editor, new_state, project_state)
        canonical_name = editor._create_index_name("migration_operations_hope", ["created_at"])

    assert index_oid(canonical_name) == canonical_created_at_index
    assert index_oid("manual_created_at_idx") == duplicate_created_at_index
    assert index_oid("migration_created_idx") is None


def test_separate_database_and_state_forwards_again_after_backwards_picks_canonical_btree(
    project_state: ProjectState, canonical_created_at_index: int, duplicate_created_at_index: int, index_oid
) -> None:
    """Backwards must leave a name the tie-breaker accepts, or reapplying the migration fails on the duplicate."""
    operation = SeparateDatabaseAndState(
        state_operations=[AddIndex("hope", models.Index(fields=["created_at"], name="migration_created_idx"))],
        database_operations=[RenameDbIndex(model_name="hope", column="created_at", new_name="migration_created_idx")],
    )
    new_state = project_state.clone()
    operation.state_forwards("migration_operations", new_state)

    with connection.schema_editor() as editor:
        operation.database_forwards("migration_operations", editor, project_state, new_state)
        operation.database_backwards("migration_operations", editor, new_state, project_state)
        operation.database_forwards("migration_operations", editor, project_state, new_state)

    assert index_oid("migration_created_idx") == canonical_created_at_index
    assert index_oid("manual_created_at_idx") == duplicate_created_at_index


def test_separate_database_and_state_rename_is_rolled_back_when_later_operation_fails(
    project_state: ProjectState, drifted_created_at_index: int, index_oid
) -> None:
    migration = Migration("0001_rename_db_indexes", "migration_operations")
    migration.operations = [
        SeparateDatabaseAndState(
            state_operations=[AddIndex("hope", models.Index(fields=["created_at"], name="migration_created_idx"))],
            database_operations=[
                RenameDbIndex(model_name="hope", column="created_at", new_name="migration_created_idx")
            ],
        ),
        RenameDbIndex(model_name="hope", column="name", new_name="migration_name_idx"),
    ]

    with pytest.raises(ValueError, match="Found no btree index"), connection.schema_editor() as editor:
        migration.apply(project_state, editor)

    assert index_oid("legacy_hope_created_at_1a2b3c4d") == drifted_created_at_index
    assert index_oid("migration_created_idx") is None
