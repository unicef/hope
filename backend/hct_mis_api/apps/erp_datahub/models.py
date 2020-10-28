from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from utils.models import AbstractSession


class FundsCommitment(models.Model):
    rec_serial_number = models.CharField(max_length=10, null=True)
    business_area = models.CharField(max_length=4, null=True)
    funds_commitment_number = models.CharField(max_length=10, null=True)
    document_type = models.CharField(max_length=2, null=True)
    document_text = models.CharField(max_length=50, null=True)
    currency_code = models.CharField(max_length=5, null=True)
    gl_account = models.CharField(null=True, max_length=10)
    commitment_amount_local = models.DecimalField(
        decimal_places=2,
        max_digits=15,
        validators=[MinValueValidator(Decimal("0.01"))],
        null=True,
    )
    commitment_amount_usd = models.DecimalField(
        decimal_places=2,
        max_digits=15,
        validators=[MinValueValidator(Decimal("0.01"))],
        null=True,
    )
    total_open_amount_local = models.DecimalField(
        decimal_places=2,
        max_digits=15,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    total_open_amount_usd = models.DecimalField(
        decimal_places=2,
        max_digits=15,
        validators=[MinValueValidator(Decimal("0.01"))],
        null=True,
    )
    vendor_id = models.CharField(max_length=10, null=True)
    posting_date = models.DateField(null=True)
    vision_approval = models.CharField(max_length=1, null=True)
    document_reference = models.CharField(max_length=16, null=True)
    fc_status = models.CharField(max_length=1, null=True)
    create_date = models.DateTimeField(null=True)
    created_by = models.CharField(max_length=50, null=True)
    update_date = models.DateTimeField(null=True)
    updated_by = models.CharField(max_length=50, null=True)
    mis_sync_flag = models.BooleanField(null=True)
    mis_sync_date = models.DateTimeField(null=True)
    ca_sync_flag = models.BooleanField(null=True)
    ca_sync_date = models.DateTimeField(null=True)


class DownPayment(models.Model):
    rec_serial_number = models.CharField(max_length=10, null=True)
    business_area = models.CharField(max_length=4)
    down_payment_reference = models.CharField(max_length=20, primary_key=True)
    document_type = models.CharField(max_length=10)
    consumed_fc_number = models.CharField(max_length=10)
    total_down_payment_amount_local = models.DecimalField(
        decimal_places=2,
        max_digits=15,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    total_down_payment_amount_usd = models.DecimalField(
        decimal_places=2,
        max_digits=15,
        validators=[MinValueValidator(Decimal("0.01"))],
        null=True,
    )
    currency_code = models.CharField(max_length=5, null=True)
    posting_date = models.DateField(null=True)
    doc_year = models.IntegerField(null=True)
    doc_number = models.CharField(max_length=10, null=True)
    doc_item_number = models.CharField(max_length=3, null=True)
    doc_reversed = models.CharField(max_length=1, null=True)
    create_date = models.DateTimeField(null=True)
    created_by = models.CharField(max_length=50, null=True)
    update_date = models.DateTimeField(null=True)
    updated_by = models.CharField(max_length=50, null=True)
    mis_sync_flag = models.BooleanField(null=True)
    mis_sync_date = models.DateTimeField(null=True)
    ca_sync_flag = models.BooleanField(null=True)
    ca_sync_date = models.DateTimeField(null=True)
