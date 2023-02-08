from decimal import Decimal
import django.core.validators
from django.db import migrations, models
import django_fsm
import hct_mis_api.apps.payment.models

from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('payment', '0083_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='delivered_quantity',
            field=models.DecimalField(decimal_places=2, max_digits=12, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))]),
        ),
        migrations.AlterField(
            model_name='payment',
            name='delivered_quantity_usd',
            field=models.DecimalField(decimal_places=2, max_digits=12, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))]),
        ),
        migrations.AlterField(
            model_name='payment',
            name='entitlement_quantity',
            field=models.DecimalField(decimal_places=2, max_digits=12, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))]),
        ),
        migrations.AlterField(
            model_name='payment',
            name='entitlement_quantity_usd',
            field=models.DecimalField(decimal_places=2, max_digits=12, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))]),
        ),
        migrations.AlterField(
            model_name='payment',
            name='status',
            field=models.CharField(choices=[('Distribution Successful', 'Distribution Successful'), ('Not Distributed', 'Not Distributed'), ('Transaction Successful', 'Transaction Successful'), ('Transaction Erroneous', 'Transaction Erroneous'), ('Force failed', 'Force failed'), ('Partially Distributed', 'Partially Distributed'), ('Pending', 'Pending')], max_length=255),
        ),
        migrations.AlterField(
            model_name='paymentplan',
            name='status',
            field=django_fsm.FSMField(choices=[('OPEN', 'Open'), ('LOCKED', 'Locked'), ('LOCKED_FSP', 'Locked FSP'), ('IN_APPROVAL', 'In Approval'), ('IN_AUTHORIZATION', 'In Authorization'), ('IN_REVIEW', 'In Review'), ('ACCEPTED', 'Accepted'), ('FINISHED', 'Finished')], db_index=True, default='OPEN', max_length=50),
        ),
        migrations.AlterField(
            model_name='paymentrecord',
            name='delivered_quantity',
            field=models.DecimalField(decimal_places=2, max_digits=12, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))]),
        ),
        migrations.AlterField(
            model_name='paymentrecord',
            name='delivered_quantity_usd',
            field=models.DecimalField(decimal_places=2, max_digits=12, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))]),
        ),
        migrations.AlterField(
            model_name='paymentrecord',
            name='entitlement_quantity',
            field=models.DecimalField(decimal_places=2, max_digits=12, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))]),
        ),
        migrations.AlterField(
            model_name='paymentrecord',
            name='entitlement_quantity_usd',
            field=models.DecimalField(decimal_places=2, max_digits=12, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))]),
        ),
        migrations.AlterField(
            model_name='paymentrecord',
            name='status',
            field=models.CharField(choices=[('Distribution Successful', 'Distribution Successful'), ('Not Distributed', 'Not Distributed'), ('Transaction Successful', 'Transaction Successful'), ('Transaction Erroneous', 'Transaction Erroneous'), ('Force failed', 'Force failed'), ('Partially Distributed', 'Partially Distributed'), ('Pending', 'Pending')], max_length=255),
        ),
    ]
