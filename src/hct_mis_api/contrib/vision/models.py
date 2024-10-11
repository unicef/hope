from django.db import models

from hct_mis_api.apps.core.models import BusinessArea


class FundsCommitment(models.Model):
    rec_serial_number = models.CharField(max_length=10, unique=True)
    business_area = models.CharField(max_length=4, blank=True, null=True)
    funds_commitment_number = models.CharField(max_length=10, blank=True, null=True)
    document_type = models.CharField(max_length=2, blank=True, null=True)
    document_text = models.CharField(max_length=50, blank=True, null=True)
    currency_code = models.CharField(max_length=5, blank=True, null=True)
    gl_account = models.CharField(null=True, blank=True, max_length=10)
    commitment_amount_local = models.DecimalField(
        decimal_places=2,
        max_digits=15,
        blank=True,
        null=True,
    )
    commitment_amount_usd = models.DecimalField(
        decimal_places=2,
        max_digits=15,
        blank=True,
        null=True,
    )
    total_open_amount_local = models.DecimalField(
        decimal_places=2,
        max_digits=15,
        blank=True,
        null=True,
    )
    total_open_amount_usd = models.DecimalField(
        decimal_places=2,
        max_digits=15,
        blank=True,
        null=True,
    )
    vendor_id = models.CharField(max_length=10, blank=True, null=True)
    posting_date = models.DateField(blank=True, null=True)
    vision_approval = models.CharField(max_length=1, blank=True, null=True)
    document_reference = models.CharField(max_length=16, null=True)
    fc_status = models.CharField(max_length=1, blank=True, null=True)
    create_date = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    created_by = models.CharField(max_length=20, null=True, blank=True, default="")
    update_date = models.DateTimeField(null=True, blank=True)
    updated_by = models.CharField(max_length=20, blank=True, null=True, default="")

    grant_number = models.CharField(max_length=10, null=True, blank=True, default="")
    sponsor = models.CharField(max_length=10, null=True, blank=True, default="")
    sponsor_name = models.CharField(max_length=100, null=True, blank=True, default="")
    wbs_element = models.CharField(max_length=24, null=True, blank=True, default="")
    fund = models.CharField(max_length=10, null=True, blank=True, default="")
    funds_center = models.CharField(max_length=16, null=True, blank=True, default="")
    funds_commitment_item = models.CharField(max_length=3, null=True, blank=True, default="")
    percentage = models.DecimalField(decimal_places=2, max_digits=5, null=True, blank=True)

    business_office_code = models.CharField(max_length=4, blank=True, null=True)
    business_area_obj = models.ForeignKey(BusinessArea, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self) -> str:
        return self.funds_commitment_number

    class Meta:
        unique_together = ("funds_commitment_number", "funds_commitment_item")


class DownPayment(models.Model):
    rec_serial_number = models.CharField(max_length=10, blank=True, null=True)
    business_area = models.CharField(max_length=4)
    down_payment_reference = models.CharField(max_length=20)
    document_type = models.CharField(max_length=10)
    consumed_fc_number = models.CharField(max_length=10)
    total_down_payment_amount_local = models.DecimalField(
        decimal_places=2,
        max_digits=15,
    )
    total_down_payment_amount_usd = models.DecimalField(
        decimal_places=2,
        max_digits=15,
        blank=True,
        null=True,
    )
    currency_code = models.CharField(max_length=5, blank=True, null=True)
    posting_date = models.DateField(blank=True, null=True)
    doc_year = models.IntegerField(blank=True, null=True)
    doc_number = models.CharField(max_length=10, blank=True, null=True)
    doc_item_number = models.CharField(max_length=3, null=True)
    create_date = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    created_by = models.CharField(max_length=20, blank=True, null=True, default="")
    update_date = models.DateTimeField(blank=True, null=True)
    updated_by = models.CharField(max_length=20, blank=True, null=True, default="")

    business_area_obj = models.ForeignKey(BusinessArea, on_delete=models.SET_NULL, null=True, blank=True)
    business_office_code = models.CharField(max_length=4, blank=True, null=True)
