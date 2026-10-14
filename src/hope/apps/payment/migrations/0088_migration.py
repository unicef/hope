from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0039_migration"),
        ("payment", "0087_migration"),
    ]

    operations = [
        migrations.AddField(
            model_name="paymentplangroup",
            name="export_file_delivery",
            field=models.ForeignKey(
                blank=True,
                help_text="Generated payment list XLSX for the FSP [sys]",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="core.filetemp",
            ),
        ),
        migrations.RemoveField(
            model_name="paymentplan",
            name="export_file_delivery",
        ),
        migrations.RemoveField(
            model_name="paymentplan",
            name="export_tag",
        ),
    ]
