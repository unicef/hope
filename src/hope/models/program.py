import random
import secrets
import string
from decimal import Decimal
from typing import Any, Collection

from django.contrib.postgres.fields import CICharField
from django.core.exceptions import ValidationError
from django.core.validators import (
    MaxLengthValidator,
    MinLengthValidator,
    MinValueValidator,
    ProhibitNullCharactersValidator,
)
from django.db import models
from django.db.models import Q, QuerySet
from django.db.models.constraints import UniqueConstraint
from django.utils.translation import gettext_lazy as _
from model_utils.models import SoftDeletableModel
from strategy_field.fields import StrategyField

from hope.apps.activity_log.utils import create_mapping_dict
from hope.models.beneficiary_group import BeneficiaryGroup
from hope.models.data_collecting_type import DataCollectingType
from hope.models.household import Household
from hope.models.payment import Payment
from hope.models.payment_plan import PaymentPlan
from hope.apps.program.collision_detectors import collision_detectors_registry
from hope.models.sanction_list import SanctionList
from hope.models.utils import (
    AbstractSyncable,
    AdminUrlMixin,
    ConcurrencyModel,
    SoftDeletableIsVisibleManager,
    TimeStampedUUIDModel,
)
from hope.apps.utils.validators import DoubleSpaceValidator, StartEndSpaceValidator
from hope.models.program_partner_through import ProgramPartnerThrough


class Program(
    SoftDeletableModel,
    TimeStampedUUIDModel,
    AbstractSyncable,
    ConcurrencyModel,
    AdminUrlMixin,
):
    ACTIVITY_LOG_MAPPING = create_mapping_dict(
        [
            "name",
            "status",
            "start_date",
            "end_date",
            "description",
            "business_area",
            "budget",
            "frequency_of_payments",
            "sector",
            "scope",
            "cash_plus",
            "population_goal",
            "administrative_areas_of_implementation",
            "partner_access",
        ],
        {"admin_areas_log": "admin_areas"},
    )
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    FINISHED = "FINISHED"
    STATUS_CHOICE = (
        (ACTIVE, _("Active")),
        (DRAFT, _("Draft")),
        (FINISHED, _("Finished")),
    )

    REGULAR = "REGULAR"
    ONE_OFF = "ONE_OFF"

    FREQUENCY_OF_PAYMENTS_CHOICE = (
        (ONE_OFF, _("One-off")),
        (REGULAR, _("Regular")),
    )

    CHILD_PROTECTION = "CHILD_PROTECTION"
    EDUCATION = "EDUCATION"
    HEALTH = "HEALTH"
    MULTI_PURPOSE = "MULTI_PURPOSE"
    NUTRITION = "NUTRITION"
    SOCIAL_POLICY = "SOCIAL_POLICY"
    WASH = "WASH"

    SECTOR_CHOICE = (
        (CHILD_PROTECTION, _("Child Protection")),
        (EDUCATION, _("Education")),
        (HEALTH, _("Health")),
        (MULTI_PURPOSE, _("Multi Purpose")),
        (NUTRITION, _("Nutrition")),
        (SOCIAL_POLICY, _("Social Policy")),
        (WASH, _("WASH")),
    )

    SCOPE_FOR_PARTNERS = "FOR_PARTNERS"
    SCOPE_UNICEF = "UNICEF"

    SCOPE_CHOICE = (
        (SCOPE_FOR_PARTNERS, _("For partners")),
        (SCOPE_UNICEF, _("Unicef")),
    )

    ALL_PARTNERS_ACCESS = "ALL_PARTNERS_ACCESS"
    NONE_PARTNERS_ACCESS = "NONE_PARTNERS_ACCESS"
    SELECTED_PARTNERS_ACCESS = "SELECTED_PARTNERS_ACCESS"

    PARTNER_ACCESS_CHOICE = (
        (ALL_PARTNERS_ACCESS, _("All partners access")),
        (NONE_PARTNERS_ACCESS, _("None partners access")),
        (SELECTED_PARTNERS_ACCESS, _("Selected partners access")),
    )

    data_collecting_type = models.ForeignKey(
        "core.DataCollectingType",
        related_name="programs",
        on_delete=models.PROTECT,
        help_text="Program data collecting type",
    )
    beneficiary_group = models.ForeignKey(
        BeneficiaryGroup,
        on_delete=models.PROTECT,
        related_name="programs",
        help_text="Program beneficiary group",
    )
    business_area = models.ForeignKey("core.BusinessArea", on_delete=models.CASCADE, help_text="Business area")
    partners = models.ManyToManyField(
        to="account.Partner",
        through=ProgramPartnerThrough,
        related_name="programs",
        help_text="Program partners",
    )
    admin_areas = models.ManyToManyField("geo.Area", related_name="programs", blank=True, help_text="Admin areas")
    name = CICharField(
        max_length=255,
        validators=[
            MinLengthValidator(3),
            MaxLengthValidator(255),
            DoubleSpaceValidator,
            StartEndSpaceValidator,
            ProhibitNullCharactersValidator(),
        ],
        db_index=True,
        help_text="Program name",
    )
    programme_code = models.CharField(max_length=4, null=True, blank=True, help_text="Program code")
    status = models.CharField(max_length=10, choices=STATUS_CHOICE, db_index=True, help_text="Program status")
    slug = models.CharField(max_length=4, db_index=True, help_text="Program slug [sys]")
    description = models.CharField(
        blank=True,
        max_length=255,
        validators=[MinLengthValidator(3), MaxLengthValidator(255)],
        help_text="Program description",
    )
    start_date = models.DateField(db_index=True, help_text="Program start date")
    end_date = models.DateField(null=True, blank=True, db_index=True, help_text="Program end date")
    sector = models.CharField(max_length=50, choices=SECTOR_CHOICE, db_index=True, help_text="Program sector")
    budget = models.DecimalField(
        decimal_places=2,
        max_digits=11,
        validators=[MinValueValidator(Decimal("0.00"))],
        db_index=True,
        help_text="Program budget",
    )
    frequency_of_payments = models.CharField(
        max_length=50,
        choices=FREQUENCY_OF_PAYMENTS_CHOICE,
        help_text="Program frequency of payments",
    )
    scope = models.CharField(
        blank=True,
        null=True,
        max_length=50,
        choices=SCOPE_CHOICE,
        help_text="Program scope",
    )

    partner_access = models.CharField(
        max_length=50,
        choices=PARTNER_ACCESS_CHOICE,
        default=SELECTED_PARTNERS_ACCESS,
        help_text="Program partner access",
    )
    cash_plus = models.BooleanField(help_text="Program cash+")
    population_goal = models.PositiveIntegerField(help_text="Program population goal")
    administrative_areas_of_implementation = models.CharField(
        max_length=255,
        blank=True,
        validators=[MinLengthValidator(3), MaxLengthValidator(255)],
        help_text="Program administrative area of implementation",
    )
    biometric_deduplication_enabled = models.BooleanField(
        default=False, help_text="Enable Deduplication of Face Images"
    )
    collision_detection_enabled = models.BooleanField(default=False, help_text="don't create duplicated")
    collision_detector = StrategyField(
        registry=collision_detectors_registry,
        null=True,
        blank=True,
        help_text="Object which detects collisions",
    )
    # System fields
    is_visible = models.BooleanField(default=True, help_text="Program is visible in UI [sys]")
    household_count = models.PositiveIntegerField(default=0, help_text="Program household count [sys]")
    individual_count = models.PositiveIntegerField(default=0, help_text="Program individual count [sys]")

    deduplication_set_id = models.UUIDField(blank=True, null=True, help_text="Program deduplication set id [sys]")

    sanction_lists = models.ManyToManyField(
        SanctionList,
        blank=True,
        related_name="programs",
        help_text="Program sanction lists",
    )
    objects = SoftDeletableIsVisibleManager()

    def clean(self) -> None:
        super().clean()
        if (
            self.data_collecting_type
            and self.beneficiary_group
            and (
                self.data_collecting_type.type == DataCollectingType.Type.SOCIAL
                and self.beneficiary_group.master_detail
            )
            or (
                self.data_collecting_type.type == DataCollectingType.Type.STANDARD
                and not self.beneficiary_group.master_detail
            )
        ):
            raise ValidationError("Selected combination of data collecting type and beneficiary group is invalid.")

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.clean()
        if not self.programme_code:
            self.programme_code = self.generate_programme_code()
        if not self.slug:
            self.slug = self.generate_slug()
        if self.data_collecting_type_id is None and self.data_collecting_type:
            # save the related object before saving Program
            self.data_collecting_type.save()
        super().save(*args, **kwargs)

    def generate_programme_code(self) -> str:
        programme_code = "".join(secrets.choice(string.ascii_uppercase + string.digits + "-") for _ in range(4))
        if Program.objects.filter(business_area_id=self.business_area_id, programme_code=programme_code).exists():
            return self.generate_programme_code()
        return programme_code

    def generate_slug(self) -> str:
        return self.programme_code.lower()

    @staticmethod
    def get_total_number_of_households_from_payments(
        qs: models.QuerySet[PaymentPlan],
    ) -> int:
        return (
            qs.filter(payment_items__delivered_quantity__gt=0)
            .distinct("payment_items__household__unicef_id")
            .values_list("payment_items__household__unicef_id", flat=True)
            .order_by("payment_items__household__unicef_id")
            .count()
        )

    def adjust_program_size(self) -> None:
        self.household_count = self.households.count()
        self.individual_count = self.individuals.count()

    @property
    def households_with_payments_in_program(self) -> QuerySet:
        # for now all Payments or maybe can filter just status__in=Payment.DELIVERED_STATUSES
        household_ids = (
            Payment.objects.filter(program=self)
            .exclude(conflicted=True, excluded=True)
            .values_list("household_id", flat=True)
            .distinct()
        )

        return Household.objects.filter(id__in=household_ids, program=self)

    @property
    def admin_areas_log(self) -> str:
        return ", ".join(self.admin_areas.all())

    @property
    def is_social_worker_program(self) -> bool:
        return self.data_collecting_type.type == DataCollectingType.Type.SOCIAL

    @property
    def screen_beneficiary(self) -> None:
        """Return if program will be screened against the sanction lists.

        :return:
        """
        return self.sanction_lists.exists()

    class Meta:
        app_label = "program"
        constraints = [
            UniqueConstraint(
                fields=["name", "business_area", "is_removed"],
                condition=Q(is_removed=False),
                name="unique_for_program_if_not_removed",
            ),
            UniqueConstraint(
                fields=["business_area", "programme_code"],
                condition=Q(is_removed=False),
                name="unique_for_business_area_and_programme_code_if_not_removed",
            ),
            UniqueConstraint(
                fields=["business_area", "slug"],
                condition=Q(is_removed=False),
                name="unique_for_business_area_and_slug_if_not_removed",
            ),
        ]
        permissions = [("enroll_beneficiaries", "Can enroll beneficiaries")]
        verbose_name = "Programme"

    def __str__(self) -> str:
        return self.name

    def validate_unique(self, exclude: Collection[str] | None = ...) -> None:  # type: ignore
        query = Program.objects.filter(name=self.name, business_area=self.business_area, is_removed=False)
        if query.exists() and query.first() != self:
            raise ValidationError(
                f"Program for name: {self.name} and business_area: {self.business_area.slug} already exists."
            )
        super().validate_unique()

    def is_active(self) -> bool:
        return self.status == self.ACTIVE

    @property
    def can_finish(self) -> bool:
        from hope.models.program_cycle import ProgramCycle

        return not self.cycles.filter(status=ProgramCycle.ACTIVE).exists()
