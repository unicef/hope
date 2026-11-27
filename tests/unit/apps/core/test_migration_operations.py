from django.db import connections
import pytest

from hope.apps.core.migration_operations import RunSQLAfterDeferred


@pytest.mark.django_db(databases=["default", "read_only"])
@pytest.mark.parametrize(
    ("alias", "expected"),
    [
        pytest.param("default", ["SELECT 1", "SELECT 2", "SELECT 3"], id="migrated database"),
        pytest.param("read_only", ["SELECT 1"], id="database the router does not migrate"),
    ],
)
def test_run_sql_after_deferred_queues_statements_behind_deferred_sql(alias: str, expected: list[str]) -> None:
    operation = RunSQLAfterDeferred(sql=["SELECT 2", "SELECT 3"])

    with connections[alias].schema_editor() as schema_editor:
        schema_editor.deferred_sql.append("SELECT 1")
        operation.database_forwards("core", schema_editor, None, None)
        queued = list(schema_editor.deferred_sql)

    assert queued == expected
