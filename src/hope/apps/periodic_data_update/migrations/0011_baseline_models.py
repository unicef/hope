from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion

import hope.apps.core.upload_paths
import hope.models.pdu_online_edit
import hope.models.pdu_xlsx_template
import hope.models.pdu_xlsx_upload
import hope.models.utils


class Migration(migrations.Migration):
    initial = True

    replaces = [
        ("periodic_data_update", "0001_migration"),
        ("periodic_data_update", "0002_migration"),
        ("periodic_data_update", "0003_migration"),
        ("periodic_data_update", "0004_migration"),
        ("periodic_data_update", "0005_migration"),
        ("periodic_data_update", "0006_migration"),
        ("periodic_data_update", "0007_migration"),
        ("periodic_data_update", "0008_migration"),
        ("periodic_data_update", "0009_migration"),
        ("periodic_data_update", "0010_migration"),
    ]

    dependencies = [
        ("core", "0044_baseline_models"),
        ("program", "0027_baseline_models"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="PDUOnlineEdit",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "name",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        validators=[
                            django.core.validators.MinLengthValidator(3),
                            django.core.validators.MaxLengthValidator(255),
                            django.core.validators.RegexValidator(
                                "\\s{2,}",
                                "Double spaces characters are not allowed.",
                                code="double_spaces_characters_not_allowed",
                                inverse_match=True,
                            ),
                            django.core.validators.RegexValidator(
                                "(^\\s+)|(\\s+$)",
                                "Leading or trailing spaces characters are not allowed.",
                                code="leading_trailing_spaces_characters_not_allowed",
                                inverse_match=True,
                            ),
                            django.core.validators.ProhibitNullCharactersValidator(),
                        ],
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=hope.models.pdu_online_edit.PDUOnlineEdit.Status.get_choices,
                        default="PENDING_CREATE",
                        max_length=20,
                    ),
                ),
                ("approved_at", models.DateTimeField(blank=True, null=True)),
                ("edit_data", models.JSONField(blank=True, default=dict)),
                (
                    "number_of_records",
                    models.PositiveIntegerField(blank=True, null=True),
                ),
                (
                    "approved_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="pdu_online_edits_approved",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "authorized_users",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Users who are authorized to perform actions on this periodic data update",
                        related_name="authorized_pdu_online_edits",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "business_area",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="pdu_online_edits",
                        to="core.businessarea",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="pdu_online_edits_created",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "program",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="pdu_online_edits",
                        to="program.program",
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
            },
            bases=(hope.models.utils.AdminUrlMixin, models.Model),
        ),
        migrations.CreateModel(
            name="PDUOnlineEditSentBackComment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("comment", models.TextField()),
                (
                    "created_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="sent_back_comments",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "pdu_online_edit",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sent_back_comment",
                        to="periodic_data_update.pduonlineedit",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="PDUXlsxTemplate",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "name",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        validators=[
                            django.core.validators.MinLengthValidator(3),
                            django.core.validators.MaxLengthValidator(255),
                            django.core.validators.RegexValidator(
                                "\\s{2,}",
                                "Double spaces characters are not allowed.",
                                code="double_spaces_characters_not_allowed",
                                inverse_match=True,
                            ),
                            django.core.validators.RegexValidator(
                                "(^\\s+)|(\\s+$)",
                                "Leading or trailing spaces characters are not allowed.",
                                code="leading_trailing_spaces_characters_not_allowed",
                                inverse_match=True,
                            ),
                            django.core.validators.ProhibitNullCharactersValidator(),
                        ],
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=hope.models.pdu_xlsx_template.PDUXlsxTemplate.Status.get_choices,
                        default="TO_EXPORT",
                        max_length=20,
                    ),
                ),
                (
                    "number_of_records",
                    models.PositiveIntegerField(blank=True, null=True),
                ),
                ("filters", models.JSONField(blank=True, default=dict, null=True)),
                ("rounds_data", models.JSONField()),
                (
                    "business_area",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="pdu_xlsx_templates",
                        to="core.businessarea",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="pdu_xlsx_templates_created",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "file",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="core.filetemp",
                    ),
                ),
                (
                    "program",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="pdu_xlsx_templates",
                        to="program.program",
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
                "permissions": (("restart_export_task", "Can restart export task"),),
            },
            bases=(models.Model, hope.models.utils.AdminUrlMixin),
        ),
        migrations.CreateModel(
            name="PDUXlsxUpload",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "status",
                    models.CharField(
                        choices=hope.models.pdu_xlsx_upload.PDUXlsxUpload.Status.get_choices,
                        default="PENDING",
                        max_length=20,
                    ),
                ),
                (
                    "file",
                    models.FileField(
                        max_length=255,
                        upload_to=hope.apps.core.upload_paths.upload_path,
                    ),
                ),
                ("error_message", models.TextField(blank=True, null=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="pdu_uploads",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "template",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="uploads",
                        to="periodic_data_update.pduxlsxtemplate",
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
            },
        ),
        migrations.AddIndex(
            model_name="pduonlineedit",
            index=hope.models.utils.LongNameIndex(
                fields=["created_at"],
                name="periodic_data_update_pduonlineedit_created_at_cbf512a8",
            ),
        ),
        migrations.AddIndex(
            model_name="pduonlineedit",
            index=hope.models.utils.LongNameIndex(
                fields=["updated_at"],
                name="periodic_data_update_pduonlineedit_updated_at_416e7971",
            ),
        ),
        migrations.AddConstraint(
            model_name="pduonlineedit",
            constraint=models.UniqueConstraint(fields=("name", "program"), name="pdu_online_name_unique_per_program"),
        ),
        migrations.AddIndex(
            model_name="pduonlineeditsentbackcomment",
            index=hope.models.utils.LongNameIndex(
                fields=["created_at"],
                name="periodic_data_update_pduon_created_at_b2b09a3c",
            ),
        ),
        migrations.AddIndex(
            model_name="pduonlineeditsentbackcomment",
            index=hope.models.utils.LongNameIndex(
                fields=["updated_at"],
                name="periodic_data_update_pduon_updated_at_e57014b4",
            ),
        ),
        migrations.AddIndex(
            model_name="pduxlsxtemplate",
            index=hope.models.utils.LongNameIndex(
                fields=["created_at"],
                name="periodic_data_update_pduxlsxtemplate_created_at_0ed2662a",
            ),
        ),
        migrations.AddIndex(
            model_name="pduxlsxtemplate",
            index=hope.models.utils.LongNameIndex(
                fields=["updated_at"],
                name="periodic_data_update_pduxlsxtemplate_updated_at_e370f5c5",
            ),
        ),
        migrations.AddConstraint(
            model_name="pduxlsxtemplate",
            constraint=models.UniqueConstraint(
                fields=("name", "program"),
                name="pdu_xlsx_template_name_unique_per_program",
            ),
        ),
        migrations.AddIndex(
            model_name="pduxlsxupload",
            index=hope.models.utils.LongNameIndex(
                fields=["created_at"],
                name="periodic_data_update_pduxlsxupload_created_at_5ad6c4ee",
            ),
        ),
        migrations.AddIndex(
            model_name="pduxlsxupload",
            index=hope.models.utils.LongNameIndex(
                fields=["updated_at"],
                name="periodic_data_update_pduxlsxupload_updated_at_fa057243",
            ),
        ),
    ]
