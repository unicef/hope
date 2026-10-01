from django.db.backends.base.schema import BaseDatabaseSchemaEditor
from django.db.migrations.operations.base import Operation, OperationCategory
from django.db.migrations.state import ProjectState


class RenameDbIndex(Operation):
    """Rename the single-column index that ``db_index=True`` created, found by its column.

    Index names on long-lived databases drift from what Django computes today (renamed models and
    fields, migration history rewritten with ``--fake``), so the name cannot identify the index.
    """

    category = OperationCategory.ALTERATION

    def __init__(self, model_name: str, column: str, new_name: str, suffix: str = "") -> None:
        if suffix not in ("", "_like"):
            raise ValueError(f"RenameDbIndex suffix must be '' or '_like', got {suffix!r}.")
        self.model_name = model_name
        self.column = column
        self.new_name = new_name
        self.suffix = suffix

    def database_forwards(
        self, app_label: str, schema_editor: BaseDatabaseSchemaEditor, from_state: ProjectState, to_state: ProjectState
    ) -> None:
        model = from_state.apps.get_model(app_label, self.model_name)

        if self._target_exists(schema_editor, model._meta.db_table):
            return

        is_like = self.suffix == "_like"

        with schema_editor.connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT index_class.relname, opclass.opcname
                FROM pg_index AS idx
                JOIN pg_class AS index_class ON index_class.oid = idx.indexrelid
                JOIN pg_attribute AS att ON att.attrelid = idx.indrelid AND att.attnum = idx.indkey[0]
                JOIN pg_opclass AS opclass ON opclass.oid = idx.indclass[0]
                WHERE idx.indrelid = %s::regclass AND att.attname = %s
                """,
                [schema_editor.quote_name(model._meta.db_table), self.column],
            )
            candidates = [name for name, opclass in cursor.fetchall() if opclass.endswith("_pattern_ops") == is_like]
        if not candidates:
            # A missing twin is known drift on long-lived databases; this operation never creates an index.
            if is_like:
                return
            raise ValueError(
                f"Found no btree index on {model._meta.db_table}({self.column}) to rename to {self.new_name}."
            )
        (old_name,) = candidates
        schema_editor.execute(
            schema_editor.sql_rename_index
            % {"old_name": schema_editor.quote_name(old_name), "new_name": schema_editor.quote_name(self.new_name)},
            params=None,
        )

    def _target_exists(self, schema_editor: BaseDatabaseSchemaEditor, db_table: str) -> bool:
        """Return whether ``new_name`` already exists in the table's schema; raise if it is not this index."""
        is_like = self.suffix == "_like"

        with schema_editor.connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    idx.indrelid = %(table)s::regclass
                    AND idx.indnatts = 1
                    AND att.attname = %(column)s
                    AND am.amname = 'btree'
                    AND CASE WHEN %(is_like)s THEN opclass.opcname = 'varchar_pattern_ops' ELSE opclass.opcdefault END
                    AND idx.indcollation[0] = att.attcollation
                    AND idx.indoption[0] = 0
                    AND idx.indpred IS NULL
                    AND NOT idx.indisunique
                    AND idx.indisvalid
                    AND idx.indisready,
                    pg_get_indexdef(idx.indexrelid)
                FROM pg_class AS index_class
                JOIN pg_index AS idx ON idx.indexrelid = index_class.oid
                JOIN pg_am AS am ON am.oid = index_class.relam
                JOIN pg_opclass AS opclass ON opclass.oid = idx.indclass[0]
                LEFT JOIN pg_attribute AS att ON att.attrelid = idx.indrelid AND att.attnum = idx.indkey[0]
                WHERE index_class.relname = %(new_name)s
                  AND index_class.relnamespace = (SELECT relnamespace FROM pg_class WHERE oid = %(table)s::regclass)
                """,
                {
                    "table": schema_editor.quote_name(db_table),
                    "column": self.column,
                    "is_like": is_like,
                    "new_name": self.new_name,
                },
            )
            target = cursor.fetchone()

        if target is None:
            return False

        matches, definition = target
        if not matches:
            kind = "varchar_pattern_ops btree" if is_like else "btree"
            raise ValueError(
                f"Index {self.new_name} already exists but is not the {kind} index on {db_table}({self.column}): "
                f"{definition}"
            )
        return True
