from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from hope.apps.activity_log.utils import create_mapping_dict
from hope.models.utils import AdminUrlMixin, TimeStampedUUIDModel, UnicefIdentifiedModel


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
        "payment.PaymentPlan",
        related_name="messages",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    registration_data_import = models.ForeignKey(
        "registration_data.RegistrationDataImport",
        related_name="messages",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    # Sampling (storing sampling params might not be needed)
    sampling_type = models.CharField(
        max_length=50,
        choices=SamplingChoices.choices,
        default=SamplingChoices.FULL_LIST,
    )
    full_list_arguments = models.JSONField(blank=True, null=True)
    random_sampling_arguments = models.JSONField(blank=True, null=True)
    sample_size = models.PositiveIntegerField(default=0)
    program = models.ForeignKey(
        "program.Program",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="messages",
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
        app_label = "accountability"
        ordering = ("created_at",)
        verbose_name = _("Message")

    def __str__(self) -> str:
        return f"{self.title} ({self.number_of_recipients} recipients)"
