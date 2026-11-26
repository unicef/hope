from django.db import migrations

# The payment plan pages check the payment plan permissions; roles keep the access their payment list permissions gave.
PERMISSION_GRANTS = (
    ("PM_VIEW_LIST", "PM_PAYMENT_PLAN_VIEW_LIST"),
    ("PM_VIEW_DETAILS", "PM_PAYMENT_PLAN_VIEW_DETAIL"),
    ("PM_CREATE", "PM_PAYMENT_PLAN_CREATE"),
    ("PM_CREATE", "PM_PAYMENT_PLAN_UPDATE"),
)
GRANT_SQL = (
    "UPDATE account_role SET permissions = array_append(permissions, %s) "
    "WHERE %s = ANY(permissions) AND NOT (%s = ANY(permissions))"
)


def forwards(apps, schema_editor) -> None:
    for held, granted in PERMISSION_GRANTS:
        schema_editor.execute(GRANT_SQL, [granted, held, granted])


class Migration(migrations.Migration):
    dependencies = [
        ("account", "0036_migration"),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
