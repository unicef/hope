from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('geo', '0007_migration'),
        ('household', '0113_migration'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='documenttype',
            options={'ordering': ['country_new', 'label']},
        ),
        migrations.AlterUniqueTogether(
            name='documenttype',
            unique_together={('country_new', 'type')},
        ),
        migrations.RemoveField(
            model_name='documenttype',
            name='country',
        ),
    ]
