# Generated by Django 3.2.25 on 2024-08-26 13:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration_data', '0038_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registrationdataimport',
            name='data_source',
            field=models.CharField(choices=[('XLS', 'Excel'), ('KOBO', 'KoBo'), ('FLEX_REGISTRATION', 'Flex Registration'), ('API', 'Flex API'), ('EDOPOMOGA', 'eDopomoga'), ('PROGRAM_POPULATION', 'Programme Population'), ('ENROLL_FROM_PROGRAM', 'Enroll From Programme')], max_length=255),
        ),
    ]