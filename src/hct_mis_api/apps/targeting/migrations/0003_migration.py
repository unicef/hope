# Generated by Django 2.2.8 on 2020-04-30 08:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('targeting', '0002_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='targetpopulation',
            name='approved_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='targetpopulation',
            name='approved_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_target_populations', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='targetpopulation',
            name='finalized_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='targetpopulation',
            name='finalized_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='finalized_target_populations', to=settings.AUTH_USER_MODEL),
        ),
    ]