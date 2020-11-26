from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.core.exceptions import ValidationError
from django.db import models

from utils.models import TimeStampedUUIDModel
from django.utils.translation import ugettext_lazy as _


class GrievanceTicket(TimeStampedUUIDModel):
    STATUS_NEW = 1
    STATUS_ASSIGNED = 2
    STATUS_IN_PROGRESS = 3
    STATUS_ON_HOLD = 4
    STATUS_FOR_APPROVAL = 5
    STATUS_CLOSED = 6

    CATEGORY_PAYMENT_VERIFICATION = 1
    CATEGORY_DATA_CHANGE = 2
    CATEGORY_SENSITIVE_GRIEVANCE = 3
    CATEGORY_GRIEVANCE_COMPLAINT = 4
    CATEGORY_NEGATIVE_FEEDBACK = 5
    CATEGORY_REFERRAL = 6
    CATEGORY_POSITIVE_FEEDBACK = 7
    CATEGORY_DEDUPLICATION = 8

    ISSUE_TYPE_DATA_BREACH = 1
    ISSUE_TYPE_BRIBERY_CORRUPTION_KICKBACK = 2
    ISSUE_TYPE_FRAUD_FORGERY = 3
    ISSUE_TYPE_FRAUD_MISUSE = 4
    ISSUE_TYPE_HARASSMENT = 5
    ISSUE_TYPE_INAPPROPRIATE_STAFF_CONDUCT = 6
    ISSUE_TYPE_UNAUTHORIZED_USE = 7
    ISSUE_TYPE_CONFLICT_OF_INTEREST = 8
    ISSUE_TYPE_GROSS_MISMANAGEMENT = 9
    ISSUE_TYPE_PERSONAL_DISPUTES = 10
    ISSUE_TYPE_SEXUAL_HARASSMENT = 11
    ISSUE_TYPE_MISCELLANEOUS = 12

    ISSUE_TYPE_HOUSEHOLD_DATA_CHANGE_DATA_UPDATE = 13
    ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE = 14
    ISSUE_TYPE_DATA_CHANGE_DELETE_INDIVIDUAL = 15
    ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL = 16
    ISSUE_TYPES_CHOICES = {
        CATEGORY_DATA_CHANGE: {
            ISSUE_TYPE_HOUSEHOLD_DATA_CHANGE_DATA_UPDATE: _("Household Data Update"),
            ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE: _("Individual Data Update"),
            ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL: _("Add Individual"),
            ISSUE_TYPE_DATA_CHANGE_DELETE_INDIVIDUAL: _("Delete Individual"),
        },
        CATEGORY_SENSITIVE_GRIEVANCE: {
            ISSUE_TYPE_DATA_BREACH: _("Data breach"),
            ISSUE_TYPE_BRIBERY_CORRUPTION_KICKBACK: _("Bribery, corruption or kickback"),
            ISSUE_TYPE_FRAUD_FORGERY: _("Fraud and forgery"),
            ISSUE_TYPE_FRAUD_MISUSE: _("Fraud involving misuse of programme funds by third party"),
            ISSUE_TYPE_HARASSMENT: _("Harassment and abuse of authority"),
            ISSUE_TYPE_INAPPROPRIATE_STAFF_CONDUCT: _("Inappropriate staff conduct"),
            ISSUE_TYPE_UNAUTHORIZED_USE: _("Unauthorized use, misuse or waste of UNICEF property or funds"),
            ISSUE_TYPE_CONFLICT_OF_INTEREST: _("Conflict of interest"),
            ISSUE_TYPE_GROSS_MISMANAGEMENT: _("Gross mismanagement"),
            ISSUE_TYPE_PERSONAL_DISPUTES: _("Personal disputes"),
            ISSUE_TYPE_SEXUAL_HARASSMENT: _("Sexual harassment and sexual exploitation"),
            ISSUE_TYPE_MISCELLANEOUS: _("Miscellaneous"),
        },
    }
    ALL_ISSUE_TYPES = [choice for choices_group in ISSUE_TYPES_CHOICES.values() for choice in choices_group.items()]
    STATUS_CHOICES = (
        (STATUS_NEW, _("New")),
        (STATUS_ASSIGNED, _("Assigned")),
        (STATUS_IN_PROGRESS, _("In Progress")),
        (STATUS_ON_HOLD, _("On Hold")),
        (STATUS_FOR_APPROVAL, _("For Approval")),
        (STATUS_CLOSED, _("Closed")),
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
    MANUAL_CATEGORIES = (
        CATEGORY_DATA_CHANGE,
        CATEGORY_SENSITIVE_GRIEVANCE,
        CATEGORY_GRIEVANCE_COMPLAINT,
        CATEGORY_NEGATIVE_FEEDBACK,
        CATEGORY_REFERRAL,
        CATEGORY_POSITIVE_FEEDBACK,
    )

    SEARCH_TICKET_TYPES_LOOKUPS = {
        "complaint_ticket_details": (
            "individual",
            "household",
            "payment_record",
        ),
        "sensitive_ticket_details": (
            "individual",
            "household",
            "payment_record",
        ),
        "individual_data_update_ticket_details": ("individual", {"household": "individual__household"}),
        "add_individual_ticket_details": ("household",),
        "household_data_update_ticket_details": ("household",),
    }
    FIELD_TICKET_TYPES_LOOKUPS = {
        "complaint_ticket_details": (
            "individual",
            "household",
            "payment_record",
        ),
        "sensitive_ticket_details": (
            "individual",
            "household",
            "payment_record",
        ),
        "individual_data_update_ticket_details": ("individual", {"household": "household"}),
        "add_individual_ticket_details": ("household",),
        "household_data_update_ticket_details": ("household",),
        "delete_individual_ticket_details": ("individual",),
    }

    user_modified = models.DateTimeField(
        verbose_name=_("Modified"),
        null=True,
        blank=True,
        help_text=_("Date this ticket was most recently changed."),
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="created_tickets",
        null=True,
        verbose_name=_("Created by"),
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="assigned_tickets",
        null=True,
        verbose_name=_("Assigned to"),
    )
    status = models.IntegerField(verbose_name=_("Status"), choices=STATUS_CHOICES, default=STATUS_NEW)
    category = models.IntegerField(verbose_name=_("Category"), choices=CATEGORY_CHOICES)
    issue_type = models.IntegerField(verbose_name=_("Type"), null=True, blank=True)
    description = models.TextField(
        verbose_name=_("Description"),
        blank=True,
        help_text=_("The content of the customers query."),
    )
    admin = models.CharField(max_length=250, blank=True)
    area = models.CharField(max_length=250, blank=True)
    language = models.TextField()
    consent = models.BooleanField(default=True)
    business_area = models.ForeignKey("core.BusinessArea", related_name="tickets", on_delete=models.CASCADE)
    linked_tickets = models.ManyToManyField(to="GrievanceTicket", through="GrievanceTicketThrough", related_name="linked_tickets_related")

    @property
    def related_tickets(self):
        yield from self.linked_tickets.all()
        yield from self.linked_tickets_related.all()

    class Meta:
        ordering = (
            "status",
            "created_at",
        )

    def clean(self):
        issue_types = self.ISSUE_TYPES_CHOICES.get(self.category)
        should_contain_issue_types = bool(issue_types)
        has_invalid_issue_type = should_contain_issue_types is True and self.issue_type not in issue_types
        has_issue_type_for_category_without_issue_types = bool(should_contain_issue_types is False and self.issue_type)
        if has_invalid_issue_type or has_issue_type_for_category_without_issue_types:
            raise ValidationError({"issue_type": "Invalid issue type for selected category"})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class GrievanceTicketThrough(TimeStampedUUIDModel):
    main_ticket = models.ForeignKey(
        "GrievanceTicket", on_delete=models.CASCADE, related_name="grievance_tickets_through_main"
    )
    linked_ticket = models.ForeignKey(
        "GrievanceTicket", on_delete=models.CASCADE, related_name="grievance_tickets_through_linked"
    )


class TicketNote(TimeStampedUUIDModel):
    description = models.TextField(
        verbose_name=_("Description"),
        help_text=_("The content of the customers query."),
    )
    ticket = models.ForeignKey("grievance.GrievanceTicket", related_name="ticket_notes", on_delete=models.CASCADE)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="ticket_notes",
        blank=True,
        null=True,
        verbose_name=_("Created by"),
    )


class TicketComplaintDetails(TimeStampedUUIDModel):
    ticket = models.OneToOneField(
        "grievance.GrievanceTicket", related_name="complaint_ticket_details", on_delete=models.CASCADE
    )
    payment_record = models.ForeignKey(
        "payment.PaymentRecord",
        related_name="complaint_ticket_details",
        on_delete=models.CASCADE,
        null=True,
    )
    household = models.ForeignKey(
        "household.Household",
        related_name="complaint_ticket_details",
        on_delete=models.CASCADE,
        null=True,
    )
    individual = models.ForeignKey(
        "household.Individual",
        related_name="complaint_ticket_details",
        on_delete=models.CASCADE,
        null=True,
    )


class TicketSensitiveDetails(TimeStampedUUIDModel):
    ticket = models.OneToOneField(
        "grievance.GrievanceTicket", related_name="sensitive_ticket_details", on_delete=models.CASCADE
    )
    payment_record = models.ForeignKey(
        "payment.PaymentRecord",
        related_name="sensitive_ticket_details",
        on_delete=models.CASCADE,
        null=True,
    )
    household = models.ForeignKey(
        "household.Household",
        related_name="sensitive_ticket_details",
        on_delete=models.CASCADE,
        null=True,
    )
    individual = models.ForeignKey(
        "household.Individual",
        related_name="sensitive_ticket_details",
        on_delete=models.CASCADE,
        null=True,
    )


class TicketHouseholdDataUpdateDetails(TimeStampedUUIDModel):
    ticket = models.OneToOneField(
        "grievance.GrievanceTicket", related_name="household_data_update_ticket_details", on_delete=models.CASCADE
    )
    household = models.ForeignKey(
        "household.Household",
        related_name="household_data_update_ticket_details",
        on_delete=models.CASCADE,
        null=True,
    )
    household_data = JSONField(null=True)


class TicketIndividualDataUpdateDetails(TimeStampedUUIDModel):
    ticket = models.OneToOneField(
        "grievance.GrievanceTicket", related_name="individual_data_update_ticket_details", on_delete=models.CASCADE
    )
    individual = models.ForeignKey(
        "household.Individual",
        related_name="individual_data_update_ticket_details",
        on_delete=models.CASCADE,
        null=True,
    )
    individual_data = JSONField(null=True)

    @property
    def household(self):
        return self.individual.household


class TicketAddIndividualDetails(TimeStampedUUIDModel):
    ticket = models.OneToOneField(
        "grievance.GrievanceTicket", related_name="add_individual_ticket_details", on_delete=models.CASCADE
    )
    household = models.ForeignKey(
        "household.Household",
        related_name="add_individual_ticket_details",
        on_delete=models.CASCADE,
        null=True,
    )
    individual_data = JSONField(null=True)
    approve_status = models.BooleanField(default=False)


class TicketDeleteIndividualDetails(TimeStampedUUIDModel):
    ticket = models.OneToOneField(
        "grievance.GrievanceTicket", related_name="delete_individual_ticket_details", on_delete=models.CASCADE
    )
    individual = models.ForeignKey(
        "household.Individual",
        related_name="delete_individual_ticket_details",
        on_delete=models.CASCADE,
        null=True,
    )

    @property
    def household(self):
        return self.individual.household
