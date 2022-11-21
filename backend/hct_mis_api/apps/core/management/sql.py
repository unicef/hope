def sql_drop_tables(connection):
    tables = connection.introspection.django_table_names(only_existing=True, include_views=False)
    nnn = connection.introspection.table_names(include_views=False)
    nnn.append("django_migrations")

    print("Get all names", nnn)
    if not nnn:
        return ""
    tables_sql = ", ".join(connection.ops.quote_name(table) for table in nnn)
    sql = f"DROP TABLE IF EXISTS {tables_sql} CASCADE;"
    return "\n".join(["BEGIN;", sql, "COMMIT;"])
