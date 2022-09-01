from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grievance', '0047_migration'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='grievanceticket',
            name='admin2',
        ),
    ]
