from datetime import timedelta
from typing import Optional

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.core.files import File
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from hct_mis_api.apps.activity_log.utils import create_mapping_dict
from hct_mis_api.apps.utils.models import (AdminUrlMixin, TimeStampedUUIDModel,
                                           UnicefIdentifiedModel)


class Message(TimeStampedUUIDModel, AdminUrlMixin, UnicefIdentifiedModel):
    ACTIVITY_LOG_MAPPING = create_mapping_dict(
        [
            "title",
            "body",
            "business_area",
            "households",
            "payment_plan",
            "registration_data_import",
            "sampling_type",
            "full_list_arguments",
            "random_sampling_arguments",
            "sample_size",
        ]
    )

    class SamplingChoices(models.TextChoices):
        FULL_LIST = "FULL_LIST", _("Full list")
        RANDOM = "RANDOM", _("Random sampling")

    title = models.CharField(max_length=60)
    body = models.TextField(max_length=1000)  # SMS messages are limited to 160 characters
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="messages",
        null=True,
        blank=True,
        verbose_name=_("Created by"),
    )
    number_of_recipients = models.PositiveIntegerField(default=0)  # count of Recipient objects after querying
    # To check permissions and create Activity Log
    business_area = models.ForeignKey("core.BusinessArea", on_delete=models.CASCADE)
    # Recipients Lookup criteria
    households = models.ManyToManyField("household.Household", related_name="messages", blank=True)
    payment_plan = models.ForeignKey(
        "payment.PaymentPlan", related_name="messages", blank=True, null=True, on_delete=models.SET_NULL
    )
    registration_data_import = models.ForeignKey(
        "registration_data.RegistrationDataImport",
        related_name="messages",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    # Sampling (storing sampling params might not be needed)
    sampling_type = models.CharField(max_length=50, choices=SamplingChoices.choices, default=SamplingChoices.FULL_LIST)
    full_list_arguments = models.JSONField(blank=True, null=True)
    random_sampling_arguments = models.JSONField(blank=True, null=True)
    sample_size = models.PositiveIntegerField(default=0)
    program = models.ForeignKey(
        "program.Program", null=True, blank=True, on_delete=models.CASCADE, related_name="messages"
    )
    copied_from = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="copied_to",
        help_text="If this object was copied from another, this field will contain the object it was copied from.",
    )

    class Meta:
        ordering = ("created_at",)
        verbose_name = _("Message")

    def __str__(self) -> str:
        return f"{self.title} ({self.number_of_recipients} recipients)"


class Feedback(TimeStampedUUIDModel, AdminUrlMixin, UnicefIdentifiedModel):
    ACTIVITY_LOG_MAPPING = create_mapping_dict(
        [
            "description",
            "comments",
            "admin2",
            "area",
            "language",
            "program",
            "linked_grievance",
        ]
    )

    POSITIVE_FEEDBACK = "POSITIVE_FEEDBACK"
    NEGATIVE_FEEDBACK = "NEGATIVE_FEEDBACK"

    ISSUE_TYPE_CHOICES = (
        (POSITIVE_FEEDBACK, _("Positive feedback")),
        (NEGATIVE_FEEDBACK, _("Negative feedback")),
    )

    issue_type = models.CharField(verbose_name=_("Issue type"), choices=ISSUE_TYPE_CHOICES, max_length=20)
    household_lookup = models.ForeignKey(
        "household.Household",
        related_name="feedbacks",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Household lookup"),
    )
    individual_lookup = models.ForeignKey(
        "household.Individual",
        related_name="feedbacks",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Individual lookup"),
    )
    business_area = models.ForeignKey("core.BusinessArea", on_delete=models.CASCADE)
    program = models.ForeignKey("program.Program", null=True, blank=True, on_delete=models.CASCADE)
    area = models.CharField(max_length=250, blank=True)
    admin2 = models.ForeignKey("geo.Area", null=True, blank=True, on_delete=models.SET_NULL)
    description = models.TextField()
    language = models.TextField(blank=True)
    comments = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="feedbacks",
        null=True,
        blank=True,
        verbose_name=_("Created by"),
    )
    linked_grievance = models.OneToOneField(
        "grievance.GrievanceTicket",
        on_delete=models.SET_NULL,
        related_name="feedback",
        null=True,
        blank=True,
        verbose_name=_("Linked grievance"),
    )
    consent = models.BooleanField(default=True)
    copied_from = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="copied_to",
        help_text="If this object was copied from another, this field will contain the object it was copied from.",
    )

    class Meta:
        ordering = ("created_at",)
        verbose_name = _("Feedback")


class FeedbackMessage(TimeStampedUUIDModel):
    description = models.TextField(
        verbose_name=_("Description"),
        help_text=_("The content of the feedback message."),
    )
    feedback = models.ForeignKey(
        Feedback,
        related_name="feedback_messages",
        on_delete=models.CASCADE,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="feedback_messages",
        blank=True,
        null=True,
        verbose_name=_("Created by"),
    )

    class Meta:
        ordering = ("created_at",)
        verbose_name = _("Feedback message")


class SampleFileExpiredException(Exception):
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
        "payment.PaymentPlan", related_name="surveys", blank=True, null=True, on_delete=models.SET_NULL
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
        ordering = ("created_at",)
        verbose_name = _("Survey")

    def __str__(self) -> str:
        return self.title

    def sample_file_path(self) -> Optional[str]:
        if not self.sample_file:
            return None
        if not self.has_valid_sample_file():
            raise SampleFileExpiredException()
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
