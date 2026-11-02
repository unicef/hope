from django.db import migrations


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ("household", "0051_migration"),
    ]

    operations = [
        # A column created as citext gets no varchar_pattern_ops twin, and the later switch to varchar
        # did not add one, so only databases built from scratch have these indexes.
        migrations.RunSQL(
            sql=[
                'DROP INDEX CONCURRENTLY IF EXISTS "household_individual_full_name_8fa0162b_like"',
                'DROP INDEX CONCURRENTLY IF EXISTS "household_individual_given_name_1ebbded2_like"',
                'DROP INDEX CONCURRENTLY IF EXISTS "household_individual_middle_name_1dfbf837_like"',
                'DROP INDEX CONCURRENTLY IF EXISTS "household_individual_family_name_4d6db55f_like"',
            ],
            reverse_sql=migrations.RunSQL.noop,
        ),
        # Older databases got the document_number index from AddIndexConcurrently, which creates no
        # varchar_pattern_ops twin; only db_index=True on a database built from scratch does.
        migrations.RunSQL(
            sql=[
                'DROP INDEX CONCURRENTLY IF EXISTS "household_document_document_number_43773c34_like"',
            ],
            reverse_sql=migrations.RunSQL.noop,
        ),
        # Long-lived databases have no varchar_pattern_ops twin of unicef_id; only db_index=True on a
        # database built from scratch creates one.
        migrations.RunSQL(
            sql=[
                'DROP INDEX CONCURRENTLY IF EXISTS "household_household_unicef_id_6f025c4d_like"',
                'DROP INDEX CONCURRENTLY IF EXISTS "household_individual_unicef_id_421e2ff2_like"',
            ],
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
