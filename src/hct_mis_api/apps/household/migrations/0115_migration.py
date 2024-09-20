from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('geo', '0007_migration'),
        ('household', '0114_migration'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='documenttype',
            options={'ordering': ['country', 'label']},
        ),
        migrations.RenameField(
            model_name='documenttype',
            old_name='country_new',
            new_name='country',
        ),
        migrations.AlterUniqueTogether(
            name='documenttype',
            unique_together={('country', 'type')},
        ),
    ]
