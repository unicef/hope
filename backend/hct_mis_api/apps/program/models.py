from decimal import Decimal
from typing import Collection, Optional, Union

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

from hct_mis_api.apps.activity_log.utils import create_mapping_dict
from hct_mis_api.apps.core.querysets import ExtendedQuerySetSequence
from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.targeting.models import TargetPopulation
from hct_mis_api.apps.utils.models import (
    AbstractSyncable,
    ConcurrencyModel,
    TimeStampedUUIDModel,
    UnicefIdentifiedModel,
)
from hct_mis_api.apps.utils.validators import (
    DoubleSpaceValidator,
    StartEndSpaceValidator,
)


class Program(SoftDeletableModel, TimeStampedUUIDModel, AbstractSyncable, ConcurrencyModel):
    ACTIVITY_LOG_MAPPING = create_mapping_dict(
        [
            "name",
            "status",
            "start_date",
            "end_date",
            "description",
            "ca_id",
            "ca_hash_id",
            "business_area",
            "budget",
            "frequency_of_payments",
            "sector",
            "scope",
            "cash_plus",
            "population_goal",
            "administrative_areas_of_implementation",
            "individual_data_needed",
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
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICE, db_index=True)
    start_date = models.DateField(db_index=True)
    end_date = models.DateField(db_index=True)
    description = models.CharField(
        blank=True,
        max_length=255,
        validators=[MinLengthValidator(3), MaxLengthValidator(255)],
    )
    ca_id = CICharField(max_length=255, null=True, blank=True, db_index=True)
    ca_hash_id = CICharField(max_length=255, null=True, blank=True, db_index=True)
    admin_areas = models.ManyToManyField("geo.Area", related_name="programs", blank=True)
    business_area = models.ForeignKey("core.BusinessArea", on_delete=models.CASCADE)
    budget = models.DecimalField(
        decimal_places=2,
        max_digits=11,
        validators=[MinValueValidator(Decimal("0.00"))],
        db_index=True,
    )
    frequency_of_payments = models.CharField(
        max_length=50,
        choices=FREQUENCY_OF_PAYMENTS_CHOICE,
    )
    sector = models.CharField(max_length=50, choices=SECTOR_CHOICE, db_index=True)
    scope = models.CharField(
        max_length=50,
        choices=SCOPE_CHOICE,
    )
    cash_plus = models.BooleanField()
    population_goal = models.PositiveIntegerField()
    administrative_areas_of_implementation = models.CharField(
        max_length=255,
        blank=True,
        validators=[MinLengthValidator(3), MaxLengthValidator(255)],
    )
    individual_data_needed = models.BooleanField(
        default=False,
        help_text="""
        This boolean decides whether the target population sync will send
        all individuals of a household that's part of the population or only
        the relevant ones (collectors etc.)""",
    )
    data_collecting_type = models.ForeignKey(
        "core.DataCollectingType", related_name="programs", on_delete=models.PROTECT, null=True, blank=True
    )

    @staticmethod
    def get_total_number_of_households_from_payments(qs: Union[models.QuerySet, ExtendedQuerySetSequence]) -> int:
        return (
            qs.filter(**{"payment_items__delivered_quantity__gt": 0})
            .distinct("payment_items__household__unicef_id")
            .values_list("payment_items__household__unicef_id", flat=True)
            .order_by("payment_items__household__unicef_id")
            .count()
        )

    @property
    def total_number_of_households(self) -> int:
        return self.household_set.count()

    @property
    def households_with_tp_in_program(self) -> QuerySet:
        target_populations_in_program = TargetPopulation.objects.filter(program=self).exclude(
            status=TargetPopulation.STATUS_OPEN
        )
        return Household.objects.filter(target_populations__in=target_populations_in_program).distinct()

    @property
    def admin_areas_log(self) -> str:
        return ", ".join(self.admin_areas.all())

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["name", "business_area", "is_removed"],
                condition=Q(is_removed=False),
                name="unique_for_program_if_not_removed",
            )
        ]
        verbose_name = "Programme"

    def __str__(self) -> str:
        return self.name

    def validate_unique(self, exclude: Optional[Collection[str]] = ...) -> None:  # type: ignore
        query = Program.objects.filter(name=self.name, business_area=self.business_area, is_removed=False)
        if query.exists() and query.first() != self:
            raise ValidationError(
                f"Program for name: {self.name} and business_area: {self.business_area.slug} already exists."
            )
        super(Program, self).validate_unique()


class ProgramCycle(SoftDeletableModel, TimeStampedUUIDModel, AbstractSyncable, ConcurrencyModel, UnicefIdentifiedModel):
    ACTIVITY_LOG_MAPPING = create_mapping_dict(
        [
            "status",
            "start_date",
            "end_date",
            "description",
        ],
    )
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    FINISHED = "FINISHED"
    STATUS_CHOICE = (
        (DRAFT, _("Draft")),
        (ACTIVE, _("Active")),
        (FINISHED, _("Finished")),
    )
    name = CICharField(
        max_length=255,
        validators=[
            MinLengthValidator(3),
            MaxLengthValidator(255),
            DoubleSpaceValidator,
            StartEndSpaceValidator,
            ProhibitNullCharactersValidator(),
        ],
        default="Default Program Cycle",
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICE, db_index=True)
    start_date = models.DateField()  # first from program
    end_date = models.DateField(null=True, blank=True)
    program = models.ForeignKey("Program", on_delete=models.CASCADE, related_name="cycles")

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["name", "program", "is_removed"],
                condition=Q(is_removed=False),
                name="program_cycle_name_unique_if_not_removed",
            ),
        ]
        ordering = ["start_date"]
        verbose_name = "ProgrammeCycle"

    def __str__(self) -> str:
        return f"{self.program.name} - cycle start date {self.start_date}"

    @property
    def total_entitled_quantity_usd(self) -> Decimal:
        result = Decimal(0.0)
        for payment_plan in self.payment_plans.all():
            if payment_plan.total_entitled_quantity_usd:
                result += payment_plan.total_entitled_quantity_usd
        return result

    @property
    def total_undelivered_quantity_usd(self) -> Decimal:
        result = Decimal(0.0)
        for payment_plan in self.payment_plans.all():
            if payment_plan.total_undelivered_quantity_usd:
                result += payment_plan.total_undelivered_quantity_usd
        return result

    @property
    def total_delivered_quantity_usd(self) -> Decimal:
        result = Decimal(0.0)
        for payment_plan in self.payment_plans.all():
            if payment_plan.total_delivered_quantity_usd:
                result += payment_plan.total_delivered_quantity_usd
        return result

    def validate_program_active_status(self) -> None:
        # all changes with Program Cycle are possible within Active Program
        if self.program.status != Program.ACTIVE:
            raise ValidationError("Program should be within Active status.")

    def set_active(self) -> None:
        self.validate_program_active_status()
        if self.status in (ProgramCycle.DRAFT, ProgramCycle.FINISHED):
            self.status = ProgramCycle.ACTIVE
            self.save()

    def set_draft(self) -> None:
        self.validate_program_active_status()
        if self.status == ProgramCycle.ACTIVE:
            self.status = ProgramCycle.DRAFT
            self.save()

    def set_finish(self) -> None:
        self.validate_program_active_status()
        self.status = ProgramCycle.FINISHED
        self.save()
