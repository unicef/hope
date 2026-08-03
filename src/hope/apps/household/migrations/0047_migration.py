from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("household", "0046_migration"),
    ]

    operations = [
        migrations.AddField(
            model_name="household",
            name="kab_female_age_group_0_5_count",
            field=models.PositiveIntegerField(
                blank=True, help_text="Known affected beneficiaries: females aged 0-5", null=True
            ),
        ),
        migrations.AddField(
            model_name="household",
            name="kab_female_age_group_6_11_count",
            field=models.PositiveIntegerField(
                blank=True, help_text="Known affected beneficiaries: females aged 6-11", null=True
            ),
        ),
        migrations.AddField(
            model_name="household",
            name="kab_female_age_group_12_17_count",
            field=models.PositiveIntegerField(
                blank=True, help_text="Known affected beneficiaries: females aged 12-17", null=True
            ),
        ),
        migrations.AddField(
            model_name="household",
            name="kab_female_age_group_18_59_count",
            field=models.PositiveIntegerField(
                blank=True, help_text="Known affected beneficiaries: females aged 18-59", null=True
            ),
        ),
        migrations.AddField(
            model_name="household",
            name="kab_female_age_group_60_count",
            field=models.PositiveIntegerField(
                blank=True, help_text="Known affected beneficiaries: females aged 60+", null=True
            ),
        ),
        migrations.AddField(
            model_name="household",
            name="kab_male_age_group_0_5_count",
            field=models.PositiveIntegerField(
                blank=True, help_text="Known affected beneficiaries: males aged 0-5", null=True
            ),
        ),
        migrations.AddField(
            model_name="household",
            name="kab_male_age_group_6_11_count",
            field=models.PositiveIntegerField(
                blank=True, help_text="Known affected beneficiaries: males aged 6-11", null=True
            ),
        ),
        migrations.AddField(
            model_name="household",
            name="kab_male_age_group_12_17_count",
            field=models.PositiveIntegerField(
                blank=True, help_text="Known affected beneficiaries: males aged 12-17", null=True
            ),
        ),
        migrations.AddField(
            model_name="household",
            name="kab_male_age_group_18_59_count",
            field=models.PositiveIntegerField(
                blank=True, help_text="Known affected beneficiaries: males aged 18-59", null=True
            ),
        ),
        migrations.AddField(
            model_name="household",
            name="kab_male_age_group_60_count",
            field=models.PositiveIntegerField(
                blank=True, help_text="Known affected beneficiaries: males aged 60+", null=True
            ),
        ),
        migrations.AddField(
            model_name="household",
            name="kab_female_age_group_0_5_disabled_count",
            field=models.PositiveIntegerField(
                blank=True, help_text="Known affected beneficiaries: females aged 0-5 with disability", null=True
            ),
        ),
        migrations.AddField(
            model_name="household",
            name="kab_female_age_group_6_11_disabled_count",
            field=models.PositiveIntegerField(
                blank=True, help_text="Known affected beneficiaries: females aged 6-11 with disability", null=True
            ),
        ),
        migrations.AddField(
            model_name="household",
            name="kab_female_age_group_12_17_disabled_count",
            field=models.PositiveIntegerField(
                blank=True, help_text="Known affected beneficiaries: females aged 12-17 with disability", null=True
            ),
        ),
        migrations.AddField(
            model_name="household",
            name="kab_female_age_group_18_59_disabled_count",
            field=models.PositiveIntegerField(
                blank=True, help_text="Known affected beneficiaries: females aged 18-59 with disability", null=True
            ),
        ),
        migrations.AddField(
            model_name="household",
            name="kab_female_age_group_60_disabled_count",
            field=models.PositiveIntegerField(
                blank=True, help_text="Known affected beneficiaries: females aged 60+ with disability", null=True
            ),
        ),
        migrations.AddField(
            model_name="household",
            name="kab_male_age_group_0_5_disabled_count",
            field=models.PositiveIntegerField(
                blank=True, help_text="Known affected beneficiaries: males aged 0-5 with disability", null=True
            ),
        ),
        migrations.AddField(
            model_name="household",
            name="kab_male_age_group_6_11_disabled_count",
            field=models.PositiveIntegerField(
                blank=True, help_text="Known affected beneficiaries: males aged 6-11 with disability", null=True
            ),
        ),
        migrations.AddField(
            model_name="household",
            name="kab_male_age_group_12_17_disabled_count",
            field=models.PositiveIntegerField(
                blank=True, help_text="Known affected beneficiaries: males aged 12-17 with disability", null=True
            ),
        ),
        migrations.AddField(
            model_name="household",
            name="kab_male_age_group_18_59_disabled_count",
            field=models.PositiveIntegerField(
                blank=True, help_text="Known affected beneficiaries: males aged 18-59 with disability", null=True
            ),
        ),
        migrations.AddField(
            model_name="household",
            name="kab_male_age_group_60_disabled_count",
            field=models.PositiveIntegerField(
                blank=True, help_text="Known affected beneficiaries: males aged 60+ with disability", null=True
            ),
        ),
        migrations.AddField(
            model_name="household",
            name="kab_size",
            field=models.PositiveIntegerField(
                blank=True, help_text="Known affected beneficiaries: total count", null=True
            ),
        ),
        migrations.AddField(
            model_name="household",
            name="kab_pregnant_count",
            field=models.PositiveIntegerField(
                blank=True, help_text="Known affected beneficiaries: pregnant members", null=True
            ),
        ),
        migrations.AddField(
            model_name="household",
            name="kab_children_count",
            field=models.PositiveIntegerField(
                blank=True, help_text="Known affected beneficiaries: children (under 18)", null=True
            ),
        ),
        migrations.AddField(
            model_name="household",
            name="kab_female_children_count",
            field=models.PositiveIntegerField(
                blank=True, help_text="Known affected beneficiaries: female children (under 18)", null=True
            ),
        ),
        migrations.AddField(
            model_name="household",
            name="kab_male_children_count",
            field=models.PositiveIntegerField(
                blank=True, help_text="Known affected beneficiaries: male children (under 18)", null=True
            ),
        ),
        migrations.AddField(
            model_name="household",
            name="kab_children_disabled_count",
            field=models.PositiveIntegerField(
                blank=True, help_text="Known affected beneficiaries: children (under 18) with disability", null=True
            ),
        ),
        migrations.AddField(
            model_name="household",
            name="kab_female_children_disabled_count",
            field=models.PositiveIntegerField(
                blank=True,
                help_text="Known affected beneficiaries: female children (under 18) with disability",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="household",
            name="kab_male_children_disabled_count",
            field=models.PositiveIntegerField(
                blank=True,
                help_text="Known affected beneficiaries: male children (under 18) with disability",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="household",
            name="kab_other_sex_group_count",
            field=models.PositiveIntegerField(
                blank=True, help_text="Known affected beneficiaries: members with other sex", null=True
            ),
        ),
        migrations.AddField(
            model_name="household",
            name="kab_unknown_sex_group_count",
            field=models.PositiveIntegerField(
                blank=True, help_text="Known affected beneficiaries: members with sex not collected", null=True
            ),
        ),
    ]
