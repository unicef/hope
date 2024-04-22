import random
import string
from decimal import Decimal
from typing import Any, Collection, Optional, Union

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
from hct_mis_api.apps.core.models import DataCollectingType
from hct_mis_api.apps.core.querysets import ExtendedQuerySetSequence
from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.targeting.models import TargetPopulation
from hct_mis_api.apps.utils.models import (
    AbstractSyncable,
    AdminUrlMixin,
    ConcurrencyModel,
    SoftDeletableIsVisibleManager,
    TimeStampedUUIDModel,
)
from hct_mis_api.apps.utils.validators import (
    DoubleSpaceValidator,
    StartEndSpaceValidator,
)


class ProgramPartnerThrough(TimeStampedUUIDModel):
    program = models.ForeignKey(
        "Program",
        on_delete=models.CASCADE,
        related_name="program_partner_through",
    )
    partner = models.ForeignKey(
        "account.Partner",
        on_delete=models.CASCADE,
        related_name="program_partner_through",
    )
    areas = models.ManyToManyField("geo.Area", related_name="program_partner_through", blank=True)
    full_area_access = models.BooleanField(default=False)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["program", "partner"],
                name="unique_program_partner",
            )
        ]


class Program(SoftDeletableModel, TimeStampedUUIDModel, AbstractSyncable, ConcurrencyModel, AdminUrlMixin):
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
        blank=True,
        null=True,
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
    data_collecting_type = models.ForeignKey(
        "core.DataCollectingType", related_name="programs", on_delete=models.PROTECT, null=True, blank=True
    )
    is_visible = models.BooleanField(default=True)
    household_count = models.PositiveIntegerField(default=0)
    individual_count = models.PositiveIntegerField(default=0)
    programme_code = models.CharField(max_length=4, null=True, blank=True)

    partner_access = models.CharField(
        null=True,
        blank=True,
        max_length=50,
        choices=PARTNER_ACCESS_CHOICE,
        default=SELECTED_PARTNERS_ACCESS,
    )
    partners = models.ManyToManyField(to="account.Partner", through=ProgramPartnerThrough, related_name="programs")

    objects = SoftDeletableIsVisibleManager()

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self.programme_code:
            self.programme_code = self._generate_programme_code()
        if self.data_collecting_type_id is None and self.data_collecting_type:
            # save the related object before saving Program
            self.data_collecting_type.save()
        super().save(*args, **kwargs)

    def _generate_programme_code(self) -> str:
        programme_code = "".join(random.choice(string.ascii_uppercase + string.digits + "-/.") for _ in range(4))
        if Program.objects.filter(business_area_id=self.business_area_id, programme_code=programme_code).exists():
            return self._generate_programme_code()
        return programme_code

    @staticmethod
    def get_total_number_of_households_from_payments(qs: Union[models.QuerySet, ExtendedQuerySetSequence]) -> int:
        return (
            qs.filter(**{"payment_items__delivered_quantity__gt": 0})
            .distinct("payment_items__household__unicef_id")
            .values_list("payment_items__household__unicef_id", flat=True)
            .order_by("payment_items__household__unicef_id")
            .count()
        )

    def adjust_program_size(self) -> None:
        self.household_count = self.household_set.count()
        self.individual_count = self.individuals.count()

    @property
    def households_with_tp_in_program(self) -> QuerySet:
        target_populations_in_program = TargetPopulation.objects.filter(program=self).exclude(
            status=TargetPopulation.STATUS_OPEN
        )
        return Household.objects.filter(target_populations__in=target_populations_in_program).distinct()

    @property
    def admin_areas_log(self) -> str:
        return ", ".join(self.admin_areas.all())

    @property
    def is_social_worker_program(self) -> bool:
        if self.data_collecting_type is None:
            return False
        return self.data_collecting_type.type == DataCollectingType.Type.SOCIAL

    class Meta:
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
        ]
        permissions = [("enroll_beneficiaries", "Can enroll beneficiaries")]
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


class ProgramCycle(SoftDeletableModel, TimeStampedUUIDModel, AbstractSyncable, ConcurrencyModel):
    ACTIVITY_LOG_MAPPING = create_mapping_dict(
        [
            "iteration",
            "status",
            "start_date",
            "end_date",
            "description",
        ],
    )
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"
    STATUS_CHOICE = (
        (ACTIVE, _("Active")),
        (CLOSED, _("Closed")),
    )

    iteration = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1),
        ],
        db_index=True,
        default=1,
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICE, db_index=True)
    start_date = models.DateField()  # first from program
    end_date = models.DateField(null=True, blank=True)
    description = models.CharField(
        blank=True,
        max_length=255,
        validators=[MinLengthValidator(3), MaxLengthValidator(255)],
    )
    program = models.ForeignKey("Program", on_delete=models.CASCADE, related_name="cycles")

    class Meta:
        unique_together = ("iteration", "program")
        ordering = ["program", "iteration"]
        verbose_name = "ProgrammeCycle"

    def __str__(self) -> str:
        return f"{self.program.name} - cycle {self.iteration}"
