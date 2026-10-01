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

    @property
    def is_like(self) -> bool:
        return self.suffix == "_like"

    @property
    def kind(self) -> str:
        return "varchar_pattern_ops btree" if self.is_like else "btree"

    def database_forwards(
        self, app_label: str, schema_editor: BaseDatabaseSchemaEditor, from_state: ProjectState, to_state: ProjectState
    ) -> None:
        db_table = from_state.apps.get_model(app_label, self.model_name)._meta.db_table

        if self._target_exists(schema_editor, db_table):
            return

        candidates = self._candidates(schema_editor, db_table)
        if not candidates:
            # A missing twin is known drift on long-lived databases; this operation never creates an index.
            if self.is_like:
                return
            raise ValueError(f"Found no btree index on {db_table}({self.column}) to rename to {self.new_name}.")
        if len(candidates) == 1:
            (old_name,) = candidates
        else:
            old_name = schema_editor._create_index_name(db_table, [self.column], self.suffix)
            if old_name not in candidates:
                raise ValueError(
                    f"Found {len(candidates)} {self.kind} indexes on {db_table}({self.column}) and none is named "
                    f"{old_name}: {', '.join(candidates)}."
                )
        schema_editor.execute(
            schema_editor.sql_rename_index
            % {"old_name": schema_editor.quote_name(old_name), "new_name": schema_editor.quote_name(self.new_name)},
            params=None,
        )

    def _target_exists(self, schema_editor: BaseDatabaseSchemaEditor, db_table: str) -> bool:
        """Return whether ``new_name`` already exists in the table's schema; raise if it is not this index."""
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
                    "is_like": self.is_like,
                    "new_name": self.new_name,
                },
            )
            target = cursor.fetchone()

        if target is None:
            return False

        matches, definition = target
        if not matches:
            raise ValueError(
                f"Index {self.new_name} already exists but is not the {self.kind} index on {db_table}({self.column}): "
                f"{definition}"
            )
        return True

    def _candidates(self, schema_editor: BaseDatabaseSchemaEditor, db_table: str) -> list[str]:
        """Return the names of the indexes of this kind that ``db_index=True`` may have created on the column."""
        with schema_editor.connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT index_class.relname, idx.indisvalid AND idx.indisready
                FROM pg_index AS idx
                JOIN pg_class AS index_class ON index_class.oid = idx.indexrelid
                JOIN pg_am AS am ON am.oid = index_class.relam
                JOIN pg_opclass AS opclass ON opclass.oid = idx.indclass[0]
                JOIN pg_attribute AS att ON att.attrelid = idx.indrelid AND att.attnum = idx.indkey[0]
                WHERE idx.indrelid = %(table)s::regclass
                  AND idx.indnatts = 1
                  AND att.attname = %(column)s
                  AND am.amname = 'btree'
                  AND CASE WHEN %(is_like)s THEN opclass.opcname = 'varchar_pattern_ops' ELSE opclass.opcdefault END
                  AND idx.indcollation[0] = att.attcollation
                  AND idx.indoption[0] = 0
                  AND idx.indpred IS NULL
                  AND NOT idx.indisunique
                ORDER BY index_class.relname
                """,
                {"table": schema_editor.quote_name(db_table), "column": self.column, "is_like": self.is_like},
            )
            rows = cursor.fetchall()

        candidates = []
        for name, usable in rows:
            # A failed CREATE INDEX CONCURRENTLY leaves an index that the planner ignores; renaming would hide it.
            if not usable:
                raise ValueError(
                    f"Index {name} on {db_table}({self.column}) is invalid or not ready; "
                    f"rebuild or drop it before renaming to {self.new_name}."
                )
            candidates.append(name)
        return candidates
