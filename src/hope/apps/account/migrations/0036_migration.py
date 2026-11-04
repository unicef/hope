from django.db import migrations

# Role permission names renamed with the payment list rename: roles store them as text.
PERMISSION_RENAMES = (
    ("PM_SYNC_PAYMENT_PLAN_WITH_PG", "PM_SYNC_PAYMENT_LIST_WITH_PG"),
    ("PM_PAYMENT_PLAN_GROUP_VIEW_LIST", "PM_PAYMENT_PLAN_VIEW_LIST"),
    ("PM_PAYMENT_PLAN_GROUP_VIEW_DETAIL", "PM_PAYMENT_PLAN_VIEW_DETAIL"),
    ("PM_PAYMENT_PLAN_GROUP_CREATE", "PM_PAYMENT_PLAN_CREATE"),
    ("PM_PAYMENT_PLAN_GROUP_UPDATE", "PM_PAYMENT_PLAN_UPDATE"),
    ("PM_PAYMENT_PLAN_GROUP_DELETE", "PM_PAYMENT_PLAN_DELETE"),
    ("PM_PAYMENT_PLAN_GROUP_SEND_TO_PAYMENT_GATEWAY", "PM_PAYMENT_PLAN_SEND_TO_PAYMENT_GATEWAY"),
    ("PM_PAYMENT_PLAN_GROUP_EXPORT_XLSX", "PM_PAYMENT_PLAN_EXPORT_XLSX"),
    ("PM_PAYMENT_PLAN_GROUP_IMPORT_XLSX", "PM_PAYMENT_PLAN_IMPORT_XLSX"),
)
RENAME_SQL = "UPDATE account_role SET permissions = array_replace(permissions, %s, %s) WHERE %s = ANY(permissions)"


def forwards(apps, schema_editor) -> None:
    for old, new in PERMISSION_RENAMES:
        schema_editor.execute(RENAME_SQL, [old, new, old])


def backwards(apps, schema_editor) -> None:
    for old, new in PERMISSION_RENAMES:
        schema_editor.execute(RENAME_SQL, [new, old, new])


class Migration(migrations.Migration):
    dependencies = [
        ("account", "0035_migration"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
