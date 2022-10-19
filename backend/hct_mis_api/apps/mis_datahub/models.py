from django.db import models
from django.utils.translation import gettext_lazy as _

from hct_mis_api.apps.household.models import (
    IDENTIFICATION_TYPE_CHOICE,
    INDIVIDUAL_HOUSEHOLD_STATUS,
    MARITAL_STATUS_CHOICE,
    RELATIONSHIP_CHOICE,
    RESIDENCE_STATUS_CHOICE,
    ROLE_CHOICE,
)
from hct_mis_api.apps.utils.models import AbstractSession, UnicefIdentifiedModel


class Session(AbstractSession):
    def __str__(self):
        return f"{self.business_area} / {self.timestamp}"


class SessionModel(models.Model):
    session = models.ForeignKey("Session", on_delete=models.CASCADE)

    class Meta:
        abstract = True


class Household(SessionModel, UnicefIdentifiedModel):
    mis_id = models.UUIDField()
    unhcr_id = models.CharField(max_length=255, null=True)
    status = models.CharField(max_length=20, choices=INDIVIDUAL_HOUSEHOLD_STATUS, default="ACTIVE")
    household_size = models.PositiveIntegerField()
    # registration household id
    form_number = models.CharField(max_length=255, null=True)
    address = models.CharField(max_length=255, null=True)
    admin1 = models.CharField(max_length=255, null=True)
    admin2 = models.CharField(max_length=255, null=True)
    country = models.CharField(null=True, max_length=3)
    residence_status = models.CharField(max_length=255, choices=RESIDENCE_STATUS_CHOICE, null=True)
    registration_date = models.DateField(null=True)
    village = models.CharField(max_length=250, blank=True, null=True)

    class Meta:
        unique_together = ("session", "mis_id")


class Individual(SessionModel, UnicefIdentifiedModel):
    INACTIVE = "INACTIVE"
    ACTIVE = "ACTIVE"
    STATUS_CHOICE = ((INACTIVE, "Inactive"), (ACTIVE, "Active"))
    MALE = "MALE"
    FEMALE = "FEMALE"
    SEX_CHOICE = (
        (MALE, _("Male")),
        (FEMALE, _("Female")),
        (None, None),
    )

    mis_id = models.UUIDField()
    unhcr_id = models.CharField(max_length=255, null=True)
    household_mis_id = models.UUIDField(null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICE, null=True)
    full_name = models.CharField(max_length=255)
    family_name = models.CharField(max_length=255, null=True)
    given_name = models.CharField(max_length=255, null=True)
    middle_name = models.CharField(max_length=255, null=True)
    sex = models.CharField(
        max_length=255,
        choices=SEX_CHOICE,
        null=True
    )
    date_of_birth = models.DateField()
    estimated_date_of_birth = models.BooleanField()
    relationship = models.CharField(
        max_length=255,
        null=True,
        choices=RELATIONSHIP_CHOICE,
    )
    marital_status = models.CharField(
        max_length=255,
        null=True,
        choices=MARITAL_STATUS_CHOICE,
    )
    phone_number = models.CharField(max_length=60, null=True)
    pregnant = models.BooleanField(null=True)
    sanction_list_confirmed_match = models.BooleanField(default=False)

    class Meta:
        unique_together = ("session", "mis_id")

    def __str__(self):
        return self.family_name or ""


class TargetPopulation(SessionModel):
    mis_id = models.UUIDField()
    name = models.CharField(max_length=255)
    population_type = models.CharField(default="HOUSEHOLD", max_length=20)
    targeting_criteria = models.TextField()

    active_households = models.PositiveIntegerField(default=0)
    program_mis_id = models.UUIDField()

    class Meta:
        unique_together = ("session", "mis_id")

    def __str__(self):
        return self.name


class IndividualRoleInHousehold(SessionModel):
    individual_mis_id = models.UUIDField()
    household_mis_id = models.UUIDField()
    role = models.CharField(
        max_length=255,
        blank=True,
        choices=ROLE_CHOICE,
    )
    active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("role", "household_mis_id", "session")


class TargetPopulationEntry(SessionModel):
    household_unhcr_id = models.CharField(max_length=255, null=True)
    individual_unhcr_id = models.CharField(max_length=255, null=True)
    household_mis_id = models.UUIDField(null=True)
    individual_mis_id = models.UUIDField(null=True)
    target_population_mis_id = models.UUIDField()
    vulnerability_score = models.DecimalField(
        blank=True,
        null=True,
        decimal_places=3,
        max_digits=6,
        help_text="Written by a tool such as Corticon.",
    )

    class Meta:
        unique_together = (
            "session",
            "household_mis_id",
            "target_population_mis_id",
        )
        verbose_name_plural = "Target Population Entries"


class Program(SessionModel):
    STATUS_NOT_STARTED = "NOT_STARTED"
    STATUS_STARTED = "STARTED"
    STATUS_COMPLETE = "COMPLETE"
    SCOPE_FOR_PARTNERS = "FOR_PARTNERS"
    SCOPE_UNICEF = "UNICEF"
    SCOPE_CHOICE = (
        (SCOPE_FOR_PARTNERS, _("For partners")),
        (SCOPE_UNICEF, _("Unicef")),
    )
    mis_id = models.UUIDField()
    business_area = models.CharField(
        max_length=20
    )  # TODO: potentially remove in future since base model has it already
    ca_id = models.CharField(max_length=255, null=True)
    ca_hash_id = models.CharField(max_length=255, null=True)
    name = models.CharField(max_length=255)
    scope = models.CharField(choices=SCOPE_CHOICE, max_length=50)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    description = models.CharField(max_length=255, null=True)
    individual_data_needed = models.BooleanField(default=False)

    class Meta:
        unique_together = ("session", "mis_id")


class Document(SessionModel):
    VALID = "VALID"
    COLLECTED = "COLLECTED"
    LOST = "LOST"
    UNKNOWN = "UNKNOWN"
    CANCELED = "CANCELED"
    EXPIRED = "EXPIRED"
    HOLD = "HOLD"
    DAMAGED = "DAMAGED"
    STATUS_CHOICE = (
        (VALID, _("Valid")),
        (COLLECTED, _("Collected")),
        (LOST, _("Lost")),
        (UNKNOWN, _("Unknown")),
        (CANCELED, _("Canceled")),
        (EXPIRED, _("Expired")),
        (HOLD, _("Hold")),
        (DAMAGED, _("Damaged")),
    )

    status = models.CharField(choices=STATUS_CHOICE, null=True, max_length=30, default=None)
    date_of_expiry = models.DateField(null=True, default=None)
    photo = models.ImageField(blank=True, default="")
    mis_id = models.UUIDField()
    number = models.CharField(max_length=255, null=True)
    individual_mis_id = models.UUIDField(null=True)
    type = models.CharField(max_length=50, choices=IDENTIFICATION_TYPE_CHOICE)


class FundsCommitment(models.Model):
    rec_serial_number = models.CharField(max_length=10, blank=True, null=True)
    business_area = models.CharField(max_length=4, blank=True, null=True)
    funds_commitment_number = models.CharField(max_length=10, blank=True, null=True)
    document_type = models.CharField(max_length=2, blank=True, null=True)
    document_text = models.CharField(max_length=50, blank=True, null=True)
    currency_code = models.CharField(max_length=5, blank=True, null=True)
    gl_account = models.CharField(null=True, blank=True, max_length=10)
    commitment_amount_local = models.DecimalField(
        decimal_places=2,
        max_digits=15,
        blank=True,
        null=True,
    )
    commitment_amount_usd = models.DecimalField(
        decimal_places=2,
        max_digits=15,
        blank=True,
        null=True,
    )
    total_open_amount_local = models.DecimalField(
        decimal_places=2,
        max_digits=15,
        blank=True,
        null=True,
    )
    total_open_amount_usd = models.DecimalField(
        decimal_places=2,
        max_digits=15,
        blank=True,
        null=True,
    )
    vendor_id = models.CharField(max_length=10, blank=True, null=True)
    posting_date = models.DateField(blank=True, null=True)
    vision_approval = models.CharField(max_length=1, blank=True, null=True)
    document_reference = models.CharField(max_length=16, null=True)
    fc_status = models.CharField(max_length=1, blank=True, null=True)
    create_date = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    created_by = models.CharField(max_length=20, null=True, blank=True, default="")
    update_date = models.DateTimeField(null=True, blank=True)
    updated_by = models.CharField(max_length=20, blank=True, null=True, default="")
    mis_sync_flag = models.BooleanField(null=True, blank=True, default=False)
    mis_sync_date = models.DateTimeField(blank=True, null=True)
    ca_sync_flag = models.BooleanField(blank=True, null=True, default=False)
    ca_sync_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.funds_commitment_number


class DownPayment(models.Model):
    rec_serial_number = models.CharField(max_length=10, blank=True, null=True)
    business_area = models.CharField(max_length=4)
    down_payment_reference = models.CharField(max_length=20)
    document_type = models.CharField(max_length=10)
    consumed_fc_number = models.CharField(max_length=10)
    total_down_payment_amount_local = models.DecimalField(
        decimal_places=2,
        max_digits=15,
    )
    total_down_payment_amount_usd = models.DecimalField(
        decimal_places=2,
        max_digits=15,
        blank=True,
        null=True,
    )
    currency_code = models.CharField(max_length=5, blank=True, null=True)
    posting_date = models.DateField(blank=True, null=True)
    doc_year = models.IntegerField(blank=True, null=True)
    doc_number = models.CharField(max_length=10, blank=True, null=True)
    doc_item_number = models.CharField(max_length=3, null=True)
    create_date = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    created_by = models.CharField(max_length=20, blank=True, null=True, default="")
    update_date = models.DateTimeField(blank=True, null=True)
    updated_by = models.CharField(max_length=20, blank=True, null=True, default="")
    mis_sync_flag = models.BooleanField(default=False, blank=True, null=True)
    mis_sync_date = models.DateTimeField(blank=True, null=True)
    ca_sync_flag = models.BooleanField(default=False, blank=True, null=True)
    ca_sync_date = models.DateTimeField(blank=True, null=True)
