import uuid

import django.db.models.deletion
import model_utils.fields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grievance', '0055_migration'),
        ("account", "0038_migration"),
        ("program", "0034_migration"),
    ]

    operations = [
        migrations.AddField(
            model_name="grievanceticket",
            name="priority",
            field=models.IntegerField(
                choices=[(1, "High"), (2, "Medium"), (3, "Low")], default=3, verbose_name="Priority"
            ),
        ),
        migrations.AddField(
            model_name="grievanceticket",
            name="urgency",
            field=models.IntegerField(
                choices=[(1, "Very urgent"), (2, "Urgent"), (3, "Not urgent")], default=3, verbose_name="Urgency"
            ),
        ),
        migrations.AddField(
            model_name="grievanceticket",
            name="partner",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="account.partner"
            ),
        ),
        migrations.AddField(
            model_name="grievanceticket",
            name="comments",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="grievanceticket",
            name="programme",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="program.program"
            ),
        ),
        migrations.CreateModel(
            name="GrievanceDocument",
            fields=[
                (
                    "id",
                    model_utils.fields.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=100, null=True)),
                ("file", models.FileField(blank=True, null=True, upload_to="")),
                ("file_size", models.IntegerField(null=True)),
                ("content_type", models.CharField(max_length=100)),
                (
                    "created_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "grievance_ticket",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="support_documents",
                        to="grievance.grievanceticket",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
