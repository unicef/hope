import uuid

from django.db import migrations, models
import django.db.models.deletion
import model_utils.fields
import mptt.fields

import hope.models.utils


class Migration(migrations.Migration):
    initial = True

    replaces = [
        ("geo", "0001_migration"),
        ("geo", "0002_migration"),
        ("geo", "0003_migration"),
        ("geo", "0004_migration"),
        ("geo", "0005_migration"),
        ("geo", "0006_migration"),
        ("geo", "0007_migration"),
        ("geo", "0008_migration"),
        ("geo", "0009_migration"),
    ]

    dependencies = [
        ("core", "0044_baseline_models"),
    ]

    operations = [
        migrations.RunSQL(
            sql="CREATE COLLATION IF NOT EXISTS \"und-ci-det\" (provider = icu, locale = 'und-u-ks-level2', deterministic = true);",
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.CreateModel(
            name="Country",
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
                ("original_id", models.UUIDField(blank=True, null=True)),
                (
                    "name",
                    models.CharField(
                        db_collation="und-ci-det",
                        help_text="The full name of the country",
                        max_length=255,
                    ),
                ),
                (
                    "short_name",
                    models.CharField(
                        db_collation="und-ci-det",
                        help_text="The short name of the country",
                        max_length=255,
                    ),
                ),
                (
                    "iso_code2",
                    models.CharField(
                        help_text="The ISO 3166-1 alpha-2 code",
                        max_length=2,
                        unique=True,
                    ),
                ),
                (
                    "iso_code3",
                    models.CharField(
                        help_text="The ISO 3166-1 alpha-3 code",
                        max_length=3,
                        unique=True,
                    ),
                ),
                (
                    "iso_num",
                    models.CharField(
                        help_text="The ISO 3166-1 numeric code",
                        max_length=4,
                        unique=True,
                    ),
                ),
                (
                    "valid_from",
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text="The date from which this record is valid",
                        null=True,
                    ),
                ),
                (
                    "valid_until",
                    models.DateTimeField(
                        blank=True,
                        help_text="The date until which this record is valid",
                        null=True,
                    ),
                ),
                (
                    "extras",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        help_text="Extra data for this country",
                    ),
                ),
                ("lft", models.PositiveIntegerField(editable=False)),
                ("rght", models.PositiveIntegerField(editable=False)),
                ("tree_id", models.PositiveIntegerField(db_index=True, editable=False)),
                ("level", models.PositiveIntegerField(editable=False)),
                (
                    "currency",
                    models.ForeignKey(
                        blank=True,
                        help_text="The currency used in this country",
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="countries",
                        to="core.currency",
                        verbose_name="Currency",
                    ),
                ),
                (
                    "parent",
                    mptt.fields.TreeForeignKey(
                        blank=True,
                        help_text="The parent area in the hierarchy",
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="children",
                        to="geo.country",
                        verbose_name="Parent",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Countries",
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="AreaType",
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
                ("original_id", models.UUIDField(blank=True, null=True)),
                ("name", models.CharField(db_collation="und-ci-det", max_length=255)),
                ("area_level", models.PositiveIntegerField(default=1)),
                ("valid_from", models.DateTimeField(auto_now_add=True, null=True)),
                ("valid_until", models.DateTimeField(blank=True, null=True)),
                ("extras", models.JSONField(blank=True, default=dict)),
                ("lft", models.PositiveIntegerField(editable=False)),
                ("rght", models.PositiveIntegerField(editable=False)),
                ("tree_id", models.PositiveIntegerField(db_index=True, editable=False)),
                ("level", models.PositiveIntegerField(editable=False)),
                (
                    "parent",
                    mptt.fields.TreeForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="geo.areatype",
                        verbose_name="Parent",
                    ),
                ),
                (
                    "country",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="geo.country"),
                ),
            ],
            options={
                "verbose_name_plural": "Area Types",
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="Area",
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
                ("original_id", models.UUIDField(blank=True, null=True)),
                ("name", models.CharField(max_length=255)),
                (
                    "p_code",
                    models.CharField(blank=True, max_length=32, null=True, verbose_name="P Code"),
                ),
                ("longitude", models.FloatField(blank=True, null=True)),
                ("latitude", models.FloatField(blank=True, null=True)),
                ("valid_from", models.DateTimeField(auto_now_add=True, null=True)),
                ("valid_until", models.DateTimeField(blank=True, null=True)),
                ("extras", models.JSONField(blank=True, default=dict)),
                ("lft", models.PositiveIntegerField(editable=False)),
                ("rght", models.PositiveIntegerField(editable=False)),
                ("tree_id", models.PositiveIntegerField(db_index=True, editable=False)),
                ("level", models.PositiveIntegerField(editable=False)),
                (
                    "parent",
                    mptt.fields.TreeForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="geo.area",
                        verbose_name="Parent",
                    ),
                ),
                (
                    "area_type",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="geo.areatype"),
                ),
            ],
            options={
                "verbose_name_plural": "Areas",
                "ordering": ("name",),
                "permissions": (("import_areas", "Can import areas"),),
                "indexes": [
                    hope.models.utils.LongNameIndex(fields=["created_at"], name="geo_area_created_at_3f07c235"),
                    hope.models.utils.LongNameIndex(fields=["updated_at"], name="geo_area_updated_at_7ec5b7d0"),
                    models.Index(fields=["tree_id", "lft"], name="geo_area_tree_id_lft_idx"),
                ],
                "constraints": [
                    models.UniqueConstraint(
                        condition=models.Q(("p_code", ""), _negated=True),
                        fields=("p_code",),
                        name="unique_area_p_code_not_blank",
                    )
                ],
            },
        ),
        migrations.AddIndex(
            model_name="country",
            index=hope.models.utils.LongNameIndex(fields=["created_at"], name="geo_country_created_at_afcd5bea"),
        ),
        migrations.AddIndex(
            model_name="country",
            index=hope.models.utils.LongNameIndex(fields=["updated_at"], name="geo_country_updated_at_daf4b47f"),
        ),
        migrations.AddIndex(
            model_name="country",
            index=hope.models.utils.LongNameIndex(fields=["name"], name="geo_country_name_01731269"),
        ),
        migrations.AddIndex(
            model_name="country",
            index=hope.models.utils.LongNameIndex(fields=["short_name"], name="geo_country_short_name_00190511"),
        ),
        migrations.AddIndex(
            model_name="country",
            index=models.Index(fields=["tree_id", "lft"], name="geo_country_tree_id_lft_idx"),
        ),
        migrations.AddIndex(
            model_name="areatype",
            index=hope.models.utils.LongNameIndex(fields=["created_at"], name="geo_areatype_created_at_7ce454f0"),
        ),
        migrations.AddIndex(
            model_name="areatype",
            index=hope.models.utils.LongNameIndex(fields=["updated_at"], name="geo_areatype_updated_at_6c355284"),
        ),
        migrations.AddIndex(
            model_name="areatype",
            index=hope.models.utils.LongNameIndex(fields=["name"], name="geo_areatype_name_b20b6ba6"),
        ),
        migrations.AddIndex(
            model_name="areatype",
            index=models.Index(fields=["tree_id", "lft"], name="geo_areatype_tree_id_lft_idx"),
        ),
        migrations.AlterUniqueTogether(
            name="areatype",
            unique_together={("country", "area_level", "name")},
        ),
    ]
