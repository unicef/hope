# Generated by Django 2.2.16 on 2021-09-16 09:26

from django.db import migrations


def initialise_geo(apps, schema_editor):
    pass


def rebuild(apps, schema_editor):
    pass


def empty_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("geo", "0001_migration")
    ]

    operations = [
        migrations.RunPython(initialise_geo, empty_reverse),
        migrations.RunPython(rebuild, empty_reverse),
    ]