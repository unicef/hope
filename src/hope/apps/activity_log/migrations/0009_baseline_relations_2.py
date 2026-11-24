from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

import hope.models.utils


class Migration(migrations.Migration):
    initial = True

    replaces = [
        ("activity_log", "0002_migration"),
    ]

    dependencies = [
        ("activity_log", "0008_baseline_relations"),
        ("program", "0023_baseline_models"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="logentry",
            name="programs",
            field=models.ManyToManyField(blank=True, related_name="activity_logs", to="program.program"),
        ),
        migrations.AddField(
            model_name="logentry",
            name="user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="logs",
                to=settings.AUTH_USER_MODEL,
                verbose_name="actor",
            ),
        ),
        migrations.AddIndex(
            model_name="logentry",
            index=models.Index(fields=["business_area", "-timestamp"], name="idx_le_ba_ts"),
        ),
        migrations.AddIndex(
            model_name="logentry",
            index=hope.models.utils.LongNameIndex(
                fields=["object_id"], name="activity_log_logentry_object_id_d7af1d06"
            ),
        ),
        migrations.AddIndex(
            model_name="logentry",
            index=hope.models.utils.LongNameIndex(fields=["action"], name="activity_log_logentry_action_7b504b2d"),
        ),
        migrations.AddIndex(
            model_name="logentry",
            index=hope.models.utils.LongNameIndex(
                fields=["action"],
                name="activity_log_logentry_action_7b504b2d_like",
                opclasses=["varchar_pattern_ops"],
            ),
        ),
        migrations.AddIndex(
            model_name="logentry",
            index=hope.models.utils.LongNameIndex(
                fields=["timestamp"], name="activity_log_logentry_timestamp_62c98ec4"
            ),
        ),
    ]
