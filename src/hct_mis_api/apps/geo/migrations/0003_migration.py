# Generated by Django 2.2.16 on 2021-09-16 09:26

from django.db import migrations


def preload_areas(apps, schema_editor):
    pass


def rebuild(apps, schema_editor):
    pass


def empty_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("geo", "0002_migration"),
        ("core", "0017_migration_squashed_0040_migration"),
    ]

    operations = [
        migrations.RunPython(preload_areas, empty_reverse),
        migrations.RunPython(rebuild, empty_reverse),
    ]