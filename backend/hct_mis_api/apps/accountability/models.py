from django.conf import settings
from django.db import models
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

    def __str__(self) -> str:
        return f"{self.title} ({self.number_of_recipients} recipients)"


class Feedback(TimeStampedUUIDModel, UnicefIdentifiedModel):
    # TODO
    # ACTIVITY_LOG_MAPPING =

    POSITIVE_FEEDBACK = 1
    NEGATIVE_FEEDBACK = 2

    ISSUE_TYPE_CHOICES = (
        (POSITIVE_FEEDBACK, _("Positive feedback")),
        (NEGATIVE_FEEDBACK, _("Negative feedback")),
    )

    business_area = models.ForeignKey("core.BusinessArea", on_delete=models.CASCADE)
    issue_type = models.IntegerField(verbose_name=_("Issue type"), choices=ISSUE_TYPE_CHOICES)
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
    linked_grievance = models.ForeignKey(
        "grievance.GrievanceTicket",
        on_delete=models.SET_NULL,
        related_name="feedbacks",
        null=True,
        blank=True,
        verbose_name=_("Linked grievance"),
    )
