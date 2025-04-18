# Generated by Django 3.2.25 on 2025-04-10 12:02

from django.db import migrations, models
import django.db.models.deletion
import model_utils.fields
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('geo', '0004_migration'),
        ('payment', '0025_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='number',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.CreateModel(
            name='FinancialInstitution',
            fields=[
                ('id', model_utils.fields.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('code', models.CharField(max_length=30, unique=True)),
                ('description', models.CharField(blank=True, max_length=255, null=True)),
                ('type', models.CharField(choices=[('bank', 'Bank'), ('telco', 'Telco'), ('other', 'Other')], max_length=30)),
                ('country', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='geo.country')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='account',
            name='financial_institution',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='payment.financialinstitution'),
        ),
    ]
