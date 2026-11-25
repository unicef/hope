from django.db import migrations, models

JOB_TITLE_SOURCE_CHOICES = [("AD", "Active Directory"), ("USER_RECORD", "User record")]


class Migration(migrations.Migration):
    dependencies = [
        ("payment", "0083_migration"),
    ]

    operations = [
        migrations.AddField(
            model_name="approval",
            name="created_by_name",
            field=models.CharField(blank=True, default="", max_length=301),
        ),
        migrations.AddField(
            model_name="approval",
            name="created_by_job_title",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
        migrations.AddField(
            model_name="approval",
            name="created_by_job_title_source",
            field=models.CharField(blank=True, choices=JOB_TITLE_SOURCE_CHOICES, default="", max_length=16),
        ),
        migrations.AddField(
            model_name="approvalprocess",
            name="sent_for_approval_by_name",
            field=models.CharField(blank=True, default="", max_length=301),
        ),
        migrations.AddField(
            model_name="approvalprocess",
            name="sent_for_approval_by_job_title",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
        migrations.AddField(
            model_name="approvalprocess",
            name="sent_for_approval_by_job_title_source",
            field=models.CharField(blank=True, choices=JOB_TITLE_SOURCE_CHOICES, default="", max_length=16),
        ),
        migrations.AddField(
            model_name="approvalprocess",
            name="sent_for_authorization_by_name",
            field=models.CharField(blank=True, default="", max_length=301),
        ),
        migrations.AddField(
            model_name="approvalprocess",
            name="sent_for_authorization_by_job_title",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
        migrations.AddField(
            model_name="approvalprocess",
            name="sent_for_authorization_by_job_title_source",
            field=models.CharField(blank=True, choices=JOB_TITLE_SOURCE_CHOICES, default="", max_length=16),
        ),
        migrations.AddField(
            model_name="approvalprocess",
            name="sent_for_finance_release_by_name",
            field=models.CharField(blank=True, default="", max_length=301),
        ),
        migrations.AddField(
            model_name="approvalprocess",
            name="sent_for_finance_release_by_job_title",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
        migrations.AddField(
            model_name="approvalprocess",
            name="sent_for_finance_release_by_job_title_source",
            field=models.CharField(blank=True, choices=JOB_TITLE_SOURCE_CHOICES, default="", max_length=16),
        ),
    ]
