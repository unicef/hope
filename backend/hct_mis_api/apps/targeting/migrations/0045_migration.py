# Generated by Django 3.2.25 on 2024-08-05 23:07

from django.db import migrations, models


def convert_is_flex_field_to_classification(apps, schema_editor):
    TargetingCriteriaRuleFilter = apps.get_model('targeting', 'TargetingCriteriaRuleFilter')
    TargetingCriteriaRuleFilter.objects.filter(is_flex_field=True).update(flex_field_classification='FLEX_FIELD_NOT_PDU')
    TargetingCriteriaRuleFilter.objects.filter(is_flex_field=False).update(flex_field_classification='NOT_FLEX_FIELD')

    TargetingIndividualBlockRuleFilter = apps.get_model('targeting', 'TargetingIndividualBlockRuleFilter')
    TargetingIndividualBlockRuleFilter.objects.filter(is_flex_field=True).update(flex_field_classification='FLEX_FIELD_NOT_PDU')
    TargetingIndividualBlockRuleFilter.objects.filter(is_flex_field=False).update(flex_field_classification='NOT_FLEX_FIELD')


class Migration(migrations.Migration):

    dependencies = [
        ('targeting', '0044_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='targetingcriteriarulefilter',
            name='flex_field_classification',
            field=models.CharField(choices=[('NOT_FLEX_FIELD', 'Not Flex Field'), ('FLEX_FIELD_NOT_PDU', 'Flex Field Not PDU'), ('FLEX_FIELD_PDU', 'Flex Field PDU')], default='NOT_FLEX_FIELD', max_length=20),
        ),
        migrations.AddField(
            model_name='targetingindividualblockrulefilter',
            name='flex_field_classification',
            field=models.CharField(choices=[('NOT_FLEX_FIELD', 'Not Flex Field'), ('FLEX_FIELD_NOT_PDU', 'Flex Field Not PDU'), ('FLEX_FIELD_PDU', 'Flex Field PDU')], default='NOT_FLEX_FIELD', max_length=20),
        ),
        migrations.RunPython(convert_is_flex_field_to_classification),
        migrations.RemoveField(
            model_name='targetingcriteriarulefilter',
            name='is_flex_field',
        ),
        migrations.RemoveField(
            model_name='targetingindividualblockrulefilter',
            name='is_flex_field',
        ),
    ]