# Generated by Django 3.2.25 on 2025-02-19 15:37

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("grievance", "0008_migration"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="grievanceticket",
            name="is_migration_handled",
        ),
        migrations.RemoveField(
            model_name="grievanceticket",
            name="migrated_at",
        ),
    ]
