from datetime import timedelta

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.core.files import File
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from hope.apps.activity_log.utils import create_mapping_dict
from hope.models.utils import (
    AdminUrlMixin,
    TimeStampedUUIDModel,
    UnicefIdentifiedModel,
)


class SampleFileExpiredError(Exception):
    pass


class Survey(UnicefIdentifiedModel, AdminUrlMixin, TimeStampedUUIDModel):
    SAMPLE_FILE_EXPIRATION_IN_DAYS = 30
    ACTIVITY_LOG_MAPPING = create_mapping_dict(
        [
            "title",
            "category",
            "number_of_recipient",
            "created_by",
            "payment_plan",
            "program",
            "sampling_type",
            "full_list_arguments",
            "random_sampling_arguments",
            "sample_size",
        ]
    )

    CATEGORY_RAPID_PRO = "RAPID_PRO"
    CATEGORY_SMS = "SMS"
    CATEGORY_MANUAL = "MANUAL"
    CATEGORY_CHOICES = (
        (CATEGORY_RAPID_PRO, _("Survey with RapidPro")),
        (CATEGORY_SMS, _("Survey with SMS")),
        (CATEGORY_MANUAL, _("Survey with manual process")),
    )

    SAMPLING_FULL_LIST = "FULL_LIST"
    SAMPLING_RANDOM = "RANDOM"
    SAMPLING_CHOICES = (
        (SAMPLING_FULL_LIST, _("Full list")),
        (SAMPLING_RANDOM, _("Random")),
    )

    title = models.CharField(max_length=60)
    body = models.TextField(max_length=1000, blank=True, default="")
    category = models.CharField(max_length=16, choices=CATEGORY_CHOICES)
    number_of_recipients = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="surveys",
        null=True,
        blank=True,
        verbose_name=_("Created by"),
    )
    recipients = models.ManyToManyField("household.Household", related_name="surveys", blank=True)
    payment_plan = models.ForeignKey(
        "payment.PaymentPlan",
        related_name="surveys",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    program = models.ForeignKey(
        "program.Program",
        related_name="surveys",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    business_area = models.ForeignKey("core.BusinessArea", on_delete=models.CASCADE)
    flow_id = models.CharField(max_length=255, blank=True, null=True)

    sampling_type = models.CharField(max_length=50, choices=SAMPLING_CHOICES, default=SAMPLING_FULL_LIST)
    sample_size = models.PositiveIntegerField(default=0)
    sample_file = models.FileField(upload_to="", blank=True, null=True)
    sample_file_generated_at = models.DateTimeField(blank=True, null=True)

    full_list_arguments = models.JSONField(default=dict)
    random_sampling_arguments = models.JSONField(default=dict)
    successful_rapid_pro_calls = ArrayField(models.JSONField(), default=list)

    class Meta:
        app_label = "accountability"
        ordering = ("created_at",)
        verbose_name = _("Survey")

    def __str__(self) -> str:
        return self.title

    def sample_file_path(self) -> str | None:
        if not self.sample_file:
            return None
        if not self.has_valid_sample_file():
            raise SampleFileExpiredError()
        return self.sample_file.url

    def has_valid_sample_file(self) -> bool:
        expiration_date = timezone.now() - timedelta(days=self.SAMPLE_FILE_EXPIRATION_IN_DAYS)
        return (
            self.sample_file is not None
            and self.sample_file_generated_at
            and self.sample_file_generated_at >= expiration_date
        )

    def store_sample_file(self, filename: str, file: File) -> None:
        self.sample_file.save(filename, file)
        self.sample_file_generated_at = timezone.now()
        self.save()
