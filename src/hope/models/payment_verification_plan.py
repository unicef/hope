import logging
from typing import TYPE_CHECKING, Any, Optional

from django.contrib.admin.options import get_content_type_for_model
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import JSONField
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from hope.apps.activity_log.utils import create_mapping_dict
from hope.models.business_area import BusinessArea
from hope.models.file_temp import FileTemp
from hope.models.payment_verification_summary import build_summary
from hope.models.utils import (
    AdminUrlMixin,
    ConcurrencyModel,
    TimeStampedUUIDModel,
    UnicefIdentifiedModel,
)

if TYPE_CHECKING:
    from hope.models.program import Program

logger = logging.getLogger(__name__)


class PaymentVerificationPlan(TimeStampedUUIDModel, ConcurrencyModel, UnicefIdentifiedModel, AdminUrlMixin):
    ACTIVITY_LOG_MAPPING = create_mapping_dict(
        [
            "status",
            "payment_plan",
            "sampling",
            "verification_channel",
            "sample_size",
            "responded_count",
            "received_count",
            "not_received_count",
            "received_with_problems_count",
            "confidence_interval",
            "margin_of_error",
            "rapid_pro_flow_id",
            "rapid_pro_flow_start_uuids",
            "age_filter",
            "excluded_admin_areas_filter",
            "sex_filter",
            "activation_date",
            "completion_date",
        ]
    )
    STATUS_PENDING = "PENDING"
    STATUS_ACTIVE = "ACTIVE"
    STATUS_FINISHED = "FINISHED"
    STATUS_INVALID = "INVALID"
    STATUS_RAPID_PRO_ERROR = "RAPID_PRO_ERROR"
    SAMPLING_FULL_LIST = "FULL_LIST"
    SAMPLING_RANDOM = "RANDOM"
    VERIFICATION_CHANNEL_RAPIDPRO = "RAPIDPRO"
    VERIFICATION_CHANNEL_XLSX = "XLSX"
    VERIFICATION_CHANNEL_MANUAL = "MANUAL"
    STATUS_CHOICES = (
        (STATUS_ACTIVE, "Active"),
        (STATUS_FINISHED, "Finished"),
        (STATUS_PENDING, "Pending"),
        (STATUS_INVALID, "Invalid"),
        (STATUS_RAPID_PRO_ERROR, "RapidPro Error"),
    )
    SAMPLING_CHOICES = (
        (SAMPLING_FULL_LIST, "Full list"),
        (SAMPLING_RANDOM, "Random sampling"),
    )
    VERIFICATION_CHANNEL_CHOICES = (
        (VERIFICATION_CHANNEL_MANUAL, "MANUAL"),
        (VERIFICATION_CHANNEL_RAPIDPRO, "RAPIDPRO"),
        (VERIFICATION_CHANNEL_XLSX, "XLSX"),
    )

    payment_plan = models.ForeignKey(
        "payment.PaymentPlan",
        on_delete=models.CASCADE,
        related_name="payment_verification_plans",
    )
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=STATUS_PENDING, db_index=True)
    verification_channel = models.CharField(max_length=50, choices=VERIFICATION_CHANNEL_CHOICES)

    sampling = models.CharField(max_length=50, choices=SAMPLING_CHOICES)
    sex_filter = models.CharField(null=True, max_length=10, blank=True)
    activation_date = models.DateTimeField(null=True)
    completion_date = models.DateTimeField(null=True)
    sample_size = models.PositiveIntegerField(null=True, blank=True)
    responded_count = models.PositiveIntegerField(null=True, blank=True)
    received_count = models.PositiveIntegerField(null=True, blank=True)
    not_received_count = models.PositiveIntegerField(null=True, blank=True)
    received_with_problems_count = models.PositiveIntegerField(null=True, blank=True)
    confidence_interval = models.FloatField(null=True, blank=True)
    margin_of_error = models.FloatField(null=True, blank=True)

    rapid_pro_flow_id = models.CharField(max_length=255, blank=True)
    rapid_pro_flow_start_uuids = ArrayField(models.CharField(max_length=255, blank=True), default=list)

    xlsx_file_exporting = models.BooleanField(default=False)
    xlsx_file_imported = models.BooleanField(default=False)

    error = models.CharField(max_length=500, null=True, blank=True)
    age_filter = JSONField(null=True, blank=True)
    excluded_admin_areas_filter = JSONField(null=True, blank=True)

    class Meta:
        app_label = "payment"
        ordering = ("created_at",)

    @property
    def business_area(self) -> BusinessArea:
        return self.payment_plan.business_area

    @property
    def get_xlsx_verification_file(self) -> FileTemp:
        try:
            return FileTemp.objects.get(object_id=self.pk, content_type=get_content_type_for_model(self))
        except FileTemp.DoesNotExist:  # pragma: no cover
            raise ValidationError("Xlsx Verification File does not exist.")
        except FileTemp.MultipleObjectsReturned as e:  # pragma: no cover
            logger.warning(e)
            raise ValidationError("Query returned multiple Xlsx Verification Files when only one was expected.")

    @property
    def has_xlsx_payment_verification_plan_file(self) -> bool:
        # TODO: what if we have two or more files here ?<?>?
        return all(
            [
                self.verification_channel == self.VERIFICATION_CHANNEL_XLSX,
                FileTemp.objects.filter(object_id=self.pk, content_type=get_content_type_for_model(self)).count() == 1,
            ]
        )

    @property
    def xlsx_payment_verification_plan_file_link(self) -> str | None:
        return self.get_xlsx_verification_file.file.url if self.has_xlsx_payment_verification_plan_file else None

    @property
    def xlsx_payment_verification_plan_file_was_downloaded(self) -> bool:
        return self.get_xlsx_verification_file.was_downloaded if self.has_xlsx_payment_verification_plan_file else False

    def set_active(self) -> None:
        self.status = PaymentVerificationPlan.STATUS_ACTIVE
        self.activation_date = timezone.now()
        self.error = None

    def set_pending(self) -> None:
        self.status = PaymentVerificationPlan.STATUS_PENDING
        self.responded_count = None
        self.received_count = None
        self.not_received_count = None
        self.received_with_problems_count = None
        self.activation_date = None
        self.rapid_pro_flow_start_uuids = []

    def can_activate(self) -> bool:
        return self.status not in (
            PaymentVerificationPlan.STATUS_PENDING,
            PaymentVerificationPlan.STATUS_RAPID_PRO_ERROR,
        )

    @property
    def get_program(self) -> Optional["Program"]:
        return self.payment_plan.program_cycle.program


@receiver(
    post_save,
    sender=PaymentVerificationPlan,
    dispatch_uid="update_verification_status_in_cash_plan",
)
def update_verification_status_in_cash_plan(sender: Any, instance: PaymentVerificationPlan, **kwargs: Any) -> None:
    build_summary(instance.payment_plan)


@receiver(
    post_delete,
    sender=PaymentVerificationPlan,
    dispatch_uid="update_verification_status_in_cash_plan_on_delete",
)
def update_verification_status_in_cash_plan_on_delete(
    sender: Any, instance: PaymentVerificationPlan, **kwargs: Any
) -> None:
    build_summary(instance.payment_plan)
