from django.db import migrations


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ("program", "0022_migration"),
    ]

    operations = [
        # A column created as citext gets no varchar_pattern_ops twin, and the later switch to varchar
        # did not add one, so only databases built from scratch have this index.
        migrations.RunSQL(
            sql=[
                'DROP INDEX CONCURRENTLY IF EXISTS "program_program_name_2670ab01_like"',
            ],
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
