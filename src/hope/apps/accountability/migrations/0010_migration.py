from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accountability", "0009_migration"),
    ]

    operations = [
        migrations.AlterField(
            model_name="feedback",
            name="program",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.deletion.SET_NULL,
                to="program.Program",
            ),
        ),
        migrations.AlterField(
            model_name="message",
            name="program",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.deletion.SET_NULL,
                related_name="messages",
                to="program.Program",
            ),
        ),
        migrations.AlterField(
            model_name="survey",
            name="program",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.deletion.SET_NULL,
                related_name="surveys",
                to="program.Program",
            ),
        ),
    ]
