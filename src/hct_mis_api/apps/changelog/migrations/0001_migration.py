# Generated by Django 3.2.25 on 2024-11-07 12:18

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Changelog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(blank=True)),
                ('version', models.CharField(help_text='HOPE version', max_length=30)),
                ('active', models.BooleanField(default=False)),
                ('date', models.DateField(default=datetime.date.today)),
            ],
            options={
                'ordering': ('-date',),
            },
        ),
    ]