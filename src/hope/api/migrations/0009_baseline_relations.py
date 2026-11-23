from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    replaces = [
        ("api", "0001_migration"),
    ]

    dependencies = [
        ("api", "0008_baseline_models"),
        ("core", "0044_baseline_models"),
    ]

    operations = [
        migrations.AddField(
            model_name="apitoken",
            name="valid_for",
            field=models.ManyToManyField(to="core.businessarea"),
        ),
        migrations.AddField(
            model_name="apilogentry",
            name="token",
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="api.apitoken"),
        ),
    ]
