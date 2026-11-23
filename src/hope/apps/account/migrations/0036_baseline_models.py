import uuid

import django.contrib.auth.models
import django.contrib.auth.validators
import django.core.validators
from django.db import migrations, models
import django.db.models.manager
import django.utils.timezone
import model_utils.fields
import timezone_field.fields

import hope.apps.account.fields
import hope.apps.account.permissions
import hope.models.user


class Migration(migrations.Migration):
    initial = True

    replaces = [
        ("account", "0003_migration"),
        ("account", "0004_migration"),
        ("account", "0005_migration"),
        ("account", "0006_migration"),
        ("account", "0007_migration"),
        ("account", "0008_migration"),
        ("account", "0009_migration"),
        ("account", "0010_migration"),
        ("account", "0011_migration"),
        ("account", "0012_migration"),
        ("account", "0013_migration"),
        ("account", "0014_add_partial_indexes"),
        ("account", "0015_migration"),
        ("account", "0016_migration"),
        ("account", "0017_migration"),
        ("account", "0018_migration"),
        ("account", "0019_migration"),
        ("account", "0020_migration"),
        ("account", "0021_migration"),
        ("account", "0022_migration"),
        ("account", "0023_migration"),
        ("account", "0024_migration"),
        ("account", "0025_migration"),
        ("account", "0026_migration"),
        ("account", "0027_migration"),
        ("account", "0028_migration"),
        ("account", "0029_migration"),
        ("account", "0030_migration"),
        ("account", "0031_migration"),
        ("account", "0032_migration"),
        ("account", "0033_migration"),
        ("account", "0034_migration"),
        ("account", "0035_migration"),
    ]

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.RunSQL(sql="CREATE EXTENSION IF NOT EXISTS citext;", reverse_sql=migrations.RunSQL.noop),
        migrations.RunSQL(
            sql="CREATE COLLATION IF NOT EXISTS \"und-ci-det\" (provider = icu, locale = 'und-u-ks-level2', deterministic = true);",
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.CreateModel(
            name="AdminAreaLimitedTo",
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
                "ordering": ("id",),
            },
        ),
        migrations.CreateModel(
            name="IncompatibleRoles",
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
                "verbose_name": "incompatible roles",
                "verbose_name_plural": "incompatible roles",
                "ordering": ("id",),
            },
        ),
        migrations.CreateModel(
            name="Partner",
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
                (
                    "name",
                    models.CharField(db_collation="und-ci-det", max_length=100, unique=True),
                ),
                ("is_un", models.BooleanField(default=False, verbose_name="U.N.")),
                ("lft", models.PositiveIntegerField(editable=False)),
                ("rght", models.PositiveIntegerField(editable=False)),
                ("tree_id", models.PositiveIntegerField(db_index=True, editable=False)),
                ("level", models.PositiveIntegerField(editable=False)),
            ],
            options={
                "ordering": ("id",),
            },
            managers=[
                ("_tree_manager", django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name="Role",
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
                    "name",
                    models.CharField(
                        max_length=250,
                        unique=True,
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
                    "permissions",
                    hope.apps.account.fields.ChoiceArrayField(
                        base_field=models.CharField(
                            choices=hope.apps.account.permissions.Permissions.choices,
                            max_length=255,
                        ),
                        blank=True,
                        null=True,
                        size=None,
                    ),
                ),
                ("is_visible_on_ui", models.BooleanField(default=True)),
                ("is_available_for_partner", models.BooleanField(default=True)),
            ],
            options={
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="RoleAssignment",
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
                    "expiry_date",
                    models.DateField(
                        blank=True,
                        help_text="After expiry date this Role Assignment will be inactive.",
                        null=True,
                    ),
                ),
            ],
            options={
                "ordering": ("id",),
            },
        ),
        migrations.CreateModel(
            name="UserGroup",
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
            ],
            options={
                "ordering": ("id",),
            },
        ),
        migrations.CreateModel(
            name="User",
            fields=[
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(blank=True, null=True, verbose_name="last login"),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        error_messages={"unique": "A user with that username already exists."},
                        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
                        max_length=150,
                        unique=True,
                        validators=[django.contrib.auth.validators.UnicodeUsernameValidator()],
                        verbose_name="username",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(blank=True, max_length=150, verbose_name="first name"),
                ),
                (
                    "last_name",
                    models.CharField(blank=True, max_length=150, verbose_name="last name"),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(default=django.utils.timezone.now, verbose_name="date joined"),
                ),
                ("azure_id", models.UUIDField(blank=True, null=True, unique=True)),
                (
                    "display_name",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                (
                    "id",
                    model_utils.fields.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=hope.models.user.get_user_status_choices,
                        default="INVITED",
                        max_length=10,
                    ),
                ),
                (
                    "email",
                    models.EmailField(max_length=254, unique=True, verbose_name="email address"),
                ),
                ("custom_fields", models.JSONField(blank=True, default=dict)),
                ("job_title", models.CharField(blank=True, max_length=255)),
                (
                    "timezone",
                    timezone_field.fields.TimeZoneField(blank=True, null=True),
                ),
                ("last_modify_date", models.DateTimeField(auto_now=True, null=True)),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "ordering": ("id",),
                "permissions": (
                    ("can_load_from_ad", "Can load users from ActiveDirectory"),
                    ("can_sync_with_ad", "Can synchronise user with ActiveDirectory"),
                    ("can_debug", "Can access debug information"),
                    ("can_inspect", "Can inspect objects"),
                    ("quick_links", "Can see quick links in admin"),
                    ("restrict_help_desk", "Limit fields to be editable for help desk"),
                    ("can_reindex_programs", "Can reindex programs"),
                    (
                        "can_add_business_area_to_partner",
                        "Can add business area to partner",
                    ),
                    ("can_change_allowed_partners", "Can change allowed partners"),
                    ("can_change_area_limits", "Can change area limits"),
                    ("can_import_fixture", "Can import fixture"),
                    ("ad_users", "Can import AD users"),
                    ("can_upload_to_kobo", "Can upload CSV file to Kobo"),
                ),
            },
            managers=[
                ("objects", django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
