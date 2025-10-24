from datetime import date, datetime
from typing import Any, Optional

from dateutil.relativedelta import relativedelta
from django.contrib.postgres.fields import CICharField
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.core.cache import cache
from django.core.validators import MinLengthValidator
from django.db import IntegrityError, models
from django.db.models import JSONField, Q, QuerySet, UniqueConstraint
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from multiselectfield import MultiSelectField
from phonenumber_field.modelfields import PhoneNumberField

from hope.apps.activity_log.utils import create_mapping_dict
from hope.apps.core.languages import Languages
from hope.apps.core.utils import FlexFieldsEncoder
from hope.apps.household.mixins import IndividualDeliveryDataMixin
from hope.apps.household.signals import individual_deleted, individual_withdrawn
from hope.apps.utils.phone import calculate_phone_numbers_validity, recalculate_phone_numbers_validity
from hope.models.business_area import BusinessArea
from hope.models.document import Document
from hope.models.household import (
    BLANK,
    CANNOT_DO,
    DEDUPLICATION_BATCH_STATUS_CHOICE,
    DEDUPLICATION_GOLDEN_RECORD_STATUS_CHOICE,
    DISABILITY_CHOICES,
    DISABLED,
    DUPLICATE,
    LOT_DIFFICULTY,
    MARITAL_STATUS_CHOICE,
    NONE,
    NOT_DISABLED,
    NOT_PROCESSED,
    NOT_PROVIDED,
    OBSERVED_DISABILITY_CHOICE,
    RELATIONSHIP_CHOICE,
    ROLE_NO_ROLE,
    ROLE_PRIMARY,
    SEVERITY_OF_DISABILITY_CHOICES,
    SEX_CHOICE,
    STATUS_ACTIVE,
    STATUS_DUPLICATE,
    STATUS_INACTIVE,
    STATUS_WITHDRAWN,
    UNIQUE,
    UNIQUE_IN_BATCH,
    WORK_STATUS_CHOICE,
    PendingHousehold,
)
from hope.models.utils import (
    AbstractSyncable,
    AdminUrlMixin,
    ConcurrencyModel,
    InternalDataFieldModel,
    PendingManager,
    SoftDeletableMergeStatusModel,
    TimeStampedUUIDModel,
    UnicefIdentifiedModel,
)


class IndividualCollection(UnicefIdentifiedModel):
    """Collection of individual representations."""

    def __str__(self) -> str:
        return self.unicef_id or ""

    @property
    def business_area(self) -> BusinessArea | None:
        return self.individuals.first().business_area if self.individuals.first() else None

    class Meta:
        app_label = "household"


class Individual(
    InternalDataFieldModel,
    SoftDeletableMergeStatusModel,
    TimeStampedUUIDModel,
    AbstractSyncable,
    ConcurrencyModel,
    UnicefIdentifiedModel,
    AdminUrlMixin,
    IndividualDeliveryDataMixin,
):
    ACTIVITY_LOG_MAPPING = create_mapping_dict(
        [
            "status",
            "duplicate",
            "withdrawn",
            "individual_id",
            "photo",
            "full_name",
            "given_name",
            "middle_name",
            "family_name",
            "sex",
            "birth_date",
            "estimated_birth_date",
            "marital_status",
            "phone_no",
            "phone_no_alternative",
            "relationship",
            "household",
            "registration_data_import",
            "disability",
            "work_status",
            "first_registration_date",
            "last_registration_date",
            "flex_fields",
            "enrolled_in_nutrition_programme",
            "unicef_id",
            "deduplication_golden_record_status",
            "deduplication_batch_status",
            "deduplication_golden_record_results",
            "deduplication_batch_results",
            "imported_individual_id",
            "sanction_list_possible_match",
            "sanction_list_confirmed_match",
            "sanction_list_last_check",
            "pregnant",
            "observed_disability",
            "seeing_disability",
            "hearing_disability",
            "physical_disability",
            "memory_disability",
            "selfcare_disability",
            "comms_disability",
            "who_answers_phone",
            "who_answers_alt_phone",
            "detail_id",
            "program_registration_id",
            "payment_delivery_phone_no",
        ]
    )

    business_area = models.ForeignKey("core.BusinessArea", on_delete=models.CASCADE, help_text="Business area")
    program = models.ForeignKey(
        "program.Program",
        db_index=True,
        related_name="individuals",
        on_delete=models.PROTECT,
        help_text="Program",
    )
    registration_data_import = models.ForeignKey(
        "registration_data.RegistrationDataImport",
        related_name="individuals",
        on_delete=models.CASCADE,
        help_text="RDI where Beneficiary was imported",
    )
    household = models.ForeignKey(
        "Household",
        related_name="individuals",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="""This represents the household this person is a MEMBER,
            and if null then relationship is NON_BENEFICIARY and that
            simply means they are a representative of one or more households
            and not a member of one.""",
    )
    individual_collection = models.ForeignKey(
        IndividualCollection,
        related_name="individuals",
        on_delete=models.CASCADE,
        null=True,
        help_text="Collection of individual representations",
    )
    copied_from = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        db_index=True,
        related_name="copied_to",
        on_delete=models.SET_NULL,
        help_text="If this individual was copied from another individual, "
        "this field will contain the individual it was copied from.",
    )

    individual_id = models.CharField(max_length=255, blank=True, help_text="Individual ID")
    photo = models.ImageField(blank=True, help_text="Photo")
    full_name = CICharField(
        max_length=255,
        validators=[MinLengthValidator(2)],
        db_index=True,
        help_text="Full Name of the Beneficiary",
    )
    given_name = CICharField(
        max_length=85,
        blank=True,
        db_index=True,
        help_text="First name of the Beneficiary",
    )
    middle_name = CICharField(
        max_length=85,
        blank=True,
        db_index=True,
        help_text="Middle name of the Beneficiary",
    )
    family_name = CICharField(
        max_length=85,
        blank=True,
        db_index=True,
        help_text="Last name of the Beneficiary",
    )
    sex = models.CharField(
        max_length=255,
        choices=SEX_CHOICE,
        db_index=True,
        help_text="Beneficiary gender",
    )
    birth_date = models.DateField(db_index=True, help_text="Beneficiary date of birth")
    estimated_birth_date = models.BooleanField(default=False, help_text="Estimated birth date flag")
    marital_status = models.CharField(
        max_length=255,
        choices=MARITAL_STATUS_CHOICE,
        default=BLANK,
        db_index=True,
        help_text="Beneficiary marital status",
    )

    phone_no = PhoneNumberField(blank=True, db_index=True, help_text="Beneficiary phone number")
    phone_no_alternative = PhoneNumberField(blank=True, db_index=True, help_text="Beneficiary phone number alternative")
    email = models.CharField(max_length=255, blank=True, help_text="Beneficiary email address")
    payment_delivery_phone_no = PhoneNumberField(blank=True, null=True, help_text="Beneficiary contact phone number")
    relationship = models.CharField(
        max_length=255,
        blank=True,
        choices=RELATIONSHIP_CHOICE,
        help_text="""This represents the MEMBER relationship. can be blank
            as well if household is null!""",
    )
    work_status = models.CharField(
        max_length=20,
        choices=WORK_STATUS_CHOICE,
        blank=True,
        default=NOT_PROVIDED,
        help_text="Work status",
    )
    pregnant = models.BooleanField(null=True, help_text="Pregnant status")
    fchild_hoh = models.BooleanField(default=False, help_text="Child is female and Head of Household flag")
    child_hoh = models.BooleanField(default=False, help_text="Child is Head of Household flag")
    disability = models.CharField(
        max_length=20,
        choices=DISABILITY_CHOICES,
        default=NOT_DISABLED,
        help_text="Disability status",
    )
    observed_disability = MultiSelectField(
        choices=OBSERVED_DISABILITY_CHOICE,
        default=NONE,
        help_text="Observed disability status",
    )
    disability_certificate_picture = models.ImageField(
        blank=True, null=True, help_text="Disability certificate picture"
    )
    seeing_disability = models.CharField(
        max_length=50,
        choices=SEVERITY_OF_DISABILITY_CHOICES,
        blank=True,
        help_text="Seeing disability",
    )
    hearing_disability = models.CharField(
        max_length=50,
        choices=SEVERITY_OF_DISABILITY_CHOICES,
        blank=True,
        help_text="Hearing disability",
    )
    physical_disability = models.CharField(
        max_length=50,
        choices=SEVERITY_OF_DISABILITY_CHOICES,
        blank=True,
        help_text="Physical disability",
    )
    memory_disability = models.CharField(
        max_length=50,
        choices=SEVERITY_OF_DISABILITY_CHOICES,
        blank=True,
        help_text="Memory disability",
    )
    selfcare_disability = models.CharField(
        max_length=50,
        choices=SEVERITY_OF_DISABILITY_CHOICES,
        blank=True,
        help_text="Selfcare disability",
    )
    comms_disability = models.CharField(
        max_length=50,
        choices=SEVERITY_OF_DISABILITY_CHOICES,
        blank=True,
        help_text="Comms disability",
    )

    who_answers_phone = models.CharField(max_length=150, blank=True, help_text="Who answers phone number")
    who_answers_alt_phone = models.CharField(
        max_length=150, blank=True, help_text="Who answers alternative phone number"
    )
    preferred_language = models.CharField(
        max_length=6,
        choices=Languages.get_tuple(),
        null=True,
        blank=True,
        help_text="Preferred language",
    )
    relationship_confirmed = models.BooleanField(default=False, help_text="Relationship confirmed status")
    wallet_name = models.CharField(max_length=64, blank=True, default="", help_text="Cryptocurrency wallet name")
    blockchain_name = models.CharField(
        max_length=64,
        blank=True,
        default="",
        help_text="Cryptocurrency blockchain name",
    )
    wallet_address = models.CharField(
        max_length=128,
        blank=True,
        default="",
        help_text="Cryptocurrency wallet address",
    )

    # System fields
    duplicate = models.BooleanField(default=False, db_index=True, help_text="Duplicate status [sys]")
    duplicate_date = models.DateTimeField(null=True, blank=True, help_text="Duplicate date [sys]")
    withdrawn = models.BooleanField(default=False, db_index=True, help_text="Withdrawn status [sys]")
    withdrawn_date = models.DateTimeField(null=True, blank=True, help_text="Withdrawn date [sys]")
    flex_fields = JSONField(
        default=dict,
        blank=True,
        encoder=FlexFieldsEncoder,
        help_text="FlexFields JSON representation [sys]",
    )
    phone_no_valid = models.BooleanField(null=True, db_index=True, help_text="Beneficiary phone number valid [sys]")
    phone_no_alternative_valid = models.BooleanField(
        null=True,
        db_index=True,
        help_text="Beneficiary phone number alternative valid [sys]",
    )
    first_registration_date = models.DateField(help_text="First registration date [sys]")
    last_registration_date = models.DateField(help_text="Last registration date [sys]")
    enrolled_in_nutrition_programme = models.BooleanField(null=True, help_text="Enrolled in nutrition program [sys]")
    deduplication_golden_record_status = models.CharField(
        max_length=50,
        default=UNIQUE,
        choices=DEDUPLICATION_GOLDEN_RECORD_STATUS_CHOICE,
        db_index=True,
        help_text="Deduplication golden record status [sys]",
    )
    deduplication_batch_status = models.CharField(
        max_length=50,
        default=UNIQUE_IN_BATCH,
        choices=DEDUPLICATION_BATCH_STATUS_CHOICE,
        db_index=True,
        help_text="Deduplication batch status [sys]",
    )
    deduplication_golden_record_results = JSONField(
        default=dict, blank=True, help_text="Deduplication golden record results [sys]"
    )
    deduplication_batch_results = JSONField(default=dict, blank=True, help_text="Deduplication batch results [sys]")
    biometric_deduplication_golden_record_status = models.CharField(
        max_length=50,
        default=NOT_PROCESSED,
        choices=DEDUPLICATION_GOLDEN_RECORD_STATUS_CHOICE,
        db_index=True,
        help_text="Deduplication golden record status [sys]",
    )
    biometric_deduplication_batch_status = models.CharField(
        max_length=50,
        default=NOT_PROCESSED,
        choices=DEDUPLICATION_BATCH_STATUS_CHOICE,
        db_index=True,
        help_text="Deduplication batch status [sys]",
    )
    biometric_deduplication_golden_record_results = JSONField(
        default=list, blank=True, help_text="Deduplication golden record results [sys]"
    )
    biometric_deduplication_batch_results = JSONField(
        default=list, blank=True, help_text="Deduplication batch results [sys]"
    )
    imported_individual_id = models.UUIDField(null=True, blank=True, help_text="Imported individual ID [sys]")
    sanction_list_possible_match = models.BooleanField(
        default=False, db_index=True, help_text="Sanction list possible match [sys]"
    )
    sanction_list_confirmed_match = models.BooleanField(
        default=False, db_index=True, help_text="Sanction list confirmed match [sys]"
    )
    detail_id = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        help_text="Kobo asset ID, Xlsx row ID, Aurora registration ID [sys]",
    )
    program_registration_id = CICharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("Beneficiary Program Registration Id"),
        help_text="Beneficiary Program Registration ID [sys]",
    )
    age_at_registration = models.PositiveSmallIntegerField(null=True, blank=True, help_text="Age at registration [sys]")
    origin_unicef_id = models.CharField(max_length=100, blank=True, null=True, help_text="Original unicef_id [sys]")
    is_migration_handled = models.BooleanField(default=False, help_text="Migration status [sys]")
    migrated_at = models.DateTimeField(null=True, blank=True, help_text="Migrated at [sys]")
    identification_key = models.CharField(
        null=True,
        blank=True,
        max_length=255,
        db_index=True,
        help_text="Key used to identify Collisions in the system",
    )
    vector_column = SearchVectorField(null=True, help_text="Database vector column for search [sys]")

    def delete(self, *args: Any, **kwargs: Any) -> tuple[int, dict[str, int]]:
        individual_deleted.send(self.__class__, instance=self)
        return super().delete(*args, **kwargs)

    @property
    def phone_no_text(self) -> str:
        return str(self.phone_no).replace(" ", "")

    @property
    def phone_no_alternative_text(self) -> str:
        return str(self.phone_no_alternative).replace(" ", "")

    @property
    def age(self) -> int:
        return relativedelta(date.today(), self.birth_date).years

    @property
    def role(self) -> str:
        role = self.households_and_roles.first()
        return role.role if role is not None else ROLE_NO_ROLE

    @property
    def get_hash_key(self) -> str:
        from hashlib import sha256

        fields = (
            "given_name",
            "middle_name",
            "family_name",
            "full_name",
            "sex",
            "birth_date",
            "phone_no",
            "phone_no_alternative",
        )
        values = [str(getattr(self, field)) for field in fields]

        return sha256(";".join(values).encode()).hexdigest()

    @property
    def status(self) -> str:
        statuses = []
        if self.duplicate:
            statuses.append(STATUS_DUPLICATE)
        if self.withdrawn:
            statuses.append(STATUS_WITHDRAWN)
        if len(statuses) > 0:
            return ", ".join(statuses)
        return STATUS_ACTIVE

    @property
    def cash_assist_status(self) -> str:
        return STATUS_INACTIVE if self.withdrawn or self.duplicate else STATUS_ACTIVE

    @property
    def sanction_list_last_check(self) -> datetime | None:
        # TODO: SANCTION LIST CHECK PER LIST
        if self.program.sanction_lists.exists():
            return cache.get("sanction_list_last_check")
        return None

    def withdraw(self) -> None:
        self.documents.update(status=Document.STATUS_INVALID)
        self.accounts.update(active=False)
        self.withdrawn = True
        self.withdrawn_date = timezone.now()
        self.save()
        individual_withdrawn.send(sender=self.__class__, instance=self)

    def unwithdraw(self) -> None:
        self.documents.update(status=Document.STATUS_NEED_INVESTIGATION)
        self.accounts.update(active=True)
        self.withdrawn = False
        self.withdrawn_date = None
        self.save()

    def mark_as_duplicate(self, original_individual: Optional["Individual"] = None) -> None:
        if original_individual is not None:
            self.unicef_id = str(original_individual.unicef_id)
        self.documents.update(status=Document.STATUS_INVALID)
        self.accounts.update(active=False)
        self.duplicate = True
        self.duplicate_date = timezone.now()
        self.save()

    def mark_as_distinct(self) -> None:
        # try update per each Document
        for doc in self.documents.all():
            try:
                doc.status = Document.STATUS_VALID
                doc.save()
            # AB#244721
            except IntegrityError:
                error_message = f"{self.unicef_id}: Valid Document already exists: {doc.document_number}."
                raise Exception(error_message)
        self.accounts.update(active=True)
        self.duplicate = False
        self.duplicate_date = timezone.now()
        self.save()

    def set_relationship_confirmed_flag(self, confirmed: bool) -> None:
        self.relationship_confirmed = confirmed
        self.save(update_fields=["relationship_confirmed"])

    def __str__(self) -> str:
        return self.unicef_id or ""

    class Meta:
        app_label = "household"
        verbose_name = "Individual"
        indexes = (GinIndex(fields=["vector_column"]),)
        constraints = [
            UniqueConstraint(
                fields=["unicef_id", "program"],
                condition=Q(is_removed=False) & Q(duplicate=False),
                name="unique_ind_unicef_id_in_program",
            ),
            UniqueConstraint(
                fields=["identification_key", "program"],
                condition=Q(is_removed=False)
                & Q(identification_key__isnull=False)
                & Q(rdi_merge_status=SoftDeletableMergeStatusModel.MERGED),
                name="identification_key_ind_unique_constraint",
            ),
        ]
        permissions = (("update_individual_iban", "Can update individual IBAN"),)

    def recalculate_data(self, save: bool = True) -> tuple[Any, list[str]]:
        update_fields = ["disability"]

        disability_fields = (
            "seeing_disability",
            "hearing_disability",
            "physical_disability",
            "memory_disability",
            "selfcare_disability",
            "comms_disability",
        )
        should_be_disabled = self.disability == DISABLED
        for field in disability_fields:
            value = getattr(self, field, None)
            should_be_disabled = should_be_disabled or value in [
                CANNOT_DO,
                LOT_DIFFICULTY,
            ]
        self.disability = DISABLED if should_be_disabled else NOT_DISABLED

        if save:
            self.save(update_fields=update_fields)

        return self, update_fields

    def count_all_roles(self) -> int:
        return self.households_and_roles.exclude(role=ROLE_NO_ROLE).count()

    def count_primary_roles(self) -> int:
        return self.households_and_roles.filter(role=ROLE_PRIMARY).count()

    @cached_property
    def parents(self) -> list["Individual"]:
        return self.household.individuals.exclude(Q(duplicate=True) | Q(withdrawn=True)) if self.household else []

    def is_golden_record_duplicated(self) -> bool:
        return self.deduplication_golden_record_status == DUPLICATE

    def get_deduplication_golden_record(self) -> list:
        status_key = "duplicates" if self.is_golden_record_duplicated() else "possible_duplicates"
        return self.deduplication_golden_record_results.get(status_key, [])

    @cached_property
    def active_record(self) -> Optional["Individual"]:
        if self.duplicate:
            return Individual.objects.filter(unicef_id=self.unicef_id, duplicate=False, is_removed=False).first()
        return None

    def is_head(self) -> bool:
        if not self.household:
            return False
        return self.household.head_of_household.id == self.id

    def erase(self) -> None:
        for document in self.documents.all():
            document.erase()

        self.is_removed = True
        self.removed_date = timezone.now()
        self.full_name = "GDPR REMOVED"
        self.given_name = "GDPR REMOVED"
        self.middle_name = "GDPR REMOVED"
        self.family_name = "GDPR REMOVED"
        self.photo = ""
        self.disability_certificate_picture = ""
        self.phone_no = ""
        self.phone_no_valid = False
        self.phone_no_alternative = ""
        self.phone_no_alternative_valid = False
        self.flex_fields = {}
        self.save()

    def validate_phone_numbers(self) -> None:
        calculate_phone_numbers_validity(self)

    def save(self, *args: Any, **kwargs: Any) -> None:
        recalculate_phone_numbers_validity(self, Individual)
        super().save(*args, **kwargs)


class PendingIndividual(Individual):
    objects = PendingManager()

    @property
    def households_and_roles(self) -> QuerySet:
        return super().households_and_roles(manager="pending_objects")

    @property
    def documents(self) -> QuerySet:
        return super().documents(manager="pending_objects")

    @property
    def identities(self) -> QuerySet:
        return super().identities(manager="pending_objects")

    @property
    def pending_household(self) -> QuerySet:
        return PendingHousehold.objects.get(pk=self.household.pk)

    class Meta:
        app_label = "household"
        proxy = True
        verbose_name = "Imported Individual"
        verbose_name_plural = "Imported Individuals"
