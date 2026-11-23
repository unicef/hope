from django.db import migrations

OLD_NAME = "WU_PAYMENT_PLAN_INVOICES_NOTIFICATIONS_ENABLED"
NEW_NAME = "WU_PAYMENT_LIST_INVOICES_NOTIFICATIONS_ENABLED"


def _rename_flag(apps, old: str, new: str) -> None:
    flag_state_model = apps.get_model("flags", "FlagState")
    taken = set(flag_state_model.objects.filter(name=new).values_list("condition", "value"))
    for flag_state in flag_state_model.objects.filter(name=old):
        if (flag_state.condition, flag_state.value) in taken:
            flag_state.delete()
        else:
            flag_state.name = new
            flag_state.save(update_fields=["name"])


def forwards(apps, schema_editor) -> None:
    _rename_flag(apps, OLD_NAME, NEW_NAME)


def backwards(apps, schema_editor) -> None:
    _rename_flag(apps, NEW_NAME, OLD_NAME)


class Migration(migrations.Migration):
    dependencies = [
        ("flags", "0014_flagstate_unique_constraint"),
        ("payment", "0088_migration"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
