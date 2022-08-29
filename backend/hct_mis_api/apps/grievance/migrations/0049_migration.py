from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grievance', '0048_migration'),
    ]

    operations = [
        migrations.RenameField(
            model_name='grievanceticket',
            old_name='admin2_new',
            new_name='admin2',
        ),
    ]
