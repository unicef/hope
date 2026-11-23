import uuid

from django.db import migrations, models
import django.db.models.deletion
import model_utils.fields
import strategy_field.fields

import hope.apps.core.upload_paths
import hope.models.utils


class Migration(migrations.Migration):
    initial = True

    replaces = [
        ("sanction_list", "0001_migration"),
        ("sanction_list", "0002_migration"),
        ("sanction_list", "0003_migration"),
        ("sanction_list", "0004_migration"),
        ("sanction_list", "0005_migration"),
        ("sanction_list", "0006_migration"),
        ("sanction_list", "0007_migration"),
        ("sanction_list", "0008_migration"),
        ("sanction_list", "0009_migration"),
    ]

    dependencies = [
        ("geo", "0010_baseline_models"),
    ]

    operations = [
        migrations.CreateModel(
            name="SanctionList",
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
                ("name", models.CharField(max_length=255)),
                ("config", models.JSONField(blank=True, default=dict)),
                ("strategy", strategy_field.fields.StrategyField(unique=True)),
            ],
            options={
                "ordering": ["name"],
                "permissions": (
                    ("refresh_sanction_list", "Can Refresh Sanction List"),
                    ("empty_sanction_list", "Can Empty Sanction List"),
                ),
                "indexes": [
                    hope.models.utils.LongNameIndex(
                        fields=["created_at"],
                        name="sanction_list_sanctionlist_created_at_116e1da0",
                    ),
                    hope.models.utils.LongNameIndex(
                        fields=["updated_at"],
                        name="sanction_list_sanctionlist_updated_at_2ecc22f2",
                    ),
                ],
            },
        ),
        migrations.CreateModel(
            name="SanctionListIndividual",
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
                ("internal_data", models.JSONField(blank=True, default=dict)),
                ("first_name", models.CharField(max_length=85)),
                (
                    "second_name",
                    models.CharField(blank=True, default="", max_length=85),
                ),
                ("third_name", models.CharField(blank=True, default="", max_length=85)),
                (
                    "fourth_name",
                    models.CharField(blank=True, default="", max_length=85),
                ),
                ("full_name", models.CharField(max_length=255)),
                (
                    "name_original_script",
                    models.CharField(blank=True, default="", max_length=255),
                ),
                ("list_type", models.CharField(max_length=50)),
                (
                    "un_list_type",
                    models.CharField(blank=True, default="", max_length=100),
                ),
                ("reference_number", models.CharField(max_length=50)),
                ("listed_on", models.DateTimeField(blank=True, null=True)),
                ("comments", models.TextField(blank=True, default="")),
                ("designation", models.TextField(blank=True, default="")),
                ("street", models.CharField(blank=True, default="", max_length=255)),
                ("city", models.CharField(blank=True, default="", max_length=255)),
                (
                    "state_province",
                    models.CharField(blank=True, default="", max_length=255),
                ),
                (
                    "address_note",
                    models.CharField(blank=True, default="", max_length=255),
                ),
                ("data_id", models.PositiveIntegerField()),
                ("version_num", models.PositiveIntegerField()),
                ("active", models.BooleanField(default=True)),
                (
                    "country_of_birth",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="geo.country",
                    ),
                ),
                (
                    "sanction_list",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="entries",
                        to="sanction_list.sanctionlist",
                    ),
                ),
            ],
            options={
                "verbose_name": "Individual",
                "verbose_name_plural": "Individuals",
                "ordering": ["-listed_on"],
            },
        ),
        migrations.CreateModel(
            name="SanctionListIndividualAliasName",
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
                ("name", models.CharField(max_length=255)),
                (
                    "individual",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="alias_names",
                        to="sanction_list.sanctionlistindividual",
                    ),
                ),
            ],
            options={
                "verbose_name": "Alias",
                "verbose_name_plural": "Aliases",
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="SanctionListIndividualCountries",
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
                    "country",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="geo.country",
                    ),
                ),
                (
                    "individual",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="countries",
                        to="sanction_list.sanctionlistindividual",
                    ),
                ),
            ],
            options={
                "verbose_name": "Sanction List Individual/Country",
                "verbose_name_plural": "Sanction List Individual/Countries",
                "ordering": ("id",),
            },
        ),
        migrations.CreateModel(
            name="SanctionListIndividualDateOfBirth",
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
                ("date", models.DateField()),
                (
                    "individual",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="dates_of_birth",
                        to="sanction_list.sanctionlistindividual",
                    ),
                ),
            ],
            options={
                "verbose_name": "Birthday",
                "ordering": ("-created_at",),
            },
        ),
        migrations.CreateModel(
            name="SanctionListIndividualDocument",
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
                ("type_of_document", models.CharField(max_length=255)),
                ("document_number", models.CharField(max_length=255)),
                (
                    "date_of_issue",
                    models.CharField(blank=True, default="", max_length=255, null=True),
                ),
                ("note", models.CharField(blank=True, default="", max_length=255)),
                (
                    "individual",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="documents",
                        to="sanction_list.sanctionlistindividual",
                    ),
                ),
                (
                    "issuing_country",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="geo.country",
                    ),
                ),
            ],
            options={
                "verbose_name": "Document",
                "verbose_name_plural": "Documents",
                "ordering": ("id",),
            },
        ),
        migrations.CreateModel(
            name="SanctionListIndividualNationalities",
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
                    "individual",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="nationalities",
                        to="sanction_list.sanctionlistindividual",
                    ),
                ),
                (
                    "nationality",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="geo.country",
                    ),
                ),
            ],
            options={
                "verbose_name": "Nationality",
                "verbose_name_plural": "Nationalities",
                "ordering": ("id",),
            },
        ),
        migrations.CreateModel(
            name="UploadedXLSXFile",
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
                    "file",
                    models.FileField(
                        max_length=255,
                        upload_to=hope.apps.core.upload_paths.upload_path,
                    ),
                ),
                ("associated_email", models.EmailField(max_length=254)),
                (
                    "selected_lists",
                    models.ManyToManyField(to="sanction_list.sanctionlist"),
                ),
            ],
        ),
        migrations.AddIndex(
            model_name="sanctionlistindividual",
            index=hope.models.utils.LongNameIndex(
                fields=["created_at"],
                name="sanction_list_sanctionlistindividual_created_at_50b73670",
            ),
        ),
        migrations.AddIndex(
            model_name="sanctionlistindividual",
            index=hope.models.utils.LongNameIndex(
                fields=["updated_at"],
                name="sanction_list_sanctionlistindividual_updated_at_a42a9b36",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="sanctionlistindividual",
            unique_together={("sanction_list", "reference_number")},
        ),
        migrations.AddIndex(
            model_name="sanctionlistindividualaliasname",
            index=hope.models.utils.LongNameIndex(
                fields=["created_at"],
                name="sanction_list_sanctionlist_created_at_f103fe15",
            ),
        ),
        migrations.AddIndex(
            model_name="sanctionlistindividualaliasname",
            index=hope.models.utils.LongNameIndex(
                fields=["updated_at"],
                name="sanction_list_sanctionlist_updated_at_c863d190",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="sanctionlistindividualaliasname",
            unique_together={("individual", "name")},
        ),
        migrations.AddIndex(
            model_name="sanctionlistindividualcountries",
            index=hope.models.utils.LongNameIndex(
                fields=["created_at"],
                name="sanction_list_sanctionlist_created_at_b4a02be4",
            ),
        ),
        migrations.AddIndex(
            model_name="sanctionlistindividualcountries",
            index=hope.models.utils.LongNameIndex(
                fields=["updated_at"],
                name="sanction_list_sanctionlist_updated_at_a6c935f2",
            ),
        ),
        migrations.AddIndex(
            model_name="sanctionlistindividualdateofbirth",
            index=hope.models.utils.LongNameIndex(
                fields=["created_at"],
                name="sanction_list_sanctionlist_created_at_fe1aae1c",
            ),
        ),
        migrations.AddIndex(
            model_name="sanctionlistindividualdateofbirth",
            index=hope.models.utils.LongNameIndex(
                fields=["updated_at"],
                name="sanction_list_sanctionlist_updated_at_b0324dfd",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="sanctionlistindividualdateofbirth",
            unique_together={("individual", "date")},
        ),
        migrations.AddIndex(
            model_name="sanctionlistindividualdocument",
            index=hope.models.utils.LongNameIndex(
                fields=["created_at"],
                name="sanction_list_sanctionlist_created_at_412c7655",
            ),
        ),
        migrations.AddIndex(
            model_name="sanctionlistindividualdocument",
            index=hope.models.utils.LongNameIndex(
                fields=["updated_at"],
                name="sanction_list_sanctionlist_updated_at_2cb780b5",
            ),
        ),
        migrations.AddIndex(
            model_name="sanctionlistindividualnationalities",
            index=hope.models.utils.LongNameIndex(
                fields=["created_at"],
                name="sanction_list_sanctionlist_created_at_6f9dffc3",
            ),
        ),
        migrations.AddIndex(
            model_name="sanctionlistindividualnationalities",
            index=hope.models.utils.LongNameIndex(
                fields=["updated_at"],
                name="sanction_list_sanctionlist_updated_at_330fb903",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="sanctionlistindividualnationalities",
            unique_together={("individual", "nationality")},
        ),
        migrations.AddIndex(
            model_name="uploadedxlsxfile",
            index=hope.models.utils.LongNameIndex(
                fields=["created_at"],
                name="sanction_list_uploadedxlsxfile_created_at_3bb5c1e7",
            ),
        ),
        migrations.AddIndex(
            model_name="uploadedxlsxfile",
            index=hope.models.utils.LongNameIndex(
                fields=["updated_at"],
                name="sanction_list_uploadedxlsxfile_updated_at_6c0e45cf",
            ),
        ),
    ]
