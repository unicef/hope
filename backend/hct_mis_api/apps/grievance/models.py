from django.conf import settings
from django.db import models

from utils.models import TimeStampedUUIDModel
from django.utils.translation import ugettext_lazy as _


class GrievanceTicket(TimeStampedUUIDModel):
    STATUS_OPEN = 1
    STATUS_REOPENED = 2
    STATUS_RESOLVED = 3
    STATUS_CLOSED = 4
    STATUS_DUPLICATE = 5

    TYPE_PAYMENT_VERIFICATION = 1
    TYPE_DATA_CHANGE = 2
    TYPE_SENSITIVE_GRIEVANCE = 3
    TYPE_GRIEVANCE_COMPLAINT = 4
    TYPE_NEGATIVE_FEEDBACK = 5
    TYPE_REFERRAL = 6
    TYPE_POSITIVE_FEEDBACK = 7
    TYPE_DEDUPLICATION = 8

    STATUS_CHOICES = (
        (STATUS_OPEN, _("Open")),
        (STATUS_REOPENED, _("Reopened")),
        (STATUS_RESOLVED, _("Resolved")),
        (STATUS_CLOSED, _("Closed")),
        (STATUS_DUPLICATE, _("Duplicate")),
    )

    TYPE_CHOICES = (
        (TYPE_PAYMENT_VERIFICATION, _("Payment Verification")),
        (TYPE_DATA_CHANGE, _("Data Change")),
        (TYPE_SENSITIVE_GRIEVANCE, _("Sensitive Grievance")),
        (TYPE_GRIEVANCE_COMPLAINT, _("Grievance Complaint")),
        (TYPE_NEGATIVE_FEEDBACK, _("Negative Feedback")),
        (TYPE_REFERRAL, _("Referral")),
        (TYPE_POSITIVE_FEEDBACK, _("Positive Feedback")),
        (TYPE_DEDUPLICATION, _("Deduplication")),
    )
    user_modified = models.DateTimeField(
        _("Modified"),
        blank=True,
        help_text=_("Date this ticket was most recently changed."),
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="created_tickets",
        blank=True,
        null=True,
        verbose_name=_("Assigned to"),
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="assigned_tickets",
        blank=True,
        null=True,
        verbose_name=_("Assigned to"),
    )
    status = models.IntegerField(
        _("Status"),
        choices=STATUS_CHOICES,
        default=STATUS_OPEN,
    )
    type = models.IntegerField(
        _("Type"),
        choices=TYPE_CHOICES,
    )
    description = models.TextField(
        _("Description"),
        blank=True,
        null=True,
        help_text=_("The content of the customers query."),
    )
    admin = models.CharField(max_length=250)
    area = models.CharField(max_length=250)
    language = models.CharField(max_length=250)
    consent = models.BooleanField(default=False)
    business_area = models.ForeignKey("core.BusinessArea", "tickets")


class TicketNotes(TimeStampedUUIDModel):
    description = models.TextField(
        _("Description"),
        blank=True,
        null=True,
        help_text=_("The content of the customers query."),
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="ticket_notes",
        blank=True,
        null=True,
        verbose_name=_("Assigned to"),
    )


class TicketDeduplicationDetails(TimeStampedUUIDModel):
    ticket = models.OneToOneField(
        "grievance.GrievanceTicket", related_name="deduplication_details", on_delete=models.CASCADE
    )
    individual = models.ForeignKey(
        "household.Individual", related_name="ticket_details", null=True, on_delete=models.CASCADE
    )
    duplicated_individuals = models.ManyToManyField("household.Individual", related_name="duplicates_ticket_details")


class TicketPaymentVerificationDetails(TimeStampedUUIDModel):
    ticket = models.OneToOneField(
        "grievance.GrievanceTicket", related_name="payment_verification_details", on_delete=models.CASCADE
    )
    payment_verification = models.ForeignKey(
        "payment.PaymentVerification", related_name="ticket_details", on_delete=models.CASCADE
    )
