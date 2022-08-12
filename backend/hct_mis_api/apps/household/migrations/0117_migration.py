from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('household', '0116_migration'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='agency',
            name='unique_type_and_country',
        ),
        migrations.RenameField(
            model_name='agency',
            old_name='country_new',
            new_name='country',
        ),
        migrations.AddConstraint(
            model_name='agency',
            constraint=models.UniqueConstraint(fields=('type', 'country'), name='unique_type_and_country'),
        ),
    ]
