from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0028_migration"),
    ]

    operations = [
        migrations.RunSQL(
            sql="DROP TABLE IF EXISTS core_surprisepageconfig;",
            reverse_sql="",
        ),
    ]
