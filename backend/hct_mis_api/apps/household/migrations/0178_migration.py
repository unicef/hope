# Generated by Django 3.2.25 on 2024-06-20 14:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('household', '0177_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='bankaccountinfo',
            name='rdi_merge_status',
            field=models.CharField(choices=[('PENDING', 'Pending'), ('MERGED', 'Merged')], default='PENDING', max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='document',
            name='rdi_merge_status',
            field=models.CharField(choices=[('PENDING', 'Pending'), ('MERGED', 'Merged')], default='PENDING', max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='household',
            name='enumerator_rec_id',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='household',
            name='flex_registrations_record_id',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='household',
            name='kobo_submission_time',
            field=models.DateTimeField(blank=True, max_length=150, null=True),
        ),
        migrations.AddField(
            model_name='household',
            name='kobo_submission_uuid',
            field=models.UUIDField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='household',
            name='mis_unicef_id',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='household',
            name='rdi_merge_status',
            field=models.CharField(choices=[('PENDING', 'Pending'), ('MERGED', 'Merged')], default='PENDING', max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='individual',
            name='mis_unicef_id',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='individual',
            name='rdi_merge_status',
            field=models.CharField(choices=[('PENDING', 'Pending'), ('MERGED', 'Merged')], default='PENDING', max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='individualidentity',
            name='rdi_merge_status',
            field=models.CharField(choices=[('PENDING', 'Pending'), ('MERGED', 'Merged')], default='PENDING', max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='individualroleinhousehold',
            name='rdi_merge_status',
            field=models.CharField(choices=[('PENDING', 'Pending'), ('MERGED', 'Merged')], default='PENDING', max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='household',
            name='head_of_household',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='heading_household', to='household.individual'),
        ),
    ]