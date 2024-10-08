from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('household', '0118_migration'),
    ]

    operations = [
        migrations.RenameField(
            model_name='household',
            old_name='admin_area_new',
            new_name='admin_area',
        ),
    ]
