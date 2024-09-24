# Generated by Django 3.2.20 on 2023-10-06 13:16

from django.db import migrations, models
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0109_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='additional_collector_name',
            field=models.CharField(blank=True, help_text='Use this field for reconciliation data when funds are collected by someone other than the designated collector or the alternate collector', max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='additional_document_number',
            field=models.CharField(blank=True, help_text='Use this field for reconciliation data', max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='additional_document_type',
            field=models.CharField(blank=True, help_text='Use this field for reconciliation data', max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name='financialserviceproviderxlsxtemplate',
            name='columns',
            field=multiselectfield.db.fields.MultiSelectField(choices=[('payment_id', 'Payment ID'), ('household_id', 'Household ID'), ('household_size', 'Household Size'), ('collector_name', 'Collector Name'), ('alternate_collector_full_name', 'Alternate collector Full Name'), ('alternate_collector_given_name', 'Alternate collector Given Name'), ('alternate_collector_middle_name', 'Alternate collector Middle Name'), ('alternate_collector_phone_no', 'Alternate collector phone number'), ('alternate_collector_document_numbers', 'Alternate collector Document numbers'), ('alternate_collector_sex', 'Alternate collector Gender'), ('payment_channel', 'Payment Channel'), ('fsp_name', 'FSP Name'), ('currency', 'Currency'), ('entitlement_quantity', 'Entitlement Quantity'), ('entitlement_quantity_usd', 'Entitlement Quantity USD'), ('delivered_quantity', 'Delivered Quantity'), ('delivery_date', 'Delivery Date'), ('reason_for_unsuccessful_payment', 'Reason for unsuccessful payment'), ('order_number', 'Order Number'), ('token_number', 'Token Number'), ('additional_collector_name', 'Additional Collector Name'), ('additional_document_type', 'Additional Document Type'), ('additional_document_number', 'Additional Document Number')], default=['payment_id', 'household_id', 'household_size', 'collector_name', 'alternate_collector_full_name', 'alternate_collector_given_name', 'alternate_collector_middle_name', 'alternate_collector_phone_no', 'alternate_collector_document_numbers', 'alternate_collector_sex', 'payment_channel', 'fsp_name', 'currency', 'entitlement_quantity', 'entitlement_quantity_usd', 'delivered_quantity', 'delivery_date', 'reason_for_unsuccessful_payment', 'order_number', 'token_number', 'additional_collector_name', 'additional_document_type', 'additional_document_number'], help_text='Select the columns to include in the report', max_length=500, verbose_name='Columns'),
        ),
    ]