# Generated by Django 3.2.25 on 2024-07-22 10:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration_data', '0036_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='koboimportdata',
            name='pull_pictures',
            field=models.BooleanField(default=True),
        ),
    ]