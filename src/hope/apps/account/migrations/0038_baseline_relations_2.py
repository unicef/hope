from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import mptt.fields

import hope.models.utils


class Migration(migrations.Migration):
    initial = True

    replaces = [
        ("account", "0002_migration"),
    ]

    dependencies = [
        ("account", "0037_baseline_relations"),
        ("auth", "0012_alter_user_first_name_max_length"),
        ("core", "0044_baseline_models"),
        ("program", "0027_baseline_models"),
    ]

    operations = [
        migrations.AddField(
            model_name="adminarealimitedto",
            name="program",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="admin_area_limits",
                to="program.program",
            ),
        ),
        migrations.AddField(
            model_name="partner",
            name="allowed_business_areas",
            field=models.ManyToManyField(blank=True, to="core.businessarea"),
        ),
        migrations.AddField(
            model_name="partner",
            name="parent",
            field=mptt.fields.TreeForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="account.partner",
                verbose_name="Parent",
            ),
        ),
        migrations.AddField(
            model_name="adminarealimitedto",
            name="partner",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="admin_area_limits",
                to="account.partner",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="partner",
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="account.partner"),
        ),
        migrations.AddIndex(
            model_name="role",
            index=hope.models.utils.LongNameIndex(fields=["created_at"], name="account_role_created_at_1453ec3c"),
        ),
        migrations.AddIndex(
            model_name="role",
            index=hope.models.utils.LongNameIndex(fields=["updated_at"], name="account_role_updated_at_d4087b83"),
        ),
        migrations.AddField(
            model_name="incompatibleroles",
            name="role_one",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="incompatible_roles_one",
                to="account.role",
            ),
        ),
        migrations.AddField(
            model_name="incompatibleroles",
            name="role_two",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="incompatible_roles_two",
                to="account.role",
            ),
        ),
        migrations.AddField(
            model_name="roleassignment",
            name="business_area",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="role_assignments",
                to="core.businessarea",
            ),
        ),
        migrations.AddField(
            model_name="roleassignment",
            name="group",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="role_assignments",
                to="auth.group",
            ),
        ),
        migrations.AddField(
            model_name="roleassignment",
            name="partner",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="role_assignments",
                to="account.partner",
            ),
        ),
        migrations.AddField(
            model_name="roleassignment",
            name="program",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="role_assignments",
                to="program.program",
            ),
        ),
        migrations.AddField(
            model_name="roleassignment",
            name="role",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="role_assignments",
                to="account.role",
            ),
        ),
        migrations.AddField(
            model_name="roleassignment",
            name="user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="role_assignments",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.CreateModel(
            name="PartnerRoleAssignment",
            fields=[],
            options={
                "verbose_name": "Role Assignment (Partner)",
                "verbose_name_plural": "Role Assignments (Partner)",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("account.roleassignment",),
        ),
        migrations.CreateModel(
            name="UserRoleAssignment",
            fields=[],
            options={
                "verbose_name": "Role Assignment (User)",
                "verbose_name_plural": "Role Assignments (User)",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("account.roleassignment",),
        ),
        migrations.AddField(
            model_name="usergroup",
            name="business_area",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="user_groups",
                to="core.businessarea",
            ),
        ),
        migrations.AddField(
            model_name="usergroup",
            name="group",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="user_groups",
                to="auth.group",
            ),
        ),
        migrations.AddField(
            model_name="usergroup",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="user_groups",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddIndex(
            model_name="adminarealimitedto",
            index=hope.models.utils.LongNameIndex(
                fields=["created_at"],
                name="account_adminarealimitedto_created_at_06b87506",
            ),
        ),
        migrations.AddIndex(
            model_name="adminarealimitedto",
            index=hope.models.utils.LongNameIndex(
                fields=["updated_at"],
                name="account_adminarealimitedto_updated_at_1c1ce965",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="adminarealimitedto",
            unique_together={("partner", "program")},
        ),
        migrations.AddIndex(
            model_name="user",
            index=models.Index(fields=["partner", "id"], name="idx_user_partner_id"),
        ),
        migrations.AddIndex(
            model_name="incompatibleroles",
            index=hope.models.utils.LongNameIndex(
                fields=["created_at"],
                name="account_incompatibleroles_created_at_7a423961",
            ),
        ),
        migrations.AddIndex(
            model_name="incompatibleroles",
            index=hope.models.utils.LongNameIndex(
                fields=["updated_at"],
                name="account_incompatibleroles_updated_at_aae9f2fb",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="incompatibleroles",
            unique_together={("role_one", "role_two")},
        ),
        migrations.AddIndex(
            model_name="roleassignment",
            index=models.Index(fields=["user", "expiry_date"], name="idx_ra_user_exp"),
        ),
        migrations.AddIndex(
            model_name="roleassignment",
            index=models.Index(
                fields=["partner", "business_area", "expiry_date"],
                name="idx_ra_partner_ba_exp",
            ),
        ),
        migrations.AddIndex(
            model_name="roleassignment",
            index=models.Index(fields=["business_area", "expiry_date"], name="idx_ra_ba_exp"),
        ),
        migrations.AddIndex(
            model_name="roleassignment",
            index=hope.models.utils.LongNameIndex(
                fields=["created_at"], name="account_roleassignment_created_at_78cf0c2d"
            ),
        ),
        migrations.AddIndex(
            model_name="roleassignment",
            index=hope.models.utils.LongNameIndex(
                fields=["updated_at"], name="account_roleassignment_updated_at_4738f268"
            ),
        ),
        migrations.AddConstraint(
            model_name="roleassignment",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    models.Q(("partner__isnull", True), ("user__isnull", False)),
                    models.Q(("partner__isnull", False), ("user__isnull", True)),
                    _connector="OR",
                ),
                name="user_or_partner_not_both",
            ),
        ),
        migrations.AddConstraint(
            model_name="roleassignment",
            constraint=models.UniqueConstraint(
                condition=models.Q(("user__isnull", False)),
                fields=("user", "role", "business_area", "program"),
                name="unique_user_role_business_area_program",
            ),
        ),
        migrations.AddConstraint(
            model_name="roleassignment",
            constraint=models.UniqueConstraint(
                condition=models.Q(("program__isnull", True), ("user__isnull", False)),
                fields=("user", "role", "business_area"),
                name="unique_user_role_business_area_no_program",
            ),
        ),
        migrations.AddConstraint(
            model_name="roleassignment",
            constraint=models.UniqueConstraint(
                condition=models.Q(("partner__isnull", False)),
                fields=("partner", "role", "business_area", "program"),
                name="unique_partner_role_business_area_program",
            ),
        ),
        migrations.AddConstraint(
            model_name="roleassignment",
            constraint=models.UniqueConstraint(
                condition=models.Q(("partner__isnull", False), ("program__isnull", True)),
                fields=("partner", "role", "business_area"),
                name="unique_partner_role_business_area_no_program",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="usergroup",
            unique_together={("business_area", "user", "group")},
        ),
    ]
