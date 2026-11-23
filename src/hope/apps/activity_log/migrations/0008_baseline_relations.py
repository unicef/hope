from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    replaces = [
        ("activity_log", "0001_migration"),
    ]

    dependencies = [
        ("activity_log", "0007_baseline_models"),
        ("contenttypes", "0002_remove_content_type_name"),
        ("core", "0044_baseline_models"),
    ]

    operations = [
        migrations.AddField(
            model_name="logentry",
            name="business_area",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="core.businessarea",
            ),
        ),
        migrations.AddField(
            model_name="logentry",
            name="content_type",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="log_entries",
                to="contenttypes.contenttype",
            ),
        ),
    ]
