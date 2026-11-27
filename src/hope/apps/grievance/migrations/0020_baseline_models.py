from decimal import Decimal
import uuid

import concurrency.fields
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import model_utils.fields

import hope.apps.grievance.constants
import hope.apps.grievance.models
import hope.models.payment_verification
import hope.models.utils


class Migration(migrations.Migration):
    initial = True

    replaces = [
        ("grievance", "0002_migration"),
        ("grievance", "0003_migration"),
        ("grievance", "0004_migration"),
        ("grievance", "0005_migration"),
        ("grievance", "0006_migration"),
        ("grievance", "0007_migration"),
        ("grievance", "0008_migration"),
        ("grievance", "0009_migration"),
        ("grievance", "0010_migration"),
        ("grievance", "0011_migration"),
        ("grievance", "0012_migration"),
        ("grievance", "0013_migration"),
        ("grievance", "0014_migration"),
        ("grievance", "0015_migration"),
        ("grievance", "0016_migration"),
        ("grievance", "0017_migration"),
        ("grievance", "0018_migration"),
        ("grievance", "0019_migration"),
        ("grievance", "0020_migration"),
    ]

    dependencies = [
        ("account", "0037_baseline_relations"),
        ("core", "0041_baseline_models"),
        ("geo", "0010_baseline_models"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="GrievanceTicketThrough",
            fields=[
                (
                    "id",
                    model_utils.fields.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="MyTasksTracking",
            fields=[
                (
                    "id",
                    model_utils.fields.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("first_email_at", models.DateTimeField(blank=True, null=True)),
                ("last_reminder_at", models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="TicketAddIndividualDetails",
            fields=[
                (
                    "id",
                    model_utils.fields.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("approve_status", models.BooleanField(default=False)),
                ("individual_data", models.JSONField(blank=True, null=True)),
            ],
            options={
                "verbose_name_plural": "Ticket Add Individual Details",
            },
        ),
        migrations.CreateModel(
            name="TicketComplaintDetails",
            fields=[
                (
                    "id",
                    model_utils.fields.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name_plural": "Ticket Complaint Details",
            },
        ),
        migrations.CreateModel(
            name="TicketDeleteHouseholdDetails",
            fields=[
                (
                    "id",
                    model_utils.fields.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("approve_status", models.BooleanField(default=False)),
                ("role_reassign_data", models.JSONField(blank=True, default=dict)),
            ],
            options={
                "verbose_name_plural": "Ticket Delete Household Details",
            },
        ),
        migrations.CreateModel(
            name="TicketDeleteIndividualDetails",
            fields=[
                (
                    "id",
                    model_utils.fields.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("approve_status", models.BooleanField(default=False)),
                ("role_reassign_data", models.JSONField(blank=True, default=dict)),
            ],
            options={
                "verbose_name_plural": "Ticket Delete Individual Details",
            },
        ),
        migrations.CreateModel(
            name="TicketHouseholdDataUpdateDetails",
            fields=[
                (
                    "id",
                    model_utils.fields.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("household_data", models.JSONField(blank=True, null=True)),
            ],
            options={
                "verbose_name_plural": "Ticket Household Data Update Details",
            },
        ),
        migrations.CreateModel(
            name="TicketIndividualDataUpdateDetails",
            fields=[
                (
                    "id",
                    model_utils.fields.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("individual_data", models.JSONField(blank=True, null=True)),
            ],
            options={
                "verbose_name_plural": "Ticket Individual Data Update Details",
            },
        ),
        migrations.CreateModel(
            name="TicketNeedsAdjudicationDetails",
            fields=[
                (
                    "id",
                    model_utils.fields.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("score_min", models.FloatField(default=0.0)),
                ("score_max", models.FloatField(default=0.0)),
                ("is_multiple_duplicates_version", models.BooleanField(default=False)),
                ("is_cross_area", models.BooleanField(default=False)),
                ("role_reassign_data", models.JSONField(blank=True, default=dict)),
                ("extra_data", models.JSONField(blank=True, default=dict)),
            ],
            options={
                "verbose_name_plural": "Ticket Needs Adjudication Details",
            },
        ),
        migrations.CreateModel(
            name="TicketNegativeFeedbackDetails",
            fields=[
                (
                    "id",
                    model_utils.fields.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name_plural": "Ticket Negative Feedback Details",
            },
        ),
        migrations.CreateModel(
            name="TicketNote",
            fields=[
                (
                    "id",
                    model_utils.fields.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "description",
                    models.TextField(
                        help_text="The content of the customers query.",
                        verbose_name="Description",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="TicketPaymentVerificationDetails",
            fields=[
                (
                    "id",
                    model_utils.fields.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "payment_verification_status",
                    models.CharField(
                        choices=hope.models.payment_verification.get_status_choices,
                        max_length=50,
                    ),
                ),
                (
                    "new_status",
                    models.CharField(
                        blank=True,
                        choices=hope.models.payment_verification.get_status_choices,
                        default=None,
                        max_length=50,
                        null=True,
                    ),
                ),
                (
                    "old_received_amount",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        max_digits=15,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(Decimal("0.01"))],
                    ),
                ),
                (
                    "new_received_amount",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        max_digits=15,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(Decimal("0.01"))],
                    ),
                ),
                ("approve_status", models.BooleanField(default=False)),
            ],
            options={
                "verbose_name_plural": "Ticket Payment Verification Details",
            },
        ),
        migrations.CreateModel(
            name="TicketPositiveFeedbackDetails",
            fields=[
                (
                    "id",
                    model_utils.fields.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name_plural": "Ticket Positive Feedback Details",
            },
        ),
        migrations.CreateModel(
            name="TicketReferralDetails",
            fields=[
                (
                    "id",
                    model_utils.fields.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name_plural": "Ticket Referral Details",
            },
        ),
        migrations.CreateModel(
            name="TicketSeen",
            fields=[
                (
                    "id",
                    model_utils.fields.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("seen_at", models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name="TicketSensitiveDetails",
            fields=[
                (
                    "id",
                    model_utils.fields.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name_plural": "Ticket Sensitive Details",
            },
        ),
        migrations.CreateModel(
            name="TicketSystemFlaggingDetails",
            fields=[
                (
                    "id",
                    model_utils.fields.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("approve_status", models.BooleanField(default=False)),
                ("role_reassign_data", models.JSONField(blank=True, default=dict)),
            ],
            options={
                "verbose_name_plural": "Ticket System Flagging Details",
            },
        ),
        migrations.CreateModel(
            name="GrievanceDocument",
            fields=[
                (
                    "id",
                    model_utils.fields.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(blank=True, max_length=100, null=True)),
                (
                    "file",
                    models.FileField(
                        blank=True,
                        null=True,
                        upload_to="",
                    ),
                ),
                ("content_type", models.CharField(max_length=100)),
                ("file_size", models.IntegerField(blank=True, null=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="GrievanceTicket",
            fields=[
                (
                    "id",
                    model_utils.fields.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "version",
                    concurrency.fields.IntegerVersionField(default=0, help_text="record revision number"),
                ),
                ("unicef_id", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "household_unicef_id",
                    models.CharField(blank=True, max_length=250, null=True),
                ),
                (
                    "priority",
                    models.IntegerField(
                        choices=hope.apps.grievance.constants.get_priority_choices,
                        default=0,
                        verbose_name="Priority",
                    ),
                ),
                (
                    "urgency",
                    models.IntegerField(
                        choices=hope.apps.grievance.constants.get_urgency_choices,
                        default=0,
                        verbose_name="Urgency",
                    ),
                ),
                (
                    "category",
                    models.IntegerField(
                        choices=hope.apps.grievance.models.get_grievance_category_choices,
                        verbose_name="Category",
                    ),
                ),
                (
                    "issue_type",
                    models.IntegerField(blank=True, null=True, verbose_name="Type"),
                ),
                (
                    "submission_channel",
                    models.IntegerField(
                        blank=True,
                        choices=hope.apps.grievance.constants.get_submission_channel_choices,
                        help_text="Submission channel; empty for system-generated tickets.",
                        null=True,
                        verbose_name="Submission Channel",
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        help_text="The content of the customers query.",
                        verbose_name="Description",
                    ),
                ),
                (
                    "status",
                    models.IntegerField(
                        choices=hope.apps.grievance.models.get_grievance_status_choices,
                        default=1,
                        verbose_name="Status",
                    ),
                ),
                ("area", models.CharField(blank=True, max_length=250)),
                ("language", models.TextField(blank=True)),
                ("consent", models.BooleanField(default=True)),
                ("ignored", models.BooleanField(default=False)),
                ("extras", models.JSONField(blank=True, default=dict)),
                ("comments", models.TextField(blank=True, null=True)),
                (
                    "user_modified",
                    models.DateTimeField(
                        blank=True,
                        help_text="Date this ticket was most recently changed.",
                        null=True,
                        verbose_name="Modified",
                    ),
                ),
                (
                    "assigned_at",
                    models.DateTimeField(
                        blank=True,
                        help_text="When the assignee of this ticket last changed.",
                        null=True,
                        verbose_name="Assignee changed at",
                    ),
                ),
                (
                    "admin2",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="geo.area",
                    ),
                ),
                (
                    "assigned_by",
                    models.ForeignKey(
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
                (
                    "assigned_to",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="assigned_tickets",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Assigned to",
                    ),
                ),
                (
                    "business_area",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tickets",
                        to="core.businessarea",
                    ),
                ),
                (
                    "copied_from",
                    models.ForeignKey(
                        blank=True,
                        help_text="If this object was copied from another, this field will contain the object it was copied from.",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="copied_to",
                        to="grievance.grievanceticket",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="created_tickets",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Created by",
                    ),
                ),
                (
                    "partner",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="account.partner",
                    ),
                ),
            ],
            options={
                "verbose_name": "Grievance Ticket",
                "ordering": ("status", "created_at"),
            },
            bases=(hope.models.utils.AdminUrlMixin, models.Model),
        ),
    ]
