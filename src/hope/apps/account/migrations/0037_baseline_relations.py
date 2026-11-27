from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    replaces = [
        ("account", "0001_migration"),
    ]

    dependencies = [
        ("account", "0036_baseline_models"),
        ("geo", "0010_baseline_models"),
    ]

    operations = [
        migrations.AddField(
            model_name="adminarealimitedto",
            name="areas",
            field=models.ManyToManyField(blank=True, related_name="admin_area_limits", to="geo.area"),
        ),
    ]
