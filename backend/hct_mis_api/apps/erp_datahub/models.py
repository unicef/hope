from decimal import Decimal

from django.core.validators import MinValueValidator

from utils.models import AbstractSession
from django.db import models


class Session(AbstractSession):
    pass


class SessionModel(models.Model):
    session = models.ForeignKey("Session", on_delete=models.CASCADE)

    class Meta:
        abstract = True


class FundsCommitment(SessionModel):
    business_area = models.CharField(max_length=4)
    funds_commitment_number = models.CharField(max_length=10, primary_key=True)
    document_type = models.CharField(max_length=10)
    document_text = models.TextField()
    currency_code = models.CharField(max_length=4, null=True)
    g_l_account = models.IntegerField(null=True)
    commitment_amount_local = models.DecimalField(
        decimal_places=2,
        max_digits=13,
        validators=[MinValueValidator(Decimal("0.01"))],
        null=True,
    )
    commitment_amount_usd = models.DecimalField(
        decimal_places=2,
        max_digits=13,
        validators=[MinValueValidator(Decimal("0.01"))],
        null=True,
    )
    total_open_amount_local = models.DecimalField(
        decimal_places=2,
        max_digits=13,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    total_open_amount_usd = models.DecimalField(
        decimal_places=2,
        max_digits=13,
        validators=[MinValueValidator(Decimal("0.01"))],
        null=True,
    )
    exchange_rate = models.DecimalField(
        decimal_places=5,
        max_digits=9,
        validators=[MinValueValidator(Decimal("0.00001"))],
        null=True,
    )
    vendor_id = models.CharField(max_length=10, null=True)
    posting_date = models.DateField(null=True)
    vision_approval = models.DateField(null=True)


class DownPayment(SessionModel):
    business_area = models.CharField(max_length=4)
    down_payment_number = models.CharField(max_length=10, primary_key=True)
    document_type = models.CharField(max_length=10)
    consumer_fc_number = models.CharField(max_length=10)
    total_down_payment_amount_local = models.DecimalField(
        decimal_places=2,
        max_digits=13,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    total_down_payment_amount_usd = models.DecimalField(
        decimal_places=2,
        max_digits=13,
        validators=[MinValueValidator(Decimal("0.01"))],
        null=True,
    )
    currency_code = models.CharField(max_length=5, null=True)
    exchange_rate = models.DecimalField(
        decimal_places=5,
        max_digits=9,
        validators=[MinValueValidator(Decimal("0.00001"))],
        null=True,
    )
    vendor_id = models.CharField(max_length=10, null=True)
    posting_date = models.DateField(null=True)
