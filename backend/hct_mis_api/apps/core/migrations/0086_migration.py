from django.db import migrations

def migrate_subtype_boolean_to_bool(apps, schema_editor):
    PeriodicFieldData = apps.get_model('core', 'PeriodicFieldData')
    PeriodicFieldData.objects.filter(subtype='BOOLEAN').update(subtype='BOOL')

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0085_migration'),
    ]

    operations = [
        migrations.RunPython(migrate_subtype_boolean_to_bool, reverse_code=migrations.RunPython.noop),
    ]
