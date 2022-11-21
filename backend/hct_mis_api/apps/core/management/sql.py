def sql_drop_tables(connection, connection_name=""):
    print("Connn ", connection_name)
    tables = connection.introspection.django_table_names(only_existing=True, include_views=False)
    tables222 = connection.introspection.django_table_names(only_existing=False, include_views=False)
    if connection_name == "default":
        tables = tables222
    nnn = connection.introspection.table_names(include_views=False)
    tables.append("django_migrations")

    print("django tables==> ", tables)
    print("only_existing=False django tables==>: ", tables222)

    print("Get all names: ...>>>>>>> ", nnn)
    if not tables222:
        return ""
    tables_sql = ", ".join(connection.ops.quote_name(table) for table in tables)
    sql = f"DROP TABLE IF EXISTS {tables_sql} CASCADE;"
    return "\n".join(["BEGIN;", sql, "COMMIT;"])
