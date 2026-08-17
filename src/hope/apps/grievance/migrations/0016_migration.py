from django.conf import settings
from django.contrib.postgres.operations import AddIndexConcurrently
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("grievance", "0015_migration"),
    ]

    operations = [
        migrations.AddField(
            model_name="grievanceticket",
            name="assigned_at",
            field=models.DateTimeField(
                blank=True,
                help_text="When the assignee of this ticket last changed.",
                null=True,
                verbose_name="Assignee changed at",
            ),
        ),
        migrations.AddField(
            model_name="grievanceticket",
            name="assigned_by",
            field=models.ForeignKey(
                blank=True,
                db_index=False,
                help_text="User who last changed the assignee of this ticket.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="assigned_tickets_by",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Assigned by",
            ),
        ),
        migrations.AddField(
            model_name="grievanceticket",
            name="user_modified_by",
            field=models.ForeignKey(
                blank=True,
                db_index=False,
                help_text="User who last edited this ticket through the update endpoint.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="modified_tickets",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Modified by",
            ),
        ),
        AddIndexConcurrently(
            model_name="grievanceticket",
            index=models.Index(fields=["assigned_at"], name="idx_gt_assigned_at"),
        ),
    ]
