# Generated by Django 3.2.25 on 2025-02-19 09:28

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("household", "0011_migration"),
    ]

    operations = [
        migrations.AddField(
            model_name="household",
            name="other_sex_group_count",
            field=models.PositiveIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name="household",
            name="unknown_sex_group_count",
            field=models.PositiveIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name="household",
            name="children_count",
            field=models.PositiveIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name="household",
            name="children_disabled_count",
            field=models.PositiveIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name="household",
            name="female_age_group_0_5_count",
            field=models.PositiveIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name="household",
            name="female_age_group_0_5_disabled_count",
            field=models.PositiveIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name="household",
            name="female_age_group_12_17_count",
            field=models.PositiveIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name="household",
            name="female_age_group_12_17_disabled_count",
            field=models.PositiveIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name="household",
            name="female_age_group_18_59_count",
            field=models.PositiveIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name="household",
            name="female_age_group_18_59_disabled_count",
            field=models.PositiveIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name="household",
            name="female_age_group_60_count",
            field=models.PositiveIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name="household",
            name="female_age_group_60_disabled_count",
            field=models.PositiveIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name="household",
            name="female_age_group_6_11_count",
            field=models.PositiveIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name="household",
            name="female_age_group_6_11_disabled_count",
            field=models.PositiveIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name="household",
            name="female_children_count",
            field=models.PositiveIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name="household",
            name="female_children_disabled_count",
            field=models.PositiveIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name="household",
            name="male_age_group_0_5_count",
            field=models.PositiveIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name="household",
            name="male_age_group_0_5_disabled_count",
            field=models.PositiveIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name="household",
            name="male_age_group_12_17_count",
            field=models.PositiveIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name="household",
            name="male_age_group_12_17_disabled_count",
            field=models.PositiveIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name="household",
            name="male_age_group_18_59_count",
            field=models.PositiveIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name="household",
            name="male_age_group_18_59_disabled_count",
            field=models.PositiveIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name="household",
            name="male_age_group_60_count",
            field=models.PositiveIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name="household",
            name="male_age_group_60_disabled_count",
            field=models.PositiveIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name="household",
            name="male_age_group_6_11_count",
            field=models.PositiveIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name="household",
            name="male_age_group_6_11_disabled_count",
            field=models.PositiveIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name="household",
            name="male_children_count",
            field=models.PositiveIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name="household",
            name="male_children_disabled_count",
            field=models.PositiveIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name="household",
            name="pregnant_count",
            field=models.PositiveIntegerField(blank=True, default=None, null=True),
        ),
    ]
