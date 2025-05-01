from typing import Any

from django.db import connections


def sql_drop_tables(connection: Any, connection_name: str = "") -> str:
    tables = connection.introspection.table_names(include_views=False)
    if "django_migrations" not in tables:
        tables.append("django_migrations")
    # fix 'cannot drop table addr because extension postgis_tiger_geocoder requires it'
    post_gis_tables = [
        "addr",
        "addrfeat",
        "bg",
        "county",
        "county_lookup",
        "countysub_lookup",
        "cousub",
        "direction_lookup",
        "edges",
        "faces",
        "featnames",
        "geocode_settings",
        "geocode_settings_default",
        "layer",
        "loader_lookuptables",
        "loader_platform",
        "loader_variables",
        "pagc_gaz",
        "pagc_lex",
        "pagc_rules",
        "place",
        "place_lookup",
        "secondary_unit_lookup",
        "state",
        "state_lookup",
        "street_type_lookup",
        "tabblock",
        "tabblock20",
        "topology",
        "tract",
        "zcta5",
        "zip_lookup",
        "zip_lookup_all",
        "zip_lookup_base",
        "zip_state",
        "zip_state_loc",
    ]
    tables = list(set(tables) - set(post_gis_tables))
    if not tables:
        return ""
    tables_sql = ", ".join(connection.ops.quote_name(table) for table in tables)
    sql = f"DROP TABLE IF EXISTS {tables_sql} CASCADE;"
    return f"BEGIN;\n{sql}\nCOMMIT;"


def drop_databases() -> None:
    for connection_name in connections:
        if connection_name == "read_only":
            continue
        connection = connections[connection_name]
        with connection.cursor() as cursor:
            sql = sql_drop_tables(connection)
            if not sql:
                continue
            return cursor.execute(sql)
    return None
