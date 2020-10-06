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

    CATEGORY_PAYMENT_VERIFICATION = 1
    CATEGORY_DATA_CHANGE = 2
    CATEGORY_SENSITIVE_GRIEVANCE = 3
    CATEGORY_GRIEVANCE_COMPLAINT = 4
    CATEGORY_NEGATIVE_FEEDBACK = 5
    CATEGORY_REFERRAL = 6
    CATEGORY_POSITIVE_FEEDBACK = 7
    CATEGORY_DEDUPLICATION = 8

    SUBCATEGORY_DATA_CHANGE_DATA_UPDATE = 1
    SUBCATEGORY_DATA_CHANGE_DELETE_INDIVIDUAL = 2
    SUBCATEGORY_DATA_CHANGE_ADD_INDIVIDUAL = 3
    SUBCATEGORY_CHOICES = {
        CATEGORY_DATA_CHANGE:{
            SUBCATEGORY_DATA_CHANGE_DATA_UPDATE: _("Da")
        }
    }
    STATUS_CHOICES = (
        (STATUS_OPEN, _("Open")),
        (STATUS_REOPENED, _("Reopened")),
        (STATUS_RESOLVED, _("Resolved")),
        (STATUS_CLOSED, _("Closed")),
        (STATUS_DUPLICATE, _("Duplicate")),
    )

    CATEGORY_CHOICES = (
        (CATEGORY_PAYMENT_VERIFICATION, _("Payment Verification")),
        (CATEGORY_DATA_CHANGE, _("Data Change")),
        (CATEGORY_SENSITIVE_GRIEVANCE, _("Sensitive Grievance")),
        (CATEGORY_GRIEVANCE_COMPLAINT, _("Grievance Complaint")),
        (CATEGORY_NEGATIVE_FEEDBACK, _("Negative Feedback")),
        (CATEGORY_REFERRAL, _("Referral")),
        (CATEGORY_POSITIVE_FEEDBACK, _("Positive Feedback")),
        (CATEGORY_DEDUPLICATION, _("Deduplication")),
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
    category = models.IntegerField(
        _("Category"),
        choices=CATEGORY_CHOICES,
    )
    subcategory = models.IntegerField(
        _("Type"),
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
