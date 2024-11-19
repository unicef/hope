from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('household', '0117_migration'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='household',
            name='admin_area',
        ),
    ]
