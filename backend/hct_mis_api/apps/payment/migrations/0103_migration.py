from decimal import Decimal
import django.core.validators

from django.db import migrations, models
import django_fsm


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0102_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cashplan',
            name='total_delivered_quantity',
            field=models.DecimalField(blank=True, db_index=True, decimal_places=2, max_digits=12, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0'))]),
        ),
        migrations.AlterField(
            model_name='cashplan',
            name='total_delivered_quantity_usd',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0'))]),
        ),
        migrations.AlterField(
            model_name='cashplan',
            name='total_entitled_quantity',
            field=models.DecimalField(db_index=True, decimal_places=2, max_digits=12, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0'))]),
        ),
        migrations.AlterField(
            model_name='cashplan',
            name='total_entitled_quantity_revised',
            field=models.DecimalField(blank=True, db_index=True, decimal_places=2, max_digits=12, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0'))]),
        ),
        migrations.AlterField(
            model_name='cashplan',
            name='total_entitled_quantity_revised_usd',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0'))]),
        ),
        migrations.AlterField(
            model_name='cashplan',
            name='total_entitled_quantity_usd',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0'))]),
        ),
        migrations.AlterField(
            model_name='cashplan',
            name='total_undelivered_quantity',
            field=models.DecimalField(blank=True, db_index=True, decimal_places=2, max_digits=12, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0'))]),
        ),
        migrations.AlterField(
            model_name='cashplan',
            name='total_undelivered_quantity_usd',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0'))]),
        ),
        migrations.AlterField(
            model_name='payment',
            name='delivered_quantity',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))]),
        ),
        migrations.AlterField(
            model_name='payment',
            name='delivered_quantity_usd',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))]),
        ),
        migrations.AlterField(
            model_name='payment',
            name='entitlement_quantity',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))]),
        ),
        migrations.AlterField(
            model_name='payment',
            name='entitlement_quantity_usd',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))]),
        ),
        migrations.AlterField(
            model_name='paymentplan',
            name='total_delivered_quantity',
            field=models.DecimalField(blank=True, db_index=True, decimal_places=2, max_digits=12, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0'))]),
        ),
        migrations.AlterField(
            model_name='paymentplan',
            name='total_delivered_quantity_usd',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0'))]),
        ),
        migrations.AlterField(
            model_name='paymentplan',
            name='total_entitled_quantity',
            field=models.DecimalField(db_index=True, decimal_places=2, max_digits=12, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0'))]),
        ),
        migrations.AlterField(
            model_name='paymentplan',
            name='total_entitled_quantity_revised',
            field=models.DecimalField(blank=True, db_index=True, decimal_places=2, max_digits=12, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0'))]),
        ),
        migrations.AlterField(
            model_name='paymentplan',
            name='total_entitled_quantity_revised_usd',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0'))]),
        ),
        migrations.AlterField(
            model_name='paymentplan',
            name='total_entitled_quantity_usd',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0'))]),
        ),
        migrations.AlterField(
            model_name='paymentplan',
            name='total_undelivered_quantity',
            field=models.DecimalField(blank=True, db_index=True, decimal_places=2, max_digits=12, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0'))]),
        ),
        migrations.AlterField(
            model_name='paymentplan',
            name='total_undelivered_quantity_usd',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0'))]),
        ),
        migrations.AlterField(
            model_name='paymentrecord',
            name='delivered_quantity',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))]),
        ),
        migrations.AlterField(
            model_name='paymentrecord',
            name='delivered_quantity_usd',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))]),
        ),
        migrations.AlterField(
            model_name='paymentrecord',
            name='entitlement_quantity',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))]),
        ),
        migrations.AlterField(
            model_name='paymentrecord',
            name='entitlement_quantity_usd',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))]),
        ),
        migrations.AddField(
            model_name='paymentplan',
            name='exclude_household_error',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='paymentplan',
            name='background_action_status',
            field=django_fsm.FSMField(blank=True, choices=[('RULE_ENGINE_RUN', 'Rule Engine Running'), ('RULE_ENGINE_ERROR', 'Rule Engine Errored'), ('XLSX_EXPORTING', 'Exporting XLSX file'), ('XLSX_EXPORT_ERROR', 'Export XLSX file Error'), ('XLSX_IMPORT_ERROR', 'Import XLSX file Error'), ('XLSX_IMPORTING_ENTITLEMENTS', 'Importing Entitlements XLSX file'), ('XLSX_IMPORTING_RECONCILIATION', 'Importing Reconciliation XLSX file'), ('EXCLUDE_BENEFICIARIES', 'Exclude Beneficiaries Running'), ('EXCLUDE_BENEFICIARIES_ERROR', 'Exclude Beneficiaries Error')], db_index=True, default=None, max_length=50, null=True),
        ),
    ]
