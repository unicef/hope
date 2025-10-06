from django.db import connections

SQL = """
    DO $$
    DECLARE
        seq_name text;
    BEGIN
        FOR seq_name IN (SELECT sequence_name
                        FROM information_schema.sequences
                        WHERE sequence_name LIKE '%_business_area_seq_%')
        LOOP
            EXECUTE 'SELECT setval($1, 1, false)' USING seq_name;
        END LOOP;
    END $$;
"""


def reset_business_area_sequences() -> None:
    for connection_name in connections:
        if connection_name == "read_only":
            continue
        connection = connections[connection_name]
        with connection.cursor() as cursor:
            cursor.execute(SQL)
