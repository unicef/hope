from django.db import models
from django_countries.fields import CountryField
from django.utils.translation import ugettext_lazy as _

from utils.models import TimeStampedUUIDModel


class Report(TimeStampedUUIDModel):
    IN_PROGRESS = 1
    COMPLETED = 2
    FAILED = 3
    STATUSES = ((IN_PROGRESS, _("Processing")), (COMPLETED, _("Generated")), (FAILED, _("Failed")))

    INDIVIDUALS = 1
    HOUSEHOLD_DEMOGRAPHICS = 2
    CASH_PLAN_VERIFICATION = 3
    PAYMENTS = 4
    PAYMENT_VERIFICATION = 5
    CASH_PLAN = 6
    PROGRAM = 7
    INDIVIDUALS_AND_PAYMENT = 8
    REPORT_TYPES = (
        (INDIVIDUALS, _("Individuals")),
        (HOUSEHOLD_DEMOGRAPHICS, _("Household Demographics")),
        (CASH_PLAN_VERIFICATION, _("Cash Plan Verification")),
        (PAYMENTS, _("Payments")),
        (PAYMENT_VERIFICATION, _("Payment verification")),
        (CASH_PLAN, _("Cash Plan")),
        (PROGRAM, _("Program")),
        (INDIVIDUALS_AND_PAYMENT, _("Individuals and Payment")),
    )

    business_area = models.ForeignKey("core.BusinessArea", related_name="reports", on_delete=models.CASCADE)
    file = models.FileField(blank=True, null=True)
    created_by = models.ForeignKey("account.User", related_name="reports", on_delete=models.CASCADE)
    status = models.IntegerField(choices=STATUSES, default=IN_PROGRESS)
    report_type = models.IntegerField(choices=REPORT_TYPES)
    date_from = models.DateField()
    date_to = models.DateField()
    # any of these are optional and their requirements will depend on report type
    country = CountryField(blank=True, null=True)
    program = models.ForeignKey(
        "program.Program", on_delete=models.CASCADE, blank=True, null=True, related_name="reports"
    )
    admin_area = models.ForeignKey(
        "core.AdminArea", on_delete=models.CASCADE, blank=True, null=True, related_name="reports"
    )

    def __str__(self):
        return f"[{self.report_type}] Report for [{self.business_area}]"
