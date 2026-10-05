from django.db import migrations


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ("payment", "0078_migration"),
    ]

    operations = [
        # Long-lived databases have no varchar_pattern_ops twin of unicef_id; only db_index=True on a
        # database built from scratch creates one.
        migrations.RunSQL(
            sql=[
                'DROP INDEX CONCURRENTLY IF EXISTS "payment_payment_unicef_id_07f610de_like"',
                'DROP INDEX CONCURRENTLY IF EXISTS "payment_paymentplan_unicef_id_ba96bd54_like"',
            ],
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
