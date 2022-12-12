from typing import Any

from django.db import connections


def sql_drop_tables(connection: Any, connection_name: str = "") -> str:
    if connection_name == "default":
        # TODO: sometimes tables not dropped if using .django_table_names()
        tables = connection.introspection.table_names(include_views=False)
    else:
        tables = connection.introspection.django_table_names(only_existing=True, include_views=False)
    tables.append("django_migrations")
    if not tables:
        return ""
    tables_sql = ", ".join(connection.ops.quote_name(table) for table in tables)
    sql = f"DROP TABLE IF EXISTS {tables_sql} CASCADE;"
    return "\n".join(["BEGIN;", sql, "COMMIT;"])


def drop_databases() -> None:
    for connection_name in connections:
        if connection_name == "read_only":
            continue
        connection = connections[connection_name]
        with connection.cursor() as cursor:
            sql = sql_drop_tables(connection)
            if not sql:
                continue
            cursor.execute(sql)
