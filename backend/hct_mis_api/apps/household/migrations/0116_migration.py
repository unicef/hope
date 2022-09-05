from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('household', '0115_migration'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='agency',
            name='unique_type_and_country',
        ),
        migrations.RemoveField(
            model_name='agency',
            name='country',
        ),
        migrations.AddConstraint(
            model_name='agency',
            constraint=models.UniqueConstraint(fields=('type', 'country_new'), name='unique_type_and_country'),
        ),
    ]
