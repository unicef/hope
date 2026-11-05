from django.db import migrations

ACTOR_FIELDS = (
    ("Approval", "created_by"),
    ("ApprovalProcess", "sent_for_approval_by"),
    ("ApprovalProcess", "sent_for_authorization_by"),
    ("ApprovalProcess", "sent_for_finance_release_by"),
)


def copy_actor_from_user_record(apps, schema_editor):
    """Prefill the `<field>_name`, `<field>_job_title`, and `<field>_job_title_source` columns from the current user record."""
    user_model = apps.get_model("account", "User")
    for model_name, field in ACTOR_FIELDS:
        model = apps.get_model("payment", model_name)
        pending = model.objects.filter(**{f"{field}__isnull": False, f"{field}_job_title_source": ""})
        for user in user_model.objects.filter(pk__in=pending.values(f"{field}_id")):
            values = {
                f"{field}_name": f"{user.first_name} {user.last_name}".strip(),
                f"{field}_job_title": user.job_title,
                f"{field}_job_title_source": "USER_RECORD",
            }
            pending.filter(**{field: user}).update(**values)


class Migration(migrations.Migration):
    dependencies = [
        ("payment", "0084_migration"),
    ]

    operations = [
        migrations.RunPython(copy_actor_from_user_record, migrations.RunPython.noop),
    ]
