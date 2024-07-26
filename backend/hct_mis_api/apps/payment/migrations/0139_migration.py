# Generated by Django 3.2.25 on 2024-07-23 15:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('program', '0049_migration'),
        ('payment', '0138_migration'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cashplan',
            name='end_date',
        ),
        migrations.RemoveField(
            model_name='cashplan',
            name='start_date',
        ),
        migrations.RemoveField(
            model_name='paymentplan',
            name='end_date',
        ),
        migrations.RemoveField(
            model_name='paymentplan',
            name='start_date',
        ),
        migrations.AlterField(
            model_name='paymentplan',
            name='program_cycle',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='payment_plans', to='program.programcycle'),
        ),
    ]