from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("registration_data", "0013_migration"),
    ]

    operations = [
        migrations.AddField(
            model_name="registrationdataimport",
            name="correlation_id",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="registrationdataimport",
            name="dedup_approve_attempts",
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="registrationdataimport",
            name="dedup_approved_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddConstraint(
            model_name="registrationdataimport",
            constraint=models.UniqueConstraint(
                condition=models.Q(("correlation_id__isnull", False)),
                fields=("correlation_id",),
                name="unique_rdi_correlation_id",
            ),
        ),
        migrations.AlterField(
            model_name="deduplicationenginesimilaritypair",
            name="status_code",
            field=models.CharField(
                choices=[
                    ("200", "Deduplication success"),
                    ("404", "No file found"),
                    ("412", "No face detected"),
                    ("416", "Face below confidence"),
                    ("418", "Image quality below threshold"),
                    ("429", "Multiple faces detected"),
                    ("500", "Generic error"),
                ],
                max_length=20,
            ),
        ),
    ]
