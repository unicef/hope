from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("payment", "0065_migration"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="paymentplan",
            name="is_follow_up",
        ),
    ]
