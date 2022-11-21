def sql_drop_tables(connection, connection_name=""):
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