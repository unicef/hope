from django.db import migrations


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ("geo", "0008_migration"),
    ]

    operations = [
        # A column created as citext gets no varchar_pattern_ops twin, and the later switch to varchar
        # did not add one, so only databases built from scratch have these indexes.
        migrations.RunSQL(
            sql=[
                'DROP INDEX CONCURRENTLY IF EXISTS "geo_country_name_01731269_like"',
                'DROP INDEX CONCURRENTLY IF EXISTS "geo_country_short_name_00190511_like"',
                'DROP INDEX CONCURRENTLY IF EXISTS "geo_areatype_name_b20b6ba6_like"',
            ],
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
