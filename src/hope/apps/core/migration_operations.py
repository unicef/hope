from django.db.backends.base.schema import BaseDatabaseSchemaEditor
from django.db.migrations.operations.base import Operation, OperationCategory
from django.db.migrations.state import ProjectState


class RenameDbIndex(Operation):
    """Rename the single-column index that ``db_index=True`` created, found by its column.

    Index names on long-lived databases drift from what Django computes today (renamed models and
    fields, migration history rewritten with ``--fake``), so the name cannot identify the index.
    """

    category = OperationCategory.ALTERATION

    def __init__(self, model_name: str, column: str, new_name: str) -> None:
        self.model_name = model_name
        self.column = column
        self.new_name = new_name

    def database_forwards(
        self, app_label: str, schema_editor: BaseDatabaseSchemaEditor, from_state: ProjectState, to_state: ProjectState
    ) -> None:
        model = from_state.apps.get_model(app_label, self.model_name)
        with schema_editor.connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT index_class.relname
                FROM pg_index AS idx
                JOIN pg_class AS index_class ON index_class.oid = idx.indexrelid
                JOIN pg_attribute AS att ON att.attrelid = idx.indrelid AND att.attnum = idx.indkey[0]
                WHERE idx.indrelid = %s::regclass AND att.attname = %s
                """,
                [schema_editor.quote_name(model._meta.db_table), self.column],
            )
            (old_name,) = cursor.fetchone()
        schema_editor.execute(
            schema_editor.sql_rename_index
            % {"old_name": schema_editor.quote_name(old_name), "new_name": schema_editor.quote_name(self.new_name)},
            params=None,
        )
