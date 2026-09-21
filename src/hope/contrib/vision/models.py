from django.db import models
from django.db.models import OuterRef, Subquery, Sum

from hope.models import BusinessArea, PaymentPlan


class FundsCommitmentHeaderQuerySet(models.QuerySet):
    def with_derived_fields(self) -> "FundsCommitmentHeaderQuerySet":
        matching_commitments = FundsCommitment.objects.filter(
            funds_commitment_number=OuterRef("funds_commitment_number")
        ).order_by("rec_serial_number")
        totals = (
            FundsCommitment.objects.filter(funds_commitment_number=OuterRef("funds_commitment_number"))
            .values("funds_commitment_number")
            .annotate(
                total_amount_usd=Sum("commitment_amount_usd"),
                total_amount_local=Sum("commitment_amount_local"),
            )
        )
        amount_field = models.DecimalField(max_digits=15, decimal_places=2)

        return self.annotate(
            rec_serial_number=Subquery(
                matching_commitments.values("rec_serial_number")[:1],
                output_field=models.IntegerField(),
            ),
            vendor_id=Subquery(
                matching_commitments.values("vendor_id")[:1],
                output_field=models.CharField(max_length=10),
            ),
            posting_date=Subquery(
                matching_commitments.values("posting_date")[:1],
                output_field=models.DateField(),
            ),
            document_reference=Subquery(
                matching_commitments.values("document_reference")[:1],
                output_field=models.CharField(max_length=16),
            ),
            fc_status=Subquery(
                matching_commitments.values("fc_status")[:1],
                output_field=models.CharField(max_length=1),
            ),
            total_amount_usd=Subquery(
                totals.values("total_amount_usd")[:1],
                output_field=amount_field,
            ),
            total_amount_local=Subquery(
                totals.values("total_amount_local")[:1],
                output_field=amount_field,
            ),
            currency=Subquery(
                matching_commitments.values("currency_code")[:1],
                output_field=models.CharField(max_length=5),
            ),
        )


class FundsCommitmentHeader(models.Model):
    funds_commitment_number = models.CharField(max_length=10)
    objects = FundsCommitmentHeaderQuerySet.as_manager()

    class Meta:
        verbose_name = "Funds Commitment Header"
        verbose_name_plural = "Funds Commitment Headers"

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
    funds_commitment_header = models.ForeignKey(
        FundsCommitmentHeader,
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
        return f"{self.funds_commitment_header} - {self.funds_commitment_item}"


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
        return self.funds_commitment_number or ""


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

    def __str__(self) -> str:
        return str(self.rec_serial_number)
