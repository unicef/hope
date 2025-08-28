from hope.apps.activity_log.utils import create_mapping_dict
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from hope.models.utils import TimeStampedUUIDModel, AdminUrlMixin, UnicefIdentifiedModel


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
        app_label = "accountability"
        ordering = ("created_at",)
        verbose_name = _("Feedback")
