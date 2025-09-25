from django.db import models

from hope.models.business_area import BusinessArea
from hope.models.payment_plan import PaymentPlan


class FundsCommitmentGroup(models.Model):
    funds_commitment_number = models.CharField(max_length=10)

    def __str__(self) -> str:
        return self.funds_commitment_number


class FundsCommitmentItem(models.Model):
    payment_plan = models.ForeignKey(
        PaymentPlan,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="funds_commitments",
    )
    funds_commitment_group = models.ForeignKey(
        FundsCommitmentGroup,
        on_delete=models.CASCADE,
        related_name="funds_commitment_items",
    )
    funds_commitment_item = models.CharField(max_length=3, db_index=True)

    rec_serial_number = models.IntegerField(primary_key=True)
    vendor_id = models.CharField(max_length=10, blank=True, null=True)
    business_area = models.CharField(max_length=4, blank=True, null=True)
    posting_date = models.DateField(blank=True, null=True)
    vision_approval = models.CharField(max_length=1, blank=True, null=True)
    document_reference = models.CharField(max_length=16, null=True)
    fc_status = models.CharField(max_length=1, blank=True, null=True)
    wbs_element = models.CharField(max_length=24, null=True, blank=True, default="")
    grant_number = models.CharField(max_length=20, null=True, blank=True, default="")
    document_type = models.CharField(max_length=2, blank=True, null=True)
    document_text = models.CharField(max_length=50, blank=True, null=True)
    currency_code = models.CharField(max_length=5, blank=True, null=True)
    gl_account = models.CharField(max_length=10, null=True, blank=True)
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

    sponsor = models.CharField(max_length=10, null=True, blank=True, default="")
    sponsor_name = models.CharField(max_length=100, null=True, blank=True, default="")
    fund = models.CharField(max_length=10, null=True, blank=True, default="")
    funds_center = models.CharField(max_length=16, null=True, blank=True, default="")
    percentage = models.DecimalField(decimal_places=2, max_digits=5, null=True, blank=True)

    create_date = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    created_by = models.CharField(max_length=20, null=True, blank=True, default="")
    update_date = models.DateTimeField(null=True, blank=True)
    updated_by = models.CharField(max_length=20, blank=True, null=True, default="")

    office = models.ForeignKey(
        BusinessArea,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="This can be a business office or a business area",
    )

    def __str__(self) -> str:
        return f"{self.funds_commitment_group} - {self.funds_commitment_item}"


class FundsCommitment(models.Model):
    rec_serial_number = models.IntegerField(primary_key=True)
    funds_commitment_number = models.CharField(max_length=10, blank=True, null=True)
    vendor_id = models.CharField(max_length=10, blank=True, null=True)
    business_area = models.CharField(max_length=4, blank=True, null=True)
    posting_date = models.DateField(blank=True, null=True)
    vision_approval = models.CharField(max_length=1, blank=True, null=True)
    document_reference = models.CharField(max_length=16, null=True)
    fc_status = models.CharField(max_length=1, blank=True, null=True)
    funds_commitment_item = models.CharField(max_length=3, null=True, blank=True, default="")
    wbs_element = models.CharField(max_length=24, null=True, blank=True, default="")
    grant_number = models.CharField(max_length=20, null=True, blank=True, default="")
    document_type = models.CharField(max_length=2, blank=True, null=True)
    document_text = models.CharField(max_length=50, blank=True, null=True)
    currency_code = models.CharField(max_length=5, blank=True, null=True)
    gl_account = models.CharField(max_length=10, null=True, blank=True)
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

    sponsor = models.CharField(max_length=10, null=True, blank=True, default="")
    sponsor_name = models.CharField(max_length=100, null=True, blank=True, default="")
    fund = models.CharField(max_length=10, null=True, blank=True, default="")
    funds_center = models.CharField(max_length=16, null=True, blank=True, default="")
    percentage = models.DecimalField(decimal_places=2, max_digits=5, null=True, blank=True)

    create_date = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    created_by = models.CharField(max_length=20, null=True, blank=True, default="")
    update_date = models.DateTimeField(null=True, blank=True)
    updated_by = models.CharField(max_length=20, blank=True, null=True, default="")

    office = models.ForeignKey(
        BusinessArea,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="This can be a business office or a business area",
    )

    def __str__(self) -> str:
        return self.funds_commitment_number


class DownPayment(models.Model):
    rec_serial_number = models.IntegerField(primary_key=True)
    business_area = models.CharField(max_length=4)
    down_payment_reference = models.CharField(max_length=20)
    document_type = models.CharField(max_length=10)
    consumed_fc_number = models.CharField(max_length=10)
    consumed_fc_item_number = models.CharField(max_length=3, null=True, blank=True)
    currency_code = models.CharField(max_length=5, blank=True, null=True)
    posting_date = models.DateField(blank=True, null=True)
    doc_year = models.IntegerField(blank=True, null=True)
    doc_number = models.CharField(max_length=10, blank=True, null=True)
    doc_item_number = models.CharField(max_length=3, null=True)

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

    create_date = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    created_by = models.CharField(max_length=20, blank=True, null=True, default="")
    update_date = models.DateTimeField(blank=True, null=True)
    updated_by = models.CharField(max_length=20, blank=True, null=True, default="")

    office = models.ForeignKey(
        BusinessArea,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="This can be a business office or a business area",
    )

    def __str__(self):
        return str(self.rec_serial_number)
