# Generated by Django 3.2.25 on 2024-11-13 14:33

from django.db import migrations, models
import django.db.models.deletion
import hct_mis_api.apps.targeting.services.targeting_service
import model_utils.fields
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('targeting', '0049_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='targetingcriteriarule',
            name='household_ids',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='targetingcriteriarule',
            name='individual_ids',
            field=models.TextField(blank=True),
        ),
        migrations.CreateModel(
            name='TargetingCollectorRuleFilterBlock',
            fields=[
                ('id', model_utils.fields.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('targeting_criteria_rule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='collectors_filters_blocks', to='targeting.targetingcriteriarule')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, hct_mis_api.apps.targeting.services.targeting_service.TargetingIndividualRuleFilterBlockBase),
        ),
        migrations.CreateModel(
            name='TargetingCollectorBlockRuleFilter',
            fields=[
                ('id', model_utils.fields.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('field_name', models.CharField(max_length=120)),
                ('comparison_method', models.CharField(choices=[('EQUALS', 'Equals')], max_length=20)),
                ('flex_field_classification', models.CharField(choices=[('NOT_FLEX_FIELD', 'Not Flex Field'), ('FLEX_FIELD_BASIC', 'Flex Field Basic'), ('FLEX_FIELD_PDU', 'Flex Field PDU')], default='NOT_FLEX_FIELD', max_length=20)),
                ('arguments', models.JSONField(help_text='\n                Array of arguments\n                ')),
                ('round_number', models.PositiveIntegerField(blank=True, null=True)),
                ('collector_block_filters', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='collector_block_filters', to='targeting.targetingcollectorrulefilterblock')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, hct_mis_api.apps.targeting.services.targeting_service.TargetingCriteriaFilterBase),
        ),
    ]