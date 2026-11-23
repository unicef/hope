from django.db import migrations, models
import django.db.models.deletion

import hope.models.utils


class Migration(migrations.Migration):
    initial = True

    replaces = [
        ("aurora", "0002_migration"),
    ]

    dependencies = [
        ("aurora", "0008_baseline_relations"),
        ("program", "0027_baseline_models"),
        ("steficon", "0008_baseline_models"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="programme",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="program.program",
            ),
        ),
        migrations.AddField(
            model_name="registration",
            name="project",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="aurora.project"),
        ),
        migrations.AddField(
            model_name="registration",
            name="steficon_rule",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="steficon.rulecommit",
            ),
        ),
        migrations.AddIndex(
            model_name="organization",
            index=hope.models.utils.LongNameIndex(
                fields=["created_at"], name="aurora_organization_created_at_4f7b8b55"
            ),
        ),
        migrations.AddIndex(
            model_name="organization",
            index=hope.models.utils.LongNameIndex(
                fields=["updated_at"], name="aurora_organization_updated_at_b65df51b"
            ),
        ),
        migrations.AddIndex(
            model_name="project",
            index=hope.models.utils.LongNameIndex(fields=["created_at"], name="aurora_project_created_at_58878624"),
        ),
        migrations.AddIndex(
            model_name="project",
            index=hope.models.utils.LongNameIndex(fields=["updated_at"], name="aurora_project_updated_at_9b17f827"),
        ),
        migrations.AddIndex(
            model_name="registration",
            index=hope.models.utils.LongNameIndex(
                fields=["created_at"], name="aurora_registration_created_at_2c5ed126"
            ),
        ),
        migrations.AddIndex(
            model_name="registration",
            index=hope.models.utils.LongNameIndex(
                fields=["updated_at"], name="aurora_registration_updated_at_4dbeb556"
            ),
        ),
    ]
