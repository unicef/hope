from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration_datahub', '0061_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='record',
            name='error_message',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='record',
            name='status',
            field=models.CharField(choices=[('TO_IMPORT', 'To import'), ('IMPORTED', 'Imported'), ('ERROR', 'Error')], default='TO_IMPORT', max_length=16),
        ),
    ]
