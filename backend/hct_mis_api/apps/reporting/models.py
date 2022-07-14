from django.utils import timezone


from django.db import models
from django.utils.translation import gettext_lazy as _

from hct_mis_api.apps.account.models import ChoiceArrayField
from hct_mis_api.apps.utils.models import TimeStampedUUIDModel


class Report(TimeStampedUUIDModel):
    IN_PROGRESS = 1
    COMPLETED = 2
    FAILED = 3
    STATUSES = (
        (IN_PROGRESS, _("Processing")),
        (COMPLETED, _("Generated")),
        (FAILED, _("Failed")),
    )

    INDIVIDUALS = 1
    HOUSEHOLD_DEMOGRAPHICS = 2
    CASH_PLAN_VERIFICATION = 3
    PAYMENTS = 4
    PAYMENT_VERIFICATION = 5
    CASH_PLAN = 6
    PROGRAM = 7
    INDIVIDUALS_AND_PAYMENT = 8
    GRIEVANCES = 9
    REPORT_TYPES = (
        (INDIVIDUALS, _("Individuals")),
        (HOUSEHOLD_DEMOGRAPHICS, _("Households")),
        (CASH_PLAN_VERIFICATION, _("Cash Plan Verification")),
        (PAYMENTS, _("Payments")),
        (PAYMENT_VERIFICATION, _("Payment verification")),
        (CASH_PLAN, _("Cash Plan")),
        (PROGRAM, _("Programme")),
        (INDIVIDUALS_AND_PAYMENT, _("Individuals & Payment")),
        (GRIEVANCES, _("Grievances")),
    )

    business_area = models.ForeignKey("core.BusinessArea", related_name="reports", on_delete=models.CASCADE)
    file = models.FileField(blank=True, null=True)
    created_by = models.ForeignKey("account.User", related_name="reports", on_delete=models.CASCADE)
    status = models.IntegerField(choices=STATUSES, default=IN_PROGRESS)
    report_type = models.IntegerField(choices=REPORT_TYPES)
    date_from = models.DateField()
    date_to = models.DateField()
    number_of_records = models.IntegerField(blank=True, null=True)
    # any of these are optional and their requirements will depend on report type
    program = models.ForeignKey(
        "program.Program",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="reports",
    )
    admin_area = models.ManyToManyField("core.AdminArea", blank=True, related_name="reports")
    admin_area_new = models.ManyToManyField("geo.Area", blank=True, related_name="reports")

    def __str__(self):
        return f"[{self.report_type}] Report for [{self.business_area}]"

    class Meta:
        ordering = ["-created_at", "report_type", "status", "created_by"]


class DashboardReport(TimeStampedUUIDModel):
    IN_PROGRESS = 1
    COMPLETED = 2
    FAILED = 3
    STATUSES = (
        (IN_PROGRESS, _("Processing")),
        (COMPLETED, _("Generated")),
        (FAILED, _("Failed")),
    )

    TOTAL_TRANSFERRED_BY_COUNTRY = "TOTAL_TRANSFERRED_BY_COUNTRY"
    TOTAL_TRANSFERRED_BY_ADMIN_AREA = "TOTAL_TRANSFERRED_BY_ADMIN_AREA"
    BENEFICIARIES_REACHED = "BENEFICIARIES_REACHED"
    INDIVIDUALS_REACHED = "INDIVIDUALS_REACHED"
    VOLUME_BY_DELIVERY_MECHANISM = "VOLUME_BY_DELIVERY_MECHANISM"
    GRIEVANCES_AND_FEEDBACK = "GRIEVANCES_AND_FEEDBACK"
    PROGRAMS = "PROGRAMS"
    PAYMENT_VERIFICATION = "PAYMENT_VERIFICATION"
    REPORT_TYPES = (
        (TOTAL_TRANSFERRED_BY_COUNTRY, _("Total transferred by country")),
        (TOTAL_TRANSFERRED_BY_ADMIN_AREA, _("Total transferred by admin area")),
        (BENEFICIARIES_REACHED, _("Beneficiaries reached")),
        (INDIVIDUALS_REACHED, _("Individuals reached drilldown")),
        (VOLUME_BY_DELIVERY_MECHANISM, _("Volume by delivery mechanism")),
        (GRIEVANCES_AND_FEEDBACK, _("Grievances and Feedback")),
        (PROGRAMS, _("Programmes")),
        (PAYMENT_VERIFICATION, _("Payment verification")),
    )

    business_area = models.ForeignKey("core.BusinessArea", related_name="dashboard_reports", on_delete=models.CASCADE)
    file = models.FileField(blank=True, null=True)
    created_by = models.ForeignKey("account.User", related_name="dashboard_reports", on_delete=models.CASCADE)
    status = models.PositiveSmallIntegerField(choices=STATUSES, default=IN_PROGRESS)
    report_type = ChoiceArrayField(models.CharField(choices=REPORT_TYPES, max_length=255))

    # filters
    year = models.PositiveSmallIntegerField(default=timezone.now().year)
    program = models.ForeignKey(
        "program.Program",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="dashboard_reports",
    )
    admin_area = models.ForeignKey(
        "core.AdminArea",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="dashboard_reports",
    )
    admin_area_new = models.ForeignKey(
        "geo.Area",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="dashboard_reports",
    )
