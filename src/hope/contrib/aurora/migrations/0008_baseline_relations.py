from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    replaces = [
        ("aurora", "0001_migration"),
    ]

    dependencies = [
        ("aurora", "0007_baseline_models"),
        ("core", "0041_baseline_models"),
    ]

    operations = [
        migrations.AddField(
            model_name="organization",
            name="business_area",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="core.businessarea",
            ),
        ),
        migrations.AddField(
            model_name="project",
            name="organization",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="aurora.organization"),
        ),
    ]
