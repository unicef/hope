from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('household', '0112_migration'),
    ]

    operations = [
        migrations.RenameField(
            model_name='household',
            old_name='country_new',
            new_name='country',
        ),
        migrations.RenameField(
            model_name='household',
            old_name='country_origin_new',
            new_name='country_origin',
        ),
    ]
