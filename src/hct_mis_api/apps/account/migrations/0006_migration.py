# Generated by Django 3.2.25 on 2025-01-28 13:16

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("account", "0005_migration"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="doap_hash",
        ),
        migrations.RemoveField(
            model_name="user",
            name="last_doap_sync",
        ),
    ]
