# Generated by Django 3.2.25 on 2025-01-15 14:51

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("account", "0002_migration"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="user",
            options={
                "permissions": (
                    ("can_load_from_ad", "Can load users from ActiveDirectory"),
                    ("can_sync_with_ad", "Can synchronise user with ActiveDirectory"),
                    ("can_create_kobo_user", "Can create users in Kobo"),
                    ("can_import_from_kobo", "Can import and sync users from Kobo"),
                    ("can_upload_to_kobo", "Can upload CSV file to Kobo"),
                    ("can_debug", "Can access debug information"),
                    ("can_inspect", "Can inspect objects"),
                    ("quick_links", "Can see quick links in admin"),
                    ("restrict_help_desk", "Limit fields to be editable for help desk"),
                    ("can_reindex_programs", "Can reindex programs"),
                    ("can_add_business_area_to_partner", "Can add business area to partner"),
                    ("can_import_fixture", "Can import fixture"),
                )
            },
        ),
    ]
