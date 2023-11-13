from typing import Any

from django.db import connections


def sql_drop_tables(connection: Any, connection_name: str = "") -> str:
    tables = connection.introspection.table_names(include_views=False)
    tables.append("django_migrations")
    print("=>>> TABLES:", tables)
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
        print(f"dropping tables for {connection_name}")
        with connection.cursor() as cursor:
            sql = sql_drop_tables(connection)
            print(sql)
            if not sql:
                continue
            return cursor.execute(sql)
