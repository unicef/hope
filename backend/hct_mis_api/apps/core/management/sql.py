from typing import Any


def sql_drop_tables(connection: Any) -> str:
    tables = connection.introspection.django_table_names(only_existing=True, include_views=False)
    tables.append("django_migrations")
    if not tables:
        return ""
    tables_sql = ", ".join(connection.ops.quote_name(table) for table in tables)
    sql = f"DROP TABLE IF EXISTS {tables_sql} CASCADE;"
    return "\n".join(["BEGIN;", sql, "COMMIT;"])
