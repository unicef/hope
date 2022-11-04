from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from hct_mis_api.apps.activity_log.utils import create_mapping_dict
from hct_mis_api.apps.utils.models import TimeStampedUUIDModel, UnicefIdentifiedModel


class Message(TimeStampedUUIDModel, UnicefIdentifiedModel):
    ACTIVITY_LOG_MAPPING = create_mapping_dict(
        [
            "title",
            "body",
            "business_area",
            "households",
            "target_population",
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
    target_population = models.ForeignKey(
        "targeting.TargetPopulation", related_name="messages", blank=True, null=True, on_delete=models.SET_NULL
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

    class Meta:
        ordering = ("created_at",)
        verbose_name = _("Message")

    def __str__(self) -> str:
        return f"{self.title} ({self.number_of_recipients} recipients)"


class Feedback(TimeStampedUUIDModel, UnicefIdentifiedModel):
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

    business_area = models.ForeignKey("core.BusinessArea", on_delete=models.CASCADE)
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
    description = models.TextField()
    comments = models.TextField(blank=True, null=True)
    admin2 = models.ForeignKey("geo.Area", null=True, blank=True, on_delete=models.SET_NULL)
    area = models.CharField(max_length=250, blank=True)
    language = models.TextField(blank=True)
    consent = models.BooleanField(default=True)
    program = models.ForeignKey("program.Program", null=True, blank=True, on_delete=models.CASCADE)
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


class Survey(UnicefIdentifiedModel, TimeStampedUUIDModel):
    SAMPLE_FILE_EXPIRATION_IN_DAYS = 30
    ACTIVITY_LOG_MAPPING = create_mapping_dict(
        [
            "title",
            "category",
            "number_of_recipient",
            "created_by",
            "target_population",
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
    target_population = models.ForeignKey(
        "targeting.TargetPopulation", related_name="surveys", blank=True, null=True, on_delete=models.SET_NULL
    )
    program = models.ForeignKey(
        "program.Program",
        related_name="surveys",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    business_area = models.ForeignKey("core.BusinessArea", on_delete=models.CASCADE)
    sample_file = models.FileField(upload_to="", blank=True, null=True)
    sample_file_generated_at = models.DateTimeField(blank=True, null=True)

    sampling_type = models.CharField(max_length=50, choices=SAMPLING_CHOICES, default=SAMPLING_FULL_LIST)
    full_list_arguments = models.JSONField(default=dict)
    random_sampling_arguments = models.JSONField(default=dict)
    sample_size = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("created_at",)
        verbose_name = _("Survey")

    def __str__(self):
        return self.title

    def sample_file_path(self):
        if not self.sample_file:
            return None
        if not self.has_valid_sample_file():
            raise SampleFileExpiredException()
        return self.sample_file.url

    def has_valid_sample_file(self) -> bool:
        return self.sample_file and self.sample_file_generated_at >= timezone.now() - timedelta(
            days=self.SAMPLE_FILE_EXPIRATION_IN_DAYS
        )

    def store_sample_file(self, filename, file):
        self.sample_file.save(filename, file)
        self.sample_file_generated_at = timezone.now()
        self.save()
