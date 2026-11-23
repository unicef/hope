from typing import Any

from django.db import migrations, router
from django.db.backends.base.schema import BaseDatabaseSchemaEditor
from django.db.migrations.state import ProjectState


class RunSQLAfterDeferred(migrations.RunSQL):
    """RunSQL whose statements run behind the deferred SQL of the migration.

    CreateModel and AddField create foreign keys and most indexes at the very end of the migration,
    so a plain RunSQL placed in the same migration runs before they exist. ``sql`` has to be a list
    of plain statements.
    """

    def database_forwards(
        self, app_label: str, schema_editor: BaseDatabaseSchemaEditor, from_state: Any, to_state: ProjectState
    ) -> None:
        if router.allow_migrate(schema_editor.connection.alias, app_label, **self.hints):
            schema_editor.deferred_sql.extend(self.sql)
