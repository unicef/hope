from django.db import migrations

# Rules get the payment list as "payment_list"; stored definitions still name it "payment_plan".
RENAME_SQL = (
    "UPDATE {table} SET definition = regexp_replace(definition, '\\m{old}\\M', '{new}', 'g') "
    "WHERE definition ~ '\\m{old}\\M'"
)
TABLES = ("steficon_rule", "steficon_rulecommit")


def rename(schema_editor, old: str, new: str) -> None:
    for table in TABLES:
        schema_editor.execute(RENAME_SQL.format(table=table, old=old, new=new))


def forwards(apps, schema_editor) -> None:
    rename(schema_editor, "payment_plan", "payment_list")


def backwards(apps, schema_editor) -> None:
    rename(schema_editor, "payment_list", "payment_plan")


class Migration(migrations.Migration):
    dependencies = [
        ("steficon", "0008_migration"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
